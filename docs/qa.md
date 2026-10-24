# Reusable QA and release acceptance

This is the current checklist. [validation.md](validation.md) preserves historical evidence; it is not an instruction to repeat every past experiment. Use a clean source checkout, a candidate built from that source, the exact qualified vendor build and an idle test desktop. Do not infer a pass on a new version from old user feedback.

## 1. Automated source and package gate

```sh
python tools/qa.py --suite headless --build-dir /tmp/typeless-qa-build --report /tmp/typeless-headless.json
python tools/stage-package.py /tmp/typeless-qa-package
cd /tmp/typeless-qa-package
makepkg --noconfirm --cleanbuild
```

Use new report/staging directories for independent runs. The runner returns nonzero for failure or blocked prerequisites and refuses to overwrite reports. Run without root. CI runs the same headless entry point followed by the staged package build. At publication, also build the exact release archive/PKGBUILD and verify downloaded asset hashes as described in [releasing.md](releasing.md).

| Coverage | Existing executable test | What it proves |
| --- | --- | --- |
| Native GIO query scope | `native-query` | Exact-call/PID/bridge gating and unrelated-call fallback |
| Vendor update detection | `vendor-feed` | Strict metadata parsing; not behavioral compatibility |
| Vendor profiles and archive | `build221-profile`, `runtime-archive` | Hash/anchor refusal, private archive integrity and known transformations |
| Menu/protocol/autostart | `desktop-integration` | Isolated migration/repair/rollback, entry ownership and user-edit preservation |
| Focus and pointer policy | `status-focus`, `hud-pointer` | Actual Lua/JS callback behavior, rectangles and focus guards |
| Package update policy | `update-policy` | Managed IPC behavior and blocked download/install routes |
| Passive input protocol | `protocol` | Isolated D-Bus/Fcitx protocol and input guards |
| QA reporting | `qa-report` | Fail/blocked status is retained, manual cases are not auto-approved, captured output is excluded and reports are not overwritten |
| Omarchy source scanning | `config-scan` | Callable-table mock loading completes within a bounded deadline, without compositor runtime operations; existing focus tests separately exercise the real-function branch |

These tests do not require an account or vendor binaries and do not restart the real desktop Fcitx. Preserve failure regressions instead of asserting only the current implementation's shape.

## 2. Installed build and real desktop gate

Install the candidate explicitly; the runner never installs or restarts applications. Fully stop dictation normally before changing the running build. Run only after the setup/repair needed for that candidate. Ensure no other test is manipulating focus, no input composition is pending, and no recording is active.

```sh
# Read-only: vendor fingerprints/file integrity, package versions, config, Wayland.
python tools/qa.py --suite desktop --report /tmp/typeless-desktop.json

# Active probes: opens isolated GTK/Foot receivers, changes focus/workspace.
# Uses the installed query adapter and current selected input method.
python tools/qa.py --suite input --report /tmp/typeless-input.json

# Active probe: briefly moves the pointer and clicks ONLY its own GTK button.
# Do not move the mouse during this test; requires ydotool/ydotoold + uinput access.
python tools/qa.py --suite pointer --report /tmp/typeless-pointer.json
```

The input suite checks exact synthetic delivery, the voice-ime backend, unchanged method before/during/after, cross-workspace Foot and password/no-focus refusal. It does not select Shuangpin for you. To qualify both Shuangpin and English, select each manually, rerun with separate reports, then restore your usual method. GTK probes need Python GObject/GTK and the Fcitx GTK module; Foot is required for the terminal probe. A desktop suite needs Hyprland, pacman and the installed vendor archive; active probes additionally require pactl and the idle compatibility HUD. Missing prerequisites are blocked, not passed. `tests/hud-focus.py` remains a separate optional active-HUD regression; do not trigger recording merely to run the idle suite.

The pointer probe proves click-through beneath an idle canvas, not clicks on actual recording controls or all points around an active popup. Live insertion uses the vendor native library with synthetic text, not speech recognition/provider requests. Original workspace/focus are restored by the existing probes; the pointer probe also restores cursor position. Keep a test desktop idle until cleanup finishes. Do not force-kill the probes or Typeless during recording.

Reports contain source commit/dirty state, selected suite/check IDs, exit status, duration, manual cases marked `not_run`, and package versions where available. Raw subprocess output, dictated text, account details, window titles and audio stream metadata are not saved in reports. Failed headless build/test output is printed for CI diagnostics; desktop subprocess output is suppressed and can be investigated by rerunning the underlying probe locally. Reports are created mode 0600; review them before publishing. A source report does not prove that the installed candidate matches that commit: record the package archive hash and source commit in the acceptance record below.

## 3. Manual end-to-end gate

Use synthetic, non-private phrases. Record each result as `pass`, `fail`, `blocked`, `not_run` or `not_applicable` with a reason. Do not mark missing tests passed. Full release acceptance needs all applicable required cases; an intentionally narrower release must state exactly which cases remain unverified and why. Automated reports always say `pending_manual` and never certify this gate automatically.

| ID | Action | Required observation |
| --- | --- | --- |
| M01 | Type Chinese with Shuangpin, dictate in a browser field, type Chinese again; repeat in English and Foot/on another workspace. | Correct text in the original receiver, no forced method change or stray insertion. |
| M02 | Record a short phrase, mouse-confirm; repeat and mouse-cancel. | Buttons clickable, confirm delivers only to the original field, cancel inserts nothing, focus/cursor stable. |
| M03 | Click normal web buttons with idle HUD; while controls are visible, click transparent areas outside them. | Underlying controls work, no invisible interception or cursor jump; visible controls still work. |
| M04 | Invoke Ask Anything/translation without an editable target; test the selected-text/editable route too. Scroll a long result, copy and close it. | Correct official card/routing, interactive actions, no rectangular displacement/flicker. |
| M05 | Cold-launch from menu; check protocol association and official startup toggle/autostart route. Open Super+K and generate the keybinding list without using a previous cache. | One visible Typeless entry, compatibility launcher used, startup flags and enabled state preserved; shortcut scanning/menu completes without a stuck Lua process. Test a full login if claimed; simulated autostart is weaker evidence. |
| M06 | On a separate clean test profile, complete first login/onboarding and protocol callback. | No blocked/hidden required windows; main window and official tray behave normally. Existing account success does not qualify first login. |
| M07 | Leave app idle, then use About's manual update check. | No recurring updater popup; package-policy explanation; no vendor Debian download/install. Do not attempt installation on the host. |
| M08 | Play browser audio, note per-stream mute state; with official background-mute enabled, dictate then stop normally; repeat with cancel, then with setting disabled. | Enabled setting restores each stream's original mute state after both normal paths; disabled setting leaves audio alone. Preserve intentionally muted streams and original settings. Observe once more after normal app exit. |
| M09 | On a disposable profile, perform setup, repeat repair, make a subsequent menu edit, then remove integration. | Idempotent repair, user edits retained/refused as documented, managed changes reversible, official files intact. |

For M08 use `pactl -f json list sink-inputs` locally before/during/after to compare the actual browser streams (IDs can change). Do not publish raw audio/application metadata. A stream being unmuted while idle does not prove restoration. Abnormal-exit/mute recovery is a separate optional investigation on a disposable session, never a forced crash on the working desktop. This project does not claim that incident fixed.

Record full-screen and each additional monitor arrangement separately if supported scope expands; the usual desktop does not establish those cases. First-account and rollback cases can be blocked when no disposable profile exists, but the release must retain that limitation.

## Acceptance record template

Copy this into a version-specific audit or release PR, not into an unchanged old release asset:

```text
Date / tester:
Source commit / clean or dirty:
Compatibility package version / archive SHA-256:
Official vendor version / exact archive fingerprint check:
Omarchy / Hyprland / Fcitx / architecture:
Input methods / monitor arrangement / rendering mode:
Official release notes reviewed (links, date, relevant changes or unavailable):
Headless report / CI URL / exact package build result:
Desktop / input / pointer reports (each method tested):
M01..M09: status + concise synthetic observation or reason not run
Known failures / scope limitations:
Acceptance: complete / partial / blocked (reason)
```

Keep public summaries separate from local raw logs. No automatic suite or manual feedback silently changes fingerprints, qualifies a different vendor build or publishes a release. Follow [the qualification procedure](releasing.md#qualify-an-official-typeless-update-first) for each vendor update.
