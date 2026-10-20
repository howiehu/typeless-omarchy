# Contributing

This is an independent compatibility project. Keep contributions focused on input delivery, narrowly matched desktop integration and reproducible compatibility fixes.

## Development

Use Arch Linux with `base-devel`, CMake, Fcitx5 development files, json-c, GLib, Python, Lua (headless focus tests) and dbus. From a clean checkout:

```sh
cmake -S . -B build-ci -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=Release
cmake --build build-ci
ctest --test-dir build-ci --output-on-failure
python tools/stage-package.py /tmp/typeless-package
cd /tmp/typeless-package
makepkg --noconfirm
```

These tests start a separate D-Bus/Fcitx session and do not restart the desktop input method. GUI acceptance tools in `tests/live-input.py` temporarily change focus/workspace; use an idle test desktop. Typeless-specific tests require a separately installed official app. Never add vendor archives or extracted vendor source to git.

## Pull requests

Explain the reported behavior, the change and the validation. Add a regression test when it exercises the actual failure. Include manual desktop results when a headless check cannot prove them. Do not claim general Wayland/GPU support from one machine.

Runtime changes must retain exact vendor fingerprint checks, leave the vendor installation untouched, and preserve the official login/deep-link paths. Do not globally replace D-Bus, clipboard, PATH or the user's input-method group. Do not add account/history polling to recover results.

Keep code changes separate from generated packaging. `tools/stage-package.py` produces a local-source recipe; `packaging/PKGBUILD.in` produces the release-source recipe. Neither should include copied vendor files.

Use synthetic text and sanitized logs. Do not submit tokens, cookies, account databases, personal dictation, core dumps or unredacted desktop captures. Report suspected security vulnerabilities privately as described in [SECURITY.md](SECURITY.md).

Original contributions are submitted under the MIT license only to the extent contributors hold rights they can grant. Preserve third-party attributions and do not relicense vendor code, match fragments or other third-party material as your own. Read LICENSE and NOTICE before contributing. Local generation and source fingerprint checks are technical safeguards, not evidence of vendor permission or a legal exception.
