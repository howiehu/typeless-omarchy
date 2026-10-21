# Release procedure

Releases are manual. Formal release status does not expand the documented desktop coverage or imply vendor/distribution endorsement. Use a pre-release only when deliberately publishing a candidate.

## Qualify an official Typeless update first

Before changing a vendor profile or declaring support for another Typeless build:

1. Read the official [release-notes index](https://www.typeless.com/help/release-notes) and [Linux release notes](https://www.typeless.com/help/release-notes/linux) first. Consult the [Linux update feed](https://typeless-static.com/desktop-release/latest-linux.yml) for version, publication timestamp and artifact identity; the feed is not a substitute for release notes.
2. Record the review date, source links, vendor version and relevant changes in `docs/typeless-<version>.md`. If detailed notes are unavailable, say so explicitly. Missing notes do not establish that behavior or interfaces are unchanged.
3. Compare the actual installed vendor build with the qualified profile. Check native input/Fcitx calls, window and pointer behavior, renderer routing, autostart and updater integration as applicable. Run `python tools/check-vendor.py --archive /opt/Typeless/resources/app.asar`; a refused fingerprint requires investigation, not automatic acceptance of new hashes.
4. Implement only the necessary adaptations, run the relevant automated and real-session checks, and record their results and limits before declaring that build qualified. Then follow the project release steps below.

The scheduled version watcher only detects unqualified version numbers. It does not read or approve release notes, verify same-version rebuilds, or replace this review. Keep these source links in the watcher and checker diagnostics so a future failure points maintainers back to this procedure.

## Publish a qualified compatibility release

1. Set the version in `CMakeLists.txt`, update the README's install tag and add a changelog entry. `tools/stage-package.py` reads the CMake version.
2. Follow [the QA procedure](qa.md): run a clean independent-directory CMake build, CTest and the generated local-source `makepkg` recipe, then applicable installed-build probes and manual M01–M09 cases. Record the source/package identity, report links, failures and untested scope using its acceptance template; keep human confirmations distinct from automated checks.
3. Inspect the git file list. No proprietary archives, generated runtime copies, binaries, account files, private logs or desktop captures belong in the source release. Verify LICENSE/NOTICE scope, English/Chinese consistency and installed notice files. Preserve attribution for third-party matching fragments; do not present technical guards as vendor authorization.
4. Push the reviewed commit to `main` and wait for the Arch CI build to pass. Record the source commit and CI URL in the release notes. Do not infer GUI coverage from CI.
5. Tag that exact commit with `v<version>`. Create the project source archive with `git archive --format=tar --prefix=typeless-omarchy-<version>/ <tag> | gzip -n`. SHA-256 the archive, substitute `@VERSION@` and `@SHA256@` in `packaging/PKGBUILD.in`, and build/test that recipe against the archive.
6. Upload the source archive, generated `PKGBUILD` and `SHA256SUMS` to a GitHub release for the same tag (mark it as a pre-release only for an explicit candidate). Verify downloaded bytes against the recorded checksums. Do not distribute the generated Typeless runtime or claim artifacts are signed unless signatures actually exist.
7. Update the Omarchy package recipe to the immutable release URL/checksum and link the independent project and validation evidence in its PR. Follow the distribution's build/review rules; do not merge your own contribution upstream.
8. Prepare the product-support report and optional social post from `docs/publication.md`. Actual delivery is separate from creating a GitHub release. Do not publish personal desktop material as demonstration footage.

An already published release filename must not be replaced with different bytes. Correct it with a new project version or package release, documenting the change. Older release archives stay available for reproducibility.
