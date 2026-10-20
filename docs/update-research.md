# Typeless on Omarchy: update strategy research

Research date: 2026-10-20. This note began as research; the recommendation is implemented in the 0.5.0 release. No vendor upgrade, desktop configuration change or publication was performed for this research.

## Recommendation (implemented in 0.5.0)

Use one installation authority: keep the existing `typeless-bin` AUR workflow for the official binary, and separately released, explicitly validated compatibility code. For the immediate release, make a small, guarded change suppressing the in-app Debian download/install path and its misleading Restart action. Explain that installation is managed through the package workflow. Preserve useful version information if it can be shown without advertising an unsupported Restart action. This does not require a new updater daemon, a replacement vendor package, or an automatic porting platform.

There is no need to build another automatic installation or adaptation service now. Omarchy already has upstream discovery, update PRs, builds and publication machinery. Automated discovery can help maintainers later; a green compilation test cannot establish that a changed proprietary application still preserves input methods, shows answer cards correctly or handles login/startup. Keep manual compatibility acceptance before supporting a new vendor build.

This is a project recommendation inferred from the inspected package behavior and the first-party mechanisms below, not an Arch or Typeless certification.

## Distribution update mechanism

Electron's own `autoUpdater` documentation recommends distribution package managers for Linux. This is general platform guidance: Typeless uses the separate `electron-updater` library, which does implement Linux package installation, so the Electron statement does not prove that Typeless cannot attempt an update. [Electron platform notices](https://www.electronjs.org/docs/latest/api/auto-updater/#platform-notices)

Pacman's system upgrade operation works with configured sync databases; its `--foreign` filter identifies packages absent from them. Thus an AUR-built installation tracked by pacman does not automatically acquire an update source merely because its files are in the local database. AUR recipe updates/builds must still happen through an AUR workflow unless the package is supplied by a configured binary repository. [pacman manual](https://man.archlinux.org/man/pacman.8.en)

The live AUR `typeless-bin` recipe fetched on the research date was `2.2.0-1`. It downloads the vendor `.deb`, extracts its payload, creates the executable link and packages device/IBus data. There is no updater-disable transformation, `prepare()` override, or replacement of the Debian package marker in that recipe. Consequently, repackaging alone does not establish package-manager-only updating. [AUR PKGBUILD](https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h=typeless-bin) Local read-only fetched evidence: `/tmp/typeless-aur-current-PKGBUILD`.

## Reuse Omarchy's existing machinery

Omarchy's repository owns its checked-in recipes and can discover releases directly from vendor/project feeds, changing declared versions and checksums. Importing an AUR recipe is an initial provenance step; its documented process does not periodically import AUR recipe changes. This means our compatibility package being accepted would not by itself establish a coordinated update source for its separate `typeless-bin` dependency. [Direct upstream watches](https://github.com/omacom/omarchy-pkgs/blob/master/docs/upstream-sources.md)

Scheduled workflows already propose upstream and dependency-rebuild PRs, then use the repository's build/publication process. `sync: false` excludes that package from upstream updates; it is neither a pacman version lock nor a restriction on another package that happens to be a dependency. Keep this hold until the compatible vendor/version publication relationship is designed and reviewed. [Omarchy package automation and metadata](https://github.com/omacom/omarchy-pkgs/blob/master/README.md#automatic-updates)

Two independent watches with automatic merging would not guarantee a matching vendor/compatibility pair. Before enabling them, decide who owns the vendor recipe, how a supported vendor build is represented, and how a failed compatibility check prevents publication. Do not point a compatibility-layer watch at vendor releases and assume a version/checksum bump adapts the patch.

## Updater options: exact version matters

The `electron-builder` source tag `v26.0.12` identifies its `electron-updater` package as `6.6.2`, matching the locally inspected library version reported during this investigation. [Version manifest](https://github.com/electron-userland/electron-builder/blob/v26.0.12/packages/electron-updater/package.json)

In this version, `autoDownload` controls whether an available update is automatically downloaded by `checkForUpdates()`. It does not forbid callers from explicitly invoking `downloadUpdate()`. `autoInstallOnAppQuit` controls the library's quit handler; it does not block an application's explicit `quitAndInstall()` or an independent installer script. These flags are application API properties, not documented shell environment overrides. [AppUpdater 6.6.2 implementation](https://github.com/electron-userland/electron-builder/blob/v26.0.12/packages/electron-updater/src/AppUpdater.ts), [BaseUpdater 6.6.2 implementation](https://github.com/electron-userland/electron-builder/blob/v26.0.12/packages/electron-updater/src/BaseUpdater.ts)

The matching generic `DebUpdater` uses `dpkg` and an `apt-get` repair fallback. This supports the format mismatch but is not proof of Typeless's exact installer path: Typeless has its own Linux update code, which must be inspected separately. [DebUpdater 6.6.2 implementation](https://github.com/electron-userland/electron-builder/blob/v26.0.12/packages/electron-updater/src/DebUpdater.ts)

The current Typeless settings guide documents audio, appearance, shortcuts and launch-at-login; it does not document a user-facing updater switch. This absence does not prove that no switch exists in a particular build. Prefer a verified official/package-supported setting if one is subsequently found. [Typeless settings guide](https://www.typeless.com/help/quickstart/settings)

## Can the notification simply be ignored?

Temporarily closing the prompt and continuing with the tested version is reasonable. It avoids intentionally starting the known incompatible Debian installer. It is not a complete long-term update policy: the confusing action remains, a download may already exist, and future vendor fixes still need review.

Do not infer from generic updater defaults that normal exit automatically installs an update. Inspect Typeless's overrides and custom installer first. Conversely, setting `autoInstallOnAppQuit=false` alone cannot neutralize an explicit Restart handler. Avoid installing Debian package tools merely to make this button work; that would introduce a second installation authority instead of integrating with Arch.

An explicit supported-build message and a small package-managed update policy are preferable to permanent silent staleness, network blocking, invented package markers, or a broad patch rewriting all update internals. Unknown vendor builds should continue to be refused by exact patch guards, and users should be told what functionality is unavailable. A dependency constraint may enforce a supported range but must be considered with the full Arch upgrade transaction; do not recommend a blanket long-term system update hold.

## Local evidence

The following observations were verified locally on 2026-10-20. They are observations of the separately installed proprietary build, not upstream API guarantees. Only derived descriptions are recorded; extracted vendor modules and account data are not distributed.

- Installed packages: `typeless-bin 2.2.0-1`, `typeless-omarchy 0.4.5-1`. The bundled `electron-updater/package.json` reports 6.6.2. `resources/package-type` contains `deb` even though pacman owns the installation. The downloaded pending vendor update is the 2.2.1 Debian archive.
- The official main module configures `autoDownload=false`, but the application exposes explicit download IPC and the pending file demonstrates a download occurred. Treating that property as a disable switch is incorrect.
- The official Linux policy disables `autoInstallOnAppQuit` for recognized deb/rpm builds outside AppImage mode. An isolated replay of the actual policy function with a deb/Linux fixture changed the property from true to false. The replay loaded no Electron application and spawned no installer. Therefore the generic library's default does not justify a claim that closing this prompt or normally quitting installs the pending package.
- The explicit Restart IPC instead enters a separate vendor Linux installer path. It prepares a detached shell that waits for the main PID to exit, invokes `pkexec` with a Debian install/repair command, and then executes `process.execPath`. The shell continues to the relaunch after installer failure. For the current compatibility runtime this is the cached executable, rather than the launcher with its arguments and parent-process helper scoping. This conclusion is from code inspection; Restart was not clicked and the installer was not executed.
- Neither `dpkg` nor `apt-get` is resolvable on the host PATH. The existing installer command is therefore unsuitable even before considering the compatibility-layer relaunch issue.
- Inspection of updater-related renderer references found an `autoUpdate`/`closeAutoUpdate` navigation/dialog mechanism, not a verified persistent disable-updates preference. The public settings guide also does not establish such a setting. Do not invent an environment variable or advertise an unverified UI switch.
- The downloaded 2.2.1 archive has different relevant module paths from those guarded by the current overlay. It was inspected only under `/tmp`; it was not installed or executed. Supporting 2.2.1 requires checking the actual new behavior before changing fingerprints, not merely accepting renamed bundles.

## Practical order of work

1. For now, dismiss the pending update prompt and keep the tested application/compatibility pair. There is no need to roll back the completed menu changes or urgently upgrade solely because this notification appeared.
2. Make a small opt-in package-managed updater policy: prevent incompatible package download/installation and misleading Restart actions for this installation, and provide a clear package-update instruction. Cover explicit IPC, any background download path and already-downloaded update state; setting one generic library flag is insufficient. Keep the policy local to this app and fail visibly for unrecognized vendor code.
3. Continue using the existing AUR recipe/build workflow for the vendor binary and explicit compatibility release qualification. The AUR recipe was still 2.2.0-1 at research time. If the project later owns both recipes in an accepted binary repository, design coordinated qualification there using the existing Omarchy update workflow.
4. Seek an official distribution-managed/no-self-update option or a packaging fix upstream so the compatibility layer can eventually drop this policy. Reassess private patch scope as vendor fixes arrive; automation may report new releases, but should not approve new fingerprints on its own.

This research did not install the new vendor release, disable updater settings, alter running processes or publish repository changes.
