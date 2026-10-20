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

The `Status` recording canvas persists after an application restart and is transparent while idle. With no workaround Hyprland draws a visible empty frame. The final rule removes decorations, blur and focus only for class `Typeless`, title `Status`; verified border_size=0 and no_focus=true plus local visual inspection. Only the recording canvas is pinned across workspaces. No dashboard rule, extra tray icon or visibility service is installed.

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
