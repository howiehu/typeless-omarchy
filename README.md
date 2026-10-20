# Typeless-Omarchy

[![Build and test](https://github.com/howiehu/typeless-omarchy/actions/workflows/ci.yml/badge.svg)](https://github.com/howiehu/typeless-omarchy/actions/workflows/ci.yml)
[![Original contributions: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Independent compatibility tools for the official Typeless Linux app on Omarchy, Hyprland and Fcitx5. **Release 0.4.5, x86_64; tested with Typeless 2.2.0.** This project is not affiliated with or endorsed by Typeless or Omarchy.

[中文说明](README.zh-CN.md) · [Releases](https://github.com/howiehu/typeless-omarchy/releases) · [Technical report](docs/upstream-report.md) · [Validation](docs/validation.md)

## What it changes

| Area | Behavior |
| --- | --- |
| Dictation | A passive Fcitx module commits to the focused input context without switching the selected Chinese/keyboard engine. |
| Launch | Runs Typeless on native Wayland and scopes the helper query adapter to Typeless's own process. |
| Recording HUD | Removes compositor decorations from the transparent `Status` canvas and keeps it visible across workspaces without taking focus. |
| Answers | Keeps official `AI result` cards interactive and visible across workspaces. |
| Ask Anything recovery | The selected-text replace path opens the official answer card when no eligible Fcitx input context exists, instead of attempting a paste with no reliable target. |
| Scrolling | Defaults only Typeless to software rendering; this resolved the rectangular text flicker/displacement confirmed on the test desktop. |

The official dashboard, tray, login, onboarding and account profile remain in use. No extra tray icon or persistent service is installed. The compatibility package does not contain the proprietary app, account data or generated runtime copies.

## Tested environment

Omarchy 4.0.5, Hyprland 0.56.2, Fcitx5 5.1.23, official Typeless 2.2.0 (`typeless-bin 2.2.0-1`), x86_64. The user confirmed mixed Shuangpin/voice input, answer-card recovery and normal scrolling with the rendering workaround. Automated coverage and limits are in [validation](docs/validation.md).

Other application versions, desktops, architectures and GPUs have not been established as supported. In particular, the answer recovery patch accepts only the exact vendor code fingerprints recorded in `runtime/prepare.py`.

## Install on Omarchy

Install the official `typeless-bin` separately through Omarchy's AUR installer. Review that recipe and the vendor's download source as you normally would for an AUR application.

Install the build dependencies with your package manager: `base-devel`, `cmake`, `fcitx5`, `json-c`, `glib2`, `python`, `dbus`, `systemd`, `desktop-file-utils` and `git`. Then, as your regular desktop user:

```sh
git clone --branch v0.4.5 --depth 1 https://github.com/howiehu/typeless-omarchy.git
cd typeless-omarchy
python tools/stage-package.py /tmp/typeless-package
cd /tmp/typeless-package
makepkg -si
```

Read the generated PKGBUILD before building. `makepkg -si` builds as your user and asks for authorization to install the package. The generated recipe downloads no proprietary software.

Exit Typeless fully, then enable the desktop integration as your regular desktop user:

```sh
typeless-omarchy-setup
```

Setup installs a marked per-user `typeless.desktop` replacement, so the menu has one **Typeless** entry instead of separate official and compatibility entries. The same desktop ID also routes `typeless://` callbacks through the launcher. A fingerprint-guarded change exempts only this marked compatibility entry from the official cleanup; other registration behavior is retained. Setup adds one exact Lua include. Setup restarts Fcitx to discover the addon, restoring the previously selected engine. Run initial setup at a convenient time because that restart briefly interrupts input. No package install hook modifies user profiles.

Launch **Typeless** from the application menu. Setup repairs recognized existing vendor autostart commands, retaining the enabled/disabled state and original startup arguments. The guarded runtime patch keeps subsequent vendor autostart writes pointed at `/usr/bin/typeless-omarchy` instead of the generated cache executable. Autostart is not enabled if no entry exists; the official startup setting still controls it. Custom commands are left untouched.

After upgrading an existing setup, fully exit Typeless and run:

```sh
typeless-omarchy-setup --repair
```

Repair migrates older setup records without restarting Fcitx and removes the managed 0.4.4 independent duplicate. It preserves the original desktop backup and refuses to overwrite later menu edits. The vendor uses a single-instance lock, so an already-running instance must be closed for new runtime patches to take effect.

## How the compatibility layer works

The vendor expects a `typeless-voice` input endpoint, but the inspected Linux package did not include a Fcitx addon binary. This implementation uses its existing VoiceIME socket protocol and Fcitx `commitString`. It registers a passive module, not a selectable input method.

The launcher exposes a private `gdbus` adapter for one exact `CurrentInputMethod` query, only to its recorded parent process and while the bridge socket responds. The virtual endpoint is visible to the vendor helper; the actual selected engine stays unchanged. Unrelated calls execute the system `gdbus`. Global PATH and the Fcitx D-Bus service are not replaced.

Answer recovery needs a small application-side change. At launch, `runtime/prepare.py` verifies three vendor source hashes and builds a private runtime copy under `${XDG_CACHE_HOME:-~/.cache}/typeless-omarchy/runtime/`. It copies the executable, links unchanged resources, and rewrites three files in a private ASAR archive with updated integrity metadata. A private main-process status request checks the bridge before the Ask Anything replace handler inserts. No eligible context means showing the original answer card; a focused editable context preserves the vendor handler.

A separate startup-command transformation changes only the executable written to the vendor autostart entry when compatibility mode is active. The filename, flags and official enabled/disabled handling are preserved.

**Installed vendor files are never edited.** The generated runtime contains vendor material for local execution and is not a project release artifact. Unsupported fingerprints emit a warning and use the base input bridge without the answer-recovery and autostart-generation patches. This project does not read account/history databases to recover answers, replace the speech service, poll the clipboard or enable persistent debugging.

## Controls and rollback

Exit the existing Typeless instance before testing these commands:

```sh
# Use the base input compatibility layer without the private answer-recovery/autostart copy.
TYPELESS_OMARCHY_BASE_ONLY=1 typeless-omarchy

# Restore hardware rendering for comparison.
TYPELESS_OMARCHY_GPU=1 typeless-omarchy
```

Software rendering can use more CPU. These overrides are independent: base-only mode still uses the default scrolling workaround unless hardware rendering is also requested.

Before uninstalling, exit Typeless and run:

```sh
typeless-omarchy-setup --remove
sudo pacman -R typeless-omarchy
```

Removal restores the original per-user desktop entry (or removes our override so the system entry becomes active), removes the managed 0.4.4 duplicate if present, and deletes only the exact config include. It refuses to overwrite later menu edits. Recognized compatibility autostart commands are reverted while preserving later changes to the official startup toggle. User input-method group entries and Typeless account/history data are not removed. Generated runtime cache can be deleted after the app has exited; it lives in the project-specific cache directory described above.

## Limits

- This is a compatibility workaround for undocumented vendor internals, not official Typeless support. Vendor updates require revalidation.
- Answer recovery covers the Ask Anything **replace** path with no eligible input context. It does not guarantee delivery after a later focus change and does not generally repair selected-text/rich-text editing. Reply, external-action, ordinary dictation and voice-translation routing are preserved.
- The bridge refuses password/sensitive contexts. The vendor's independent clipboard fallbacks are outside its control.
- The earlier application disappearance had no confirmed root cause. Successful tests do not establish crash freedom.
- Automated tests use synthetic text. Long-term use and first-login flows across multiple desktop configurations still need broader testing.

## Build and contribute

```sh
cmake -S . -B build-ci -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Release
cmake --build build-ci
ctest --test-dir build-ci --output-on-failure
```

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) and [CHANGELOG.md](CHANGELOG.md). GUI acceptance tools require the installed vendor app and a desktop session; CI does not claim to prove those GUI behaviors.

The Omarchy packaging contribution is [omacom/omarchy-pkgs#1294](https://github.com/omacom/omarchy-pkgs/pull/1294). Its review/build status is independent of this project's releases. The community package is not yet evidence of acceptance into an official distribution repository.

## Copyright, license and third-party rights

Copyright (c) 2026 Hao Hu and contributors. The MIT license in [LICENSE](LICENSE) applies to this project's original contributions only, to the extent contributors hold rights they can license. It does not relicense Typeless, third-party material or generated runtime copies.

[NOTICE](NOTICE) is the shared English/Chinese statement covering third-party rights, vendor-derived matching fragments, names and non-affiliation. It is installed beside LICENSE in the compatibility package. Dependencies and software supplied by their own installers retain their upstream terms and notices.

The private-runtime patch uses vendor-specific identifiers and small matching fragments; no ownership or MIT relicensing of third-party material is claimed. Installed vendor files are unchanged, but the generated runtime contains modified vendor material. Local generation, source fingerprint checks and non-distribution do not establish vendor authorization or legal compliance. Typeless's [Terms of Service](https://www.typeless.com/terms), including sections 3 and 7, contain restrictions relevant to reverse engineering and modification. No applicable exception, permission or legal-clearance determination is represented here.

This project is not affiliated with or endorsed by Typeless or Omarchy. Their names identify compatibility targets; no trademark rights or official support are granted by this project. These notices clarify scope and do not replace a legal review.
