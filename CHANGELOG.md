# Changelog

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
