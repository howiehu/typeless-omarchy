# Typeless 2.2.0 Linux: Omarchy / Hyprland / Fcitx5 compatibility report

Prepared for Typeless engineering. This report describes a community workaround, not an accepted upstream fix. All public evidence uses synthetic text or user-confirmed observations; private dictation, account databases, screenshots and diagnostic sessions are not distributed.

Project: https://github.com/howiehu/typeless-omarchy

Omarchy packaging PR: https://github.com/omacom/omarchy-pkgs/pull/1294

## Environment and scope

- Omarchy 4.0.5, x86_64; Hyprland 0.56.2 native Wayland.
- Fcitx5 5.1.23; Shuangpin and English keyboard modes.
- Official Typeless Linux 2.2.0, installed as `typeless-bin 2.2.0-1`.
- GTK text entries, browser fields and Foot were exercised. The rendering observation comes from one desktop with fractional display scaling, not a matrix of GPUs.
- Exact tested main/renderer hashes and fail-closed patch guards are in `runtime/prepare.py`.

## 1. Input delivery and preserving the selected input method

**Reproduce:** focus an isolated Foot text receiver, dictate synthetic Chinese/English text, and compare the received string with the requested insertion. Repeat with Shuangpin selected, interleaving manual Chinese before and after dictation, then switch to English.

**Observed:** the inspected vendor package expected `typeless-voice` but contained no corresponding Fcitx addon binary. Its simulated clipboard fallback reported success when Foot received no text. A first selectable-engine replacement delivered text but displaced the user's selected engine during warmup/restore.

**Expected:** deliver to the current input context while preserving the user's active engine, without treating a simulated paste as proof of delivery.

**Community workaround:** a passive Fcitx module implements the existing local VoiceIME protocol and commits to the genuinely focused input context. A per-process, exact-query adapter prevents the helper from switching the user's engine. GTK, Foot and cross-workspace tests delivered exact synthetic strings; real engine names stayed unchanged before/during/after warmup. The user confirmed mixed Shuangpin/voice input and English switching.

**Suggested upstream direction:** ship or document a supported Fcitx backend and use an input-method-independent commit path. The private query adapter should become unnecessary once the official helper can select a passive delivery backend directly.

## 2. Native Wayland overlay semantics

**Reproduce:** launch on native Wayland, leave the recording canvas idle, then change workspace during dictation. Open an Ask Anything answer and change workspace again.

**Observed:** the idle transparent `Status` canvas was presented with an empty rectangular frame; official overlay intent did not map fully to compositor behavior across workspaces. Native-Wayland execution also required avoiding an X11 helper path that emitted `BadWindow` errors.

**Community workaround:** launch with native Wayland while removing `DISPLAY` only from the app process. Narrow class/title rules remove border, shadow and blur from the recording HUD and keep it floating/pinned. Version 0.4.6 permits its cancel/confirm pointer input while suppressing initial/hover focus and restoring the preceding keyboard target; see section 6. The official interactive `AI result` card retains its focus behavior. No dashboard, tray, login or onboarding controller is added.

**Important correction:** native constructors share a translated title key, but a real mapped answer card uses the title `AI result`. The earlier suspicion that a `Status`-only no-focus rule explained the missing answer was not established. Actual window observation distinguished the roles.

**Suggested upstream direction:** distinguish HUD and interactive-result roles through stable, documented surface properties and support the compositor's Wayland overlay/window semantics without relying on X11 behavior.

## 3. Ask Anything replace result lost when there is no eligible input target

**Reproduce:** select non-editable text, press Right Alt + Space, and ask for an explanation or translation. The relevant completion is classified as `delivery=replace`. The focus/insertion classification can lead to an insertion attempt despite no eligible input context.

**Observed:** an answer was generated and retained in app history, but no result card mapped. The native path logged focus-in timeouts followed by a clipboard-paste success status. The vendor renderer's replace handler attempts insertion and conditionally suppresses its answer card according to accessibility/application classification. That condition does not establish successful delivery.

**Replay evidence:** `tests/result-routing.cjs` extracts the actual locally installed completion function. With an absent input context and an insertion-classified application, the original function produces one insertion attempt and zero cards. A stale editable hint also prevents reliable recovery. No proprietary function body is included in this repository.

**Community workaround:** before this replace branch inserts, a private main-process IPC handler checks the passive Fcitx bridge. With no focused, non-sensitive input context, the renderer opens the original official interactive card instead of pasting. With an eligible context it preserves the existing handler. Reply/external actions, ordinary dictation and voice-translation routing are unchanged.

**Validation:** replay tests pass after the patch. A temporary local diagnostic session ran the patched handler with synthetic text, real Fcitx status and the official card entry point on an empty workspace. The card mapped, accepted focus and followed workspace changes. The user subsequently confirmed real answers appeared. Debugging was disabled afterwards and is not part of the launcher.

**Suggested upstream direction:** base the fallback decision on reliable input/delivery state, and show the answer card when there is no usable target or delivery fails. A preflight alone cannot guarantee delivery if focus changes later; the current workaround does not claim otherwise. Rich-text replacement remains outside its general coverage.

## 4. Scrolling tile artifacts in answer cards

**Reproduce:** display a long official answer card and scroll with the mouse wheel on the tested native-Wayland desktop.

**Observed:** the user reported rectangular blocks of displaced text and flicker while scrolling.

**A/B result:** repeat with the same official UI and a 100-paragraph synthetic answer, changing the Typeless launch option to `--disable-gpu`. The user confirmed the artifacts disappeared and scrolling was normal.

**Community workaround:** apply software rendering to Typeless only. `TYPELESS_OMARCHY_GPU=1` restores the original hardware path. This may increase CPU usage and is not evidence that all GPUs require the workaround or that a specific driver is at fault.

**Suggested upstream direction:** reproduce and investigate accelerated transparent-window scrolling, including fractional scaling, and provide a supported per-app rendering fallback or a targeted rendering fix.

## Implementation, validation and adoption

The project offers its original contributions under MIT only to the extent contributors hold rights they can license. Third-party identifiers and small matching fragments retain any applicable third-party rights; see LICENSE and NOTICE. No complete extracted vendor modules, proprietary app or generated patched bundle are release assets. The installed proprietary files remain unchanged; the runtime patch is generated locally only for exact known source hashes. That does not establish authorization: Typeless’s Terms of Service sections 3 and 7 include restrictions relevant to reverse engineering and modification. This project does not claim an applicable exception, vendor permission or legal clearance.

Headless checks cover protocol validation, socket permissions, caller scoping, archive rewriting/integrity and refusal of unsupported hashes. GUI and human acceptance evidence is listed separately in `docs/validation.md`. One post-restart terminal probe lost input focus; a subsequent cross-workspace run passed. These results do not prove race-free delivery, universal compatibility or crash freedom. The earlier application disappearance had no confirmed root cause.

We would welcome guidance on the preferred engineering contact, supported Linux extension interfaces and how to replace these workarounds with official fixes. The minimal, reproducible cases and independent implementation can be used to guide source-level changes without adopting the compatibility layer's private-runtime mechanism.

## 5. Menu override removed and autostart bypasses compatibility

**Reproduce:** install a per-user `typeless.desktop` override pointing to the compatibility launcher while the official system entry exists, then launch Typeless and inspect the user menu entry and autostart command. Log out/in using that autostart command.

**Observed on 2026-10-20:** the official registration code deletes the same-name user desktop entry when `/usr/share/applications/typeless.desktop` exists. The vendor autostart builder writes the running executable's path, which is the private cache executable in this setup. Both routes then bypass the launcher, losing native-Wayland flags, DISPLAY removal, helper scoping and the rendering workaround. This host's login autostart failed with `X_ChangeProperty / BadWindow`.

**Community workaround (0.4.4):** own a separate `typeless-omarchy.desktop` menu entry. A third fingerprint-guarded transformation changes only the executable passed to the original startup command builder to `/usr/bin/typeless-omarchy` in compatibility mode. The original startup filename, arguments and enable/disable logic remain. The setup repair command migrates legacy records and fixes recognized existing startup commands without restarting Fcitx. No watcher, extra tray or persistent service is installed.

**Suggested upstream direction:** preserve explicitly customized desktop entries and support a stable user-configurable launcher for menu/protocol/autostart integration instead of serializing a temporary runtime path.


**0.4.5 refinement:** the menu now uses a marked same-ID `typeless.desktop` replacement, eliminating the separate official/compatibility choices. Its display name stays Typeless; the independently maintained project/package remains Typeless-Omarchy. The existing exact-fingerprint main-module transformation exempts only an entry containing the project marker and exact compatibility Exec line from vendor cleanup. Official protocol registration continues and resolves to that same replacement. Repair removes the managed 0.4.4 independent entry and retains the original pre-integration backup; uninstall restores the previous entry. No global filesystem interception, watcher, package-owned desktop edit or application-process blocking is used.


## 6. Recording HUD cancel/confirm loses pointer or input target

The prior community Status rule used `no_focus=true`. In Hyprland 0.56.2 this excludes the window from pointer hit-testing, preventing the official cancel/confirm controls from receiving clicks. Allowing focus made both buttons clickable, but clicking confirm moved keyboard focus into Status; the native insertion path then timed out waiting for Fcitx focus and the original input did not receive text. This was confirmed by the user and reproduced with an isolated GTK receiver (`NO_FOCUS`).

0.4.6 keeps initial/hover focus suppression but permits pointer input. A compositor-local `window.active` callback restores only the preceding still-mapped, visible window on the same workspace, provided focus has not since changed to another window. Restoration is deferred by one event-loop timer; there is no background daemon or unfocused-context text injection. Interactive AI-result windows do not trigger restoration. The isolated receiver then accepted the exact synthetic commit, and the user confirmed actual cancel/confirm operation and delivery to the original field. Headless tests cover stale/hidden/closed targets, workspace boundaries, later user focus changes and interactive answers.

The compositor behavior is documented by the version-matched [pointer hit-test](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/desktop/state/ViewHitTester.cpp) and [focus state](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/desktop/state/FocusState.cpp) implementations. This corrects the earlier claim that marking Status globally non-focusable preserved all of its intended functionality. It does not establish coverage for other compositors, fullscreen/layer-shell input or every multi-monitor focus scenario.


### 7. Empty HUD intercepts clicks and focus restoration warps the cursor

After 0.4.6, the user reported clicks on ordinary web controls pulling the cursor to the screen center while no recording HUD was visible. The mapped Status canvas covered 750×500 logical pixels. The version-matched [focus dispatcher](https://github.com/hyprwm/Hyprland/blob/v0.56.2/src/config/shared/actions/ConfigActions.cpp) calls `window->warpCursor()` after focusing the target. This exposed a regression in the community focus callback.

0.4.7 scopes `cursor:no_warps=true` to the synchronous restoration call and restores the preceding value even if dispatch raises an error. It does not permanently change the user's cursor preferences. A fingerprint-guarded runtime change makes an empty/degenerate HUD input region call `setIgnoreMouseEvents(true)` on the supported Wayland path; valid visible controls retain the vendor's clickable path. This does not claim per-pixel click-through for every transparent part of a visible recording canvas.

The headless callback regression fails against 0.4.6 and covers cursor-policy restoration after success/failure. The actual GUI regression additionally compares cursor coordinates and policy before/after the delayed callback and commits a fixed synthetic token only to its isolated receiver. Real pointer acceptance is tracked separately in the validation record. No update policy or new vendor version support is included in this repair.


### 8. Local 0.5.0 follow-up

Real pointer acceptance rejected the empty-region mouse-ignore workaround. On the tested native Wayland runtime, an isolated underlying GTK button still missed the click; excluding Status through Hyprland made it work. A visible idle popup also showed that a binary empty/active distinction is insufficient. The guarded runtime now publishes numeric HUD control rectangles through the internal window title. A compositor-local 8 ms check enables pointer input only over these regions and stops when no regions exist. This avoids a separate daemon but has a short boundary race; native input-region support would be preferable upstream.

A real click trace found the initial click-focus event followed by a desktop-state focus event. Cursor preservation therefore captures coordinates at Status activation, before the deferred callback. Headless focus dispatch alone did not reproduce this sequence.

The compatibility-mode updater setup now registers package-managed IPC handlers before the vendor handlers. Background checks remain silent; manual About checks explain the Omarchy/AUR workflow. Download and explicit restart-install requests do not invoke the vendor updater. Shared onboarding version diagnostics receive an explicit managed result without a dialog. The policy does not qualify a new vendor build or provide a new automatic updater service. A pending cached .deb is left intact.
