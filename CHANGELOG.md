# Changelog

## 0.5.2 — 2026-10-24 — release

- Fix a 0.5.0 regression that hung Omarchy's Super+K source scanner: its callable-table API proxy never terminates under `ipairs`. Skip compositor integration before any runtime operations when the real window enumeration function is absent.
- Guard new Lua includes; migrate recognized plain and user-guarded blocks, collapse duplicate managed blocks, and remove either form. Preserve unrelated configuration and refuse unknown/malformed marked blocks before changing integration files.
- Add a bounded source-scan regression and migration/idempotence/removal cases. Include the reusable QA runner and manual acceptance checklist introduced after 0.5.1.

## 0.5.1 — 2026-10-21 — release

- Qualify the exact official Typeless 2.2.1 build with a guarded three-module profile; retain the existing 2.2.0 profile and refusal of unknown fingerprints.
- Adapt the new direct GIO/Fcitx input-method query only in the Typeless main process while the passive bridge responds. Preserve the real selected input method and transparently forward unrelated calls.
- Verify native GTK/cross-workspace Foot input, input-method preservation, normal Wayland startup and idle-HUD click-through on 2.2.1. Add isolated query-scope tests and retain prior UI/update-policy coverage.
- Monitor official version metadata every six hours without automatically qualifying or publishing vendor builds. Document a release-notes-first qualification procedure with official source links in both READMEs, the checker and the workflow.

## 0.5.0 — 2026-10-20 — release

- Bound HUD pointer hit-testing to numeric control regions; pass clicks through the transparent remainder and preserve pointer position while restoring the input target.
- Keep in-app background update requests silent and route manual checks to the package workflow, blocking the vendor Debian download/restart-install path in the guarded runtime.
- Preserve official main/tray/login behavior and record the tested pointer, recording confirmation/cancellation and text-delivery coverage and limits.

## 0.4.6 — 2026-10-20 — release

- Fix recording HUD cancel/confirm buttons being excluded from Hyprland pointer hit-testing by `no_focus`. Keep initial/hover focus suppression.
- Restore keyboard focus from Status to the preceding live, visible window on the same workspace, so clicking confirm retains the original Fcitx input target. Respect subsequent focus changes and keep AI-result cards interactive.
- Add eleven headless focus-safety cases and a dedicated isolated GTK focus/commit GUI regression. Real cancel/confirm behavior was user-confirmed.


## 0.4.5 — 2026-10-20 — release

- Replace the official desktop ID with one marked per-user compatibility entry named Typeless instead of leaving two visible menu entries. The project/package remains Typeless-Omarchy. Official protocol registration now resolves to the same launcher.
- Guard the exact vendor cleanup branch so it retains only the marked compatibility override; unrelated entries retain their original handling.
- Migrate the managed 0.4.4 duplicate while preserving original rollback records and later user edits.
- Retain the 0.4.4 autostart routing and official enabled/disabled setting.


## 0.4.4 — 2026-10-20 — release

- Install an independent `typeless-omarchy.desktop` entry that survives the official app's cleanup of same-name user overrides.
- Add `typeless-omarchy-setup --repair` to migrate existing desktop state without restarting Fcitx; preserve rollback records and refuse later menu edits.
- Keep official autostart generation routed through the compatibility launcher using a third exact-fingerprint runtime transformation; preserve startup arguments and the official enable/disable setting.
- Repair recognized existing startup commands and preserve user toggles when removing the compatibility integration.
- Add isolated desktop migration/rollback regressions; retain the existing dictation, answer-card and scrolling behavior.


## 0.4.3 — 2026-10-19 — release

- Clarify the copyright attribution as Hao Hu and contributors without changing the MIT license text.
- Add a shared English/Chinese NOTICE distinguishing original contributions from vendor matching fragments, dependencies and generated runtime material.
- Explicitly distinguish technical safeguards/non-distribution from vendor permission or legal clearance, with references to the relevant Typeless terms.
- Install NOTICE beside LICENSE and align the README, contribution guide, report and packaging.
- Record that X was posted and email outreach was cancelled. Runtime behavior is unchanged.

## 0.4.2 — 2026-10-19 — pre-release

First standalone public release. Tested on one Omarchy x86_64 desktop; broader desktop and GPU compatibility is not established.

- Passive Fcitx5 module delivers dictation without changing the selected input method.
- Native Wayland launcher and reversible per-user desktop setup.
- Frameless, non-focusable Status HUD and interactive AI-result cards across workspaces.
- Exact-fingerprint runtime patch shows the official Ask Anything answer card when its replace branch has no eligible input context.
- App-scoped software rendering avoids the scrolling tile artifacts confirmed on the test desktop; a hardware-rendering override is available.
- Headless protocol/runtime tests, Arch packaging and independent-directory CMake test support.
- Public installation, rollback, contribution and upstream-report documentation.

Local development versions 0.1–0.4.1 preceded this standalone release. They are not retroactively published as releases.
