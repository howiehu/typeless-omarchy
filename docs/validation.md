# Validation and deployment

This is a chronological record of development evidence. The release scope and current behavior are summarized in the README and `docs/upstream-report.md`. Historical prototype paths below are rollback references, not current installation instructions.

The minimal reproduction is `python tests/live-input.py --terminal`. It opens an isolated Foot process running `read`, calls the same native `insertText` symbol as Typeless with synthetic text, and compares the captured result. It never types into an existing user shell. The test restores the original workspace and focus. On this machine Hyprland uses Lua dispatch, so the harness uses `hl.dsp.focus`.

Require the bridge, rather than accepting a vendor clipboard fallback:

```bash
python tests/live-input.py --require-ime
python tests/live-input.py --terminal --require-ime
python tests/live-input.py --terminal --require-ime --other-workspace
python tests/live-input.py --guard-password
python tests/live-input.py --guard-no-focus
```

The initial development prototype used these user-owned files:

- `~/.local/lib/fcitx5/typeless-omarchy-voice.so`
- `~/.local/share/fcitx5/addon/typeless-voice.conf`
- `~/.local/state/typeless-omarchy/install.json`
- `~/.local/bin/typeless-omarchy`
- `~/.config/hypr/typeless-compat.lua`
- An added `require("hypr.typeless-compat")` line and its preceding prototype comment in `~/.config/hypr/hyprland.lua`
- `~/.local/share/applications/typeless.desktop`, with its prior version saved as `typeless.desktop.bak.compat`

To undo the development plugin, run `python tools/install-user.py --remove`. Remove the exact prototype comment and require line from Hyprland's user config, then delete `~/.config/hypr/typeless-compat.lua`. Restore `typeless.desktop.bak.compat` to `typeless.desktop` and remove the user launcher. Run `hyprctl reload` and check `hyprctl configerrors`. The earlier pre-prototype config is also saved as `hyprland.lua.bak.typeless-*`; do not blindly restore it over later user changes.

Do not publish raw vendor logs or desktop screenshots: they may contain the user's dictated text or account information. The contribution report uses only synthetic test results and backend status tokens.

The initial packaged migration used the pacman-managed `typeless-omarchy 0.2.0-1` package. Its explicit desktop setup was disabled and enabled again successfully, followed by another passing GTK and cross-workspace Foot test. The package owns the Fcitx plugin, launcher, setup utility and optional Lua rule; user setup state is stored in `~/.local/state/typeless-omarchy/package.json`. The development plugin and its Lua include have been removed.

The first prototype registered a selectable `typeless-voice` input method. A new regression detected that Typeless warmup changed the actual method before restoring it. Version 0.2 replaces that engine with a passive module and a narrowly scoped per-process query adapter. The additional acceptance command is `python tests/live-input.py --terminal --require-ime --preserve-im --shuangpin`; it requires both exact text delivery and identical real input-method names before, during and after native warmup/commit.

Final 0.2 verification passed GTK and cross-workspace Foot tests with `--preserve-im --shuangpin`, plus `--interleave` for actual manual Chinese before/after the voice commit. The user confirmed real mixed Shuangpin/voice use and an English-mode switch while retaining the selected method. System `fcitx5-remote -n` reported `shuangpin` while Typeless was running; its private query saw the virtual endpoint and performed no real engine capture or switch.

The `Status` recording canvas persists after an application restart and is transparent while idle. With no workaround Hyprland draws a visible empty frame. The final rule removes decorations, blur and focus only for class `Typeless`, title `Status`; verified border_size=0 and no_focus=true plus local visual inspection (the historical no_focus rule is superseded by 0.4.6 below). Only the recording canvas is pinned across workspaces. No dashboard rule, extra tray icon or visibility service is installed.

Version 0.4 result validation:

- A synthetic replay of the installed vendor completion handler fails before the patch: absent input context and an insertion-classified app produce one insertion and zero cards. After the patch, absent context (including a stale editable accessibility hint) produces zero insertions and one official card; a genuinely focused editable case preserves the vendor route.
- Run `node tests/result-routing.cjs <extracted-CLnu4epW.mjs>` against the original and privately patched archive entries to reproduce the before/after. The proprietary handler is read from the locally installed app, not included in the package.
- `python tests/runtime.py` checks archive offset/integrity repair, unchanged vendor bytes/resources, cache reuse and refusal of unsupported code hashes.
- A temporary loopback Electron diagnostic session ran the patched vendor completion handler with synthetic text, the real Fcitx status IPC and the real vendor card entry point on an empty workspace. The `AI result` window mapped, accepted focus and followed workspace changes. The recording HUD remained non-focusable. No speech/provider call was made for this test. Debug flags are not part of the normal launcher.
- The native constructors share a translated title key, but the renderer sets the actual interactive card title to `AI result`. The previous title-collision explanation did not establish the cause of the missing answer. Actual window observation and completion routing provide the evidence above.

Version 0.4.1 scrolling validation: the user reported rectangular text displacement and flicker when scrolling the answer card. A 100-paragraph synthetic card used the official result UI on the same desktop, then the same app was restarted with `--disable-gpu` as the changed rendering option. The user confirmed the artifacts disappeared and scrolling was normal. Software rendering is scoped to Typeless, with `TYPELESS_OMARCHY_GPU=1` as an escape hatch. This A/B result supports the workaround, not a diagnosis of a particular GPU driver defect.

Release 0.4.2 preparation: an independent `/tmp` CMake build with no reliance on the old in-tree build passed both CTests. The protocol harness now receives the actual CMake target directory, preventing accidental use of a stale addon. Desktop runtime behavior is unchanged from the user-accepted 0.4.1 package.


Release 0.4.4 menu/autostart validation (2026-10-20):

- Reproduced the official same-name desktop cleanup: after startup, `applications/typeless.desktop` disappeared. The official autostart command also pointed directly into the generated runtime cache. The login-time service log showed `X_ChangeProperty / BadWindow` with that direct launch route.
- Three CTests pass from an independent build: runtime archive/guards, isolated desktop integration and the private D-Bus/Fcitx protocol. The desktop suite has ten cases covering legacy migration with missing/present entries, repeated repair, matching manual-entry adoption, enabled/disabled/absent autostart, rollback and preservation/refusal of subsequent user edits.
- A local synthetic replay evaluated only the actual vendor string decoder and autostart command builder, not application startup or account data. The original builder emitted the supplied cache executable; the guarded replacement emitted the compatibility launcher with byte-identical original arguments. Without compatibility mode it emitted the original command unchanged. Extracted proprietary code remains local and is not in the repository or release assets.
- The staged Arch package built and installed as `typeless-omarchy 0.4.4-1`, upgrading the user's 0.4.1 package. `--repair` migrated the real v1 setup without restarting Fcitx.
- A real menu cold start mapped the native Wayland dashboard and Status windows. The independent menu entry survived official registration, and the generated autostart entry retained the launcher plus the original silent-start/password-store flags and enabled state.
- Stopped that instance and simulated login startup by executing the exact generated autostart command through the user service manager. It remained active with no startup failure. The menu then reopened the background instance's dashboard; both menu and autostart paths remained correct. A full logout/reboot was not performed.
- `pacman -Qkk typeless-bin` reported 361 files and zero altered files; `hyprctl configerrors` was empty. No new speech request was needed for launch acceptance, and this release does not claim to fix the separately observed audio mute incident.

Release 0.4.5 single-entry validation (2026-10-20):

- Before the change, Gio enumerated both `typeless.desktop` (official direct executable) and `typeless-omarchy.desktop` (compatibility launcher) as visible. This reproduces the user's duplicate-choice concern.
- After migrating the installed package with `--repair`, Gio enumerated exactly one visible entry: `typeless.desktop`, displayed as Typeless and executing `/usr/bin/typeless-omarchy %U`. The managed 0.4.4 duplicate was removed and the original pre-integration backup retained.
- A local replay of the exact guarded cleanup branch showed the original deletes the marked replacement. The patched branch retains only the matching marker plus exact launcher command in compatibility mode; unmarked/other-command entries and non-compatibility behavior are unchanged. The patched main and startup modules passed JavaScript syntax checks. No complete extracted vendor module is distributed.
- Cold startup using `gtk-launch typeless.desktop` mapped the dashboard, retained the marked replacement and generated the correct autostart command. Executing that exact autostart command and then reopening from the same menu ID passed again; Gio still reported one visible entry.
- `gio mime` reported `typeless.desktop` as the only registered/recommended/default protocol handler. Gio resolved its command to the compatibility launcher. No authentication token was used and a fresh login/account setup was not exercised.
- The desktop integration suite now has eleven cases, including migration of v1/0.4.4 records, repeat repair/removal, one-ID replacement, user edits and autostart preservation. All three CTests and the generated Arch package build passed. The installed official package still reported 361 files and zero altered files; Hyprland configuration had no errors. A full reboot was not performed.


Release 0.4.6 recording-control validation (2026-10-20):

- User reproduced non-clickable cancel/confirm controls. The installed Status rule had `no_focus=true`; Hyprland 0.56.2 pointer hit-testing explicitly skips such windows.
- Removing that exclusion and suppressing hover/initial focus made controls clickable, but the user reported confirmation text missing from the original field. The active window was Status and the native logs showed Fcitx focus timeouts followed by clipboard fallback.
- An isolated GTK reproduction created its own input receiver, transferred focus to the existing Status window and attempted one fixed synthetic commit. Before restoration it failed with `NO_FOCUS`; with the compositor event callback the same probe restored the receiver and committed the exact expected text. Reusable command: `python tests/hud-focus.py` with Typeless already running. This simulates the focus transition; it is not an automated mouse/speech test.
- The user then confirmed both actual mouse cancel and mouse confirm work, including text delivery to the original input field. The temporary rule/handler was used for acceptance; final deployment uses the packaged Lua include.
- Eleven headless cases exercise the actual Lua callbacks, including no original target, expired objects, hidden/unmapped/invisible targets, workspace mismatch, subsequent user focus changes and unaffected AI-result focus. These are separate from the real pointer/speech acceptance above.
- No native input bridge, vendor runtime transformation, updater behavior or official account/onboarding code was changed. The separate update-policy research remains a recommendation, not an implemented update change.


Local 0.4.7 pointer regression attempt (not released) (2026-10-20):

- The user reported cursor jumps when clicking web content with no recording active or visible HUD. The mapped transparent Status window occupied 750×500 logical pixels; the focus dispatcher used by 0.4.6 explicitly warps the cursor.
- The new actual-Lua callback test fails against the original restoration call. Thirteen cases now cover cursor-warp suppression, restoration of both possible user policy values, and restoration after a dispatcher error in addition to the prior focus guards.
- A guarded runtime predicate makes empty/degenerate HUD regions ignore mouse events on the compatibility Wayland path, while valid controls and other launch environments preserve the vendor behavior. Its isolated JavaScript regression passes; private archive tests verify the guarded replacement and unchanged vendor archive.
- Five CTest suites and the staged Arch package build pass. After installing the local 0.4.7 package and restarting only Typeless, the GUI probe passed exact synthetic input and unchanged cursor coordinates/policy. Hyprland configuration errors were empty; the installed official package still had 361 files and zero altered files.
- These checks do not establish per-pixel click-through around a visible HUD, every multi-monitor scenario, or actual mouse/speech acceptance. No updater policy change is installed with this repair.


Release 0.5.0 correction and package update policy (2026-10-20):

- User acceptance rejected the first pointer repair. The earlier synthetic focus test did not exercise actual pointer hit-testing. A real uinput click on an isolated GTK button failed while the Status overlay accepted input; excluding Status with compositor no_focus made the same click succeed.
- The running private archive contained the attempted repair; the app reported empty element positions. Directly setting Electron mouse-ignore true still failed the real click test on this session. Thus the initial empty-region API change was insufficient.
- A later idle popup exposed why active/idle classification alone was insufficient. The guarded HUD adapter now publishes only numeric padded control rectangles in its internal title. Hyprland uses actual window geometry and cursor coordinates to accept pointer input only over those rectangles. The 8 ms compositor timer stops when no rectangles remain. This is a polling workaround, with a short boundary race, not a native Wayland input-region implementation.
- A real click test on a synthetic control region also reproduced cursor warping despite the scoped no_warps change. A focused trace then found a second desktop-state focus event after the initial mouse click. The correction captures cursor coordinates at Status activation and restores that position during the guarded callback, covering the later compositor warp without changing global cursor configuration.
- Six CTest suites pass, including sixteen Lua cases, production HUD adapter transitions and the package update policy. Official source fingerprints remain mandatory; the overlay now checks four modules. Unsupported vendor builds are not automatically qualified.
- The live app returned null for background updater polling and an explicit managedByPackageManager result for manual version checks, without starting a download or showing a dialog. About alone requests the package-policy information dialog; the shared setup diagnostic does not. Pending vendor .deb cache files are left intact and cannot be installed through the intercepted compatibility-mode IPC path.
- Final live checks passed: an actual click outside a synthetic visible popup reached the underlying isolated GTK button without cursor/focus movement; a click inside a synthetic control region stayed on the HUD without moving the cursor; a synthetic commit after the focus transition reached the original isolated receiver. Diagnostic helpers and their loopback inspector were stopped/removed; normal launcher startup was restored. The vendor package still had 361 unchanged files. The user then confirmed the normal launch build: underlying web controls work, updater prompts no longer recur, and actual recording confirm/cancel and input remain normal. No proprietary archive or private diagnostic data is distributed.


0.5.1 / official 2.2.1 qualification (2026-10-21):

- The installed 0.5.0 overlay refused 2.2.1's changed module paths; the existing process still used the old 2.2.0 cache. No blind fingerprint update was applied.
- The actual new completion handler replay failed without preflight and passed all three routing fixtures after adaptation. Both the legacy four-file and new three-file profiles retain hash/unique-anchor refusal.
- The first native test failed to load the new library because g_bus_get_sync was unresolved. Explicitly loading GIO exposed the direct Fcitx calls; native commits could succeed, but restore queries stalled cleanup. The new exact-call/PID adapter resolved both selection and shutdown behavior.
- Real native-library tests passed isolated GTK and cross-workspace Foot insertion with the voice-ime backend marker and preserved Shuangpin. Nine CTest suites and the staged Arch package build pass, including fake-backend/private-socket tests for GIO scope and transparent fallback.
