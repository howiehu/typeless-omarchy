#!/usr/bin/python3
"""Run reusable QA suites; save structured results without captured app output.

Desktop/input/pointer suites require a configured idle Omarchy desktop. They do
not install, restart, record speech, access account data or publish anything.
See docs/qa.md for prerequisites and the separate manual release gate.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
MANUAL = ('M01-mixed-input', 'M02-confirm-cancel', 'M03-hud-pointer',
          'M04-result-card', 'M05-menu-autostart', 'M06-login-onboarding',
          'M07-update-policy', 'M08-audio-restore', 'M09-rollback')


def capture(command):
    return subprocess.run(command, cwd=ROOT, capture_output=True, text=True,
                          errors='replace', check=False)


def clean_config_response(text):
    errors = json.loads(text)
    # Hyprland can represent no config errors as [] or [""].
    return isinstance(errors, list) and all(isinstance(x, str) and not x.strip() for x in errors)


class Report:
    def __init__(self, suites):
        self.results = []
        self.data = {'schema': 1, 'started_utc': datetime.now(timezone.utc).isoformat(),
                     'suites': suites, 'checks': self.results,
                     'manual': {key: 'not_run' for key in MANUAL}}
        try:
            commit = capture(['git', 'rev-parse', 'HEAD'])
            state = capture(['git', 'status', '--porcelain'])
            self.data['source_commit'] = commit.stdout.strip() if commit.returncode == 0 else None
            self.data['source_dirty'] = bool(state.stdout.strip()) if state.returncode == 0 else None
        except OSError:
            self.data['source_commit'] = None
            self.data['source_dirty'] = None

    def add(self, key, status, detail='', duration=0):
        self.results.append({'id': key, 'status': status, 'detail': detail,
                             'seconds': round(duration, 3)})
        print(status.upper() + ' ' + key + (': ' + detail if detail else ''), flush=True)
        return status == 'pass'

    def run(self, key, command, env=None, show_failure=False):
        started = time.monotonic()
        try:
            # Do not save raw output: native/app diagnostics can contain private data.
            result = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, check=False)
            if result.returncode and show_failure:
                # Only headless source/build tests opt in. Desktop output stays private.
                print(result.stdout.decode(errors='replace'), file=sys.stderr)
            return self.add(key, 'pass' if result.returncode == 0 else 'fail',
                            'exit=' + str(result.returncode), time.monotonic() - started)
        except OSError:
            return self.add(key, 'blocked', 'command unavailable or could not start')

    def save(self, target):
        statuses = {x['status'] for x in self.results}
        status = 'fail' if 'fail' in statuses else 'blocked' if 'blocked' in statuses else 'pass'
        self.data.update(automated_status=status, release_acceptance='pending_manual',
                         finished_utc=datetime.now(timezone.utc).isoformat())
        target.parent.mkdir(parents=True, exist_ok=True)
        # Refuse overwriting a report, including symlinks; retain previous evidence.
        with target.open('x', encoding='utf-8') as stream:
            os.chmod(target, 0o600)
            json.dump(self.data, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        return 0 if status == 'pass' else 1


def headless(report, build):
    steps = [('shell-syntax', ['bash', '-n', 'bin/typeless-omarchy']),
             ('configure', ['cmake', '-S', str(ROOT), '-B', str(build),
                            '-DCMAKE_INSTALL_PREFIX=/usr', '-DCMAKE_BUILD_TYPE=Release',
                            '-DBUILD_TESTING=ON']),
             ('build', ['cmake', '--build', str(build), '--parallel', '2']),
             ('ctest', ['ctest', '--test-dir', str(build), '--output-on-failure', '--no-tests=error'])]
    for key, command in steps:
        if not report.run(key, command, show_failure=True):
            break  # Dependent steps cannot be treated as passing.


def desktop(report):
    report.run('vendor-fingerprints', [sys.executable, 'tools/check-vendor.py',
                                      '--archive', '/opt/Typeless/resources/app.asar'])
    report.run('vendor-files', ['pacman', '-Qkk', 'typeless-bin'])
    try:
        versions = capture(['pacman', '-Q', 'typeless-bin', 'typeless-omarchy',
                            'hyprland', 'fcitx5', 'omarchy'])
        report.data['packages'] = versions.stdout.strip().splitlines()
        report.add('package-versions', 'pass' if versions.returncode == 0 else 'blocked')
        errors = capture(['hyprctl', 'configerrors', '-j'])
        clean = errors.returncode == 0 and clean_config_response(errors.stdout)
        report.add('compositor-config', 'pass' if clean else 'fail')
        clients = json.loads(capture(['hyprctl', 'clients', '-j']).stdout)
        windows = [x for x in clients if x.get('class') == 'Typeless']
        report.add('native-wayland', 'blocked' if not windows else
                   'pass' if all(x.get('xwayland') is False for x in windows) else 'fail',
                   'no Typeless windows' if not windows else 'Typeless windows only; titles not collected')
    except (OSError, ValueError, KeyError):
        report.add('desktop-session', 'blocked', 'desktop queries unavailable or malformed')


def idle(report, key):
    try:
        active = capture(['pactl', '-f', 'json', 'list', 'source-outputs'])
        if active.returncode or not isinstance(streams := json.loads(active.stdout), list):
            return report.add(key, 'blocked', 'cannot check recording state')
        if streams:
            return report.add(key, 'blocked', 'recording/capture stream present; finish it normally first')
        clients = json.loads(capture(['hyprctl', 'clients', '-j']).stdout)
        if not any(x.get('class') == 'Typeless' and x.get('title') == 'Status (idle)' for x in clients):
            return report.add(key, 'blocked', 'running compatibility idle HUD required')
        return report.add(key, 'pass')
    except (OSError, ValueError):
        return report.add(key, 'blocked', 'cannot verify an idle desktop')


def inputs(report):
    library = Path('/usr/lib/typeless-omarchy/libtypeless-query.so')
    if not library.is_file():
        report.add('installed-query-adapter', 'blocked', 'install the candidate compatibility package first')
        return
    env = dict(os.environ, TYPELESS_TEST_QUERY_LIBRARY=str(library))
    cases = [('input-gtk', ['--require-ime', '--preserve-im']),
             ('input-foot-workspace', ['--terminal', '--other-workspace', '--require-ime', '--preserve-im']),
             ('guard-password', ['--guard-password']), ('guard-no-focus', ['--guard-no-focus'])]
    for key, flags in cases:
        if not idle(report, key + '-preflight'):
            break
        if not report.run(key, [sys.executable, 'tests/live-input.py', *flags], env):
            break


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suite', choices=('headless', 'desktop', 'input', 'pointer'),
                        action='append', required=True)
    parser.add_argument('--build-dir', type=Path, default=ROOT / 'build-qa')
    parser.add_argument('--report', type=Path, required=True, help='new JSON file; never overwrite old evidence')
    args = parser.parse_args()
    if args.report.exists() or args.report.is_symlink():
        parser.error('report already exists; use a new path')
    report = Report(args.suite)
    for suite in dict.fromkeys(args.suite):
        if suite == 'headless':
            headless(report, args.build_dir.resolve())
        elif suite == 'desktop':
            desktop(report)
        elif suite == 'input':
            inputs(report)
        elif idle(report, 'pointer-preflight'):
            report.run('idle-hud-pointer', [sys.executable, 'tests/pointer-click.py'])
    return report.save(args.report)


if __name__ == '__main__':
    sys.exit(main())
