# Release procedure

Releases are manual. Formal release status does not expand the documented desktop coverage or imply vendor/distribution endorsement. Use a pre-release only when deliberately publishing a candidate.

1. Set the version in `CMakeLists.txt`, update the README's install tag and add a changelog entry. `tools/stage-package.py` reads the CMake version.
2. Run a clean independent-directory CMake build, CTest and the generated local-source `makepkg` recipe. Run applicable desktop acceptance tests separately; keep human confirmations distinct from automated checks.
3. Inspect the git file list. No proprietary archives, generated runtime copies, binaries, account files, private logs or desktop captures belong in the source release. Verify LICENSE/NOTICE scope, English/Chinese consistency and installed notice files. Preserve attribution for third-party matching fragments; do not present technical guards as vendor authorization.
4. Push the reviewed commit to `main` and wait for the Arch CI build to pass. Record the source commit and CI URL in the release notes. Do not infer GUI coverage from CI.
5. Tag that exact commit with `v<version>`. Create the project source archive with `git archive --format=tar --prefix=typeless-omarchy-<version>/ <tag> | gzip -n`. SHA-256 the archive, substitute `@VERSION@` and `@SHA256@` in `packaging/PKGBUILD.in`, and build/test that recipe against the archive.
6. Upload the source archive, generated `PKGBUILD` and `SHA256SUMS` to a GitHub release for the same tag (mark it as a pre-release only for an explicit candidate). Verify downloaded bytes against the recorded checksums. Do not distribute the generated Typeless runtime or claim artifacts are signed unless signatures actually exist.
7. Update the Omarchy package recipe to the immutable release URL/checksum and link the independent project and validation evidence in its PR. Follow the distribution's build/review rules; do not merge your own contribution upstream.
8. Prepare the product-support report and optional social post from `docs/publication.md`. Actual delivery is separate from creating a GitHub release. Do not publish personal desktop material as demonstration footage.

An already published release filename must not be replaced with different bytes. Correct it with a new project version or package release, documenting the change. Older release archives stay available for reproducibility.
