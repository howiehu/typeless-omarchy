#!/usr/bin/python3
"""Read-only vendor qualification; never accept new hashes or build a runtime.

Before adapting a vendor build, read https://www.typeless.com/help/release-notes
and https://www.typeless.com/help/release-notes/linux, then follow
docs/releasing.md's vendor qualification procedure.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('runtime_prepare',root/'runtime/prepare.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
SUPPORTED = ('2.2.0','2.2.1')

def feed_version(text):
    matches=re.findall(r'^version:\s*[\'\"]?([0-9]+(?:\.[0-9]+){2})[\'\"]?\s*$',text,re.M)
    if len(matches)!=1:raise ValueError('Expected exactly one valid release version in vendor feed')
    return matches[0]

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feed',type=Path)
    parser.add_argument('--archive',type=Path)
    args=parser.parse_args()
    if not args.feed and not args.archive:parser.error('provide --feed or --archive')
    expected=None
    if args.feed:
        if args.feed.stat().st_size>131072:raise ValueError('Vendor feed exceeds size limit')
        expected=feed_version(args.feed.read_text())
        if expected not in SUPPORTED:raise ValueError('Unqualified vendor release '+expected+'; first read https://www.typeless.com/help/release-notes/linux and follow docs/releasing.md to review interfaces and publish a compatibility release')
        print('Qualified release version:',expected,'(version only; archive fingerprints require --archive)')
    if args.archive:
        archive=m.Archive(args.archive)
        version=json.loads(archive.read('package.json'))['version']
        if version not in SUPPORTED or expected and expected!=version:raise ValueError('Archive version is not qualified or does not match feed')
        changed=m.patch_sources(archive)
        print('PASS qualified archive:',version,';',len(changed),'patched modules checked in memory; no runtime written')

if __name__=='__main__':
    try:main()
    except (ValueError,KeyError,OSError) as error:
        print(str(error),file=sys.stderr);sys.exit(1)
