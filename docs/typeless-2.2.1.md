# Typeless 2.2.1 qualification

Audit date: 2026-10-21. The official [Linux release-notes page](https://www.typeless.com/help/release-notes/linux) has a heading but no detailed 2.2.1 entry in the fetched page. The [Linux update feed](https://typeless-static.com/desktop-release/latest-linux.yml) identifies 2.2.1 and releaseDate 2026-10-19T12:15:03.255Z, archive URLs and checksums, without change descriptions. No claim of unchanged behavior follows from this absence.

The official [release-notes index](https://www.typeless.com/help/release-notes) is the starting point for future reviews. Follow the [vendor qualification procedure](releasing.md#qualify-an-official-typeless-update-first) before changing any profile; this audit records the actual-build investigation required when detailed notes are unavailable.

## Observed changes

- The old bootstrap and startup modules are consolidated into `dist/main/index.js`. Autostart generation, same-name desktop cleanup, HUD shape updates and updater IPC remain. A separate profile qualifies the new file and the two affected renderer modules, preserving the old four-module 2.2.0 profile.
- About update checking moved into `BRBPsUW-.mjs`; the answer completion route moved into `BT1_b3hq.mjs`. In-memory replay of the unmodified 2.2.1 handler still attempted insertion with no eligible context; the patched handler opens the official card in that case and preserves focused editable insertion.
- The native input helper now imports GIO functions including g_bus_get_sync and g_dbus_connection_call_sync without declaring a direct GIO library dependency. Electron's environment supplies it; the isolated ctypes harness now explicitly loads libgio globally before loading the helper.
- With that dependency supplied, a real native trace showed CurrentInputMethod and SetCurrentIM calls through GIO, bypassing the old command-line adapter. The passive module is not a selectable engine. A native commit could reach the isolated receiver, but warmup reported selected=0 and repeated restore queries kept the process alive beyond the harness timeout.
- A launcher-scoped query adapter supplies the virtual engine response only for the exact main-PID Fcitx query and only with a responding passive bridge. It does not intercept SetCurrentIM or change the user's selected engine. Foreign processes, unrelated methods/arguments, canceled calls and missing/invalid endpoints fall back to real GIO. Floating GVariant parameter ownership is preserved. The legacy command adapter remains.

## Evidence and limits

The actual 2.2.1 native library then passed exact GTK and cross-workspace Foot insertion with the voice-ime success marker and identical Shuangpin selection before/during/after. Headless coverage includes both vendor patch profiles, wrong hashes/anchors, isolated GIO scope/fallback, endpoint states, UI rules, updater routing and input protocol guards. Full vendor modules and binaries are not included in this project.

The small scheduled metadata watcher reports unqualified versions but cannot detect vendor same-version rebuilds or prove graphical/voice compatibility. Project CI packages reviewed source; Omarchy's watch follows our formal qualified releases rather than silently accepting vendor changes. The downstream package contribution is still subject to maintainer approval.

Live desktop acceptance of the installed 0.5.1 build is recorded in docs/validation.md; automated checks alone do not establish a fresh account login flow or all monitor/fullscreen combinations. No audio mute policy is changed. Stop/restart verification must first confirm no active microphone stream and no inherited background mute.
