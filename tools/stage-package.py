#!/usr/bin/python
"""Stage a reviewable local-source Arch recipe; no downloads or installation."""
import hashlib
import json
import re
from pathlib import Path
import shutil
import sys

root = Path(__file__).resolve().parent.parent
version = re.search(r"project\(typeless-omarchy VERSION ([0-9.]+)", (root / "CMakeLists.txt").read_text()).group(1)
target = Path(sys.argv[1]).resolve()
target.mkdir(parents=True, exist_ok=True)
files = ["CMakeLists.txt", "src/voice.cpp", "src/query.cpp", "tests/query.py", "tests/query-backend.cpp", "data/typeless-voice-addon.conf",
         "runtime/prepare.py", "runtime/build221.py", "tests/build221.py", "tests/vendor-feed.py", "tools/check-vendor.py", "runtime/update-policy.mjs", "tests/update-policy-test.mjs", "tests/runtime.py", "tests/desktop.py", "tests/status-focus.lua", "tests/hud-pointer.cjs", "tests/result-routing.cjs", "helpers/gdbus", "data/typeless.lua", "bin/typeless-omarchy",
         "bin/typeless-omarchy-setup", "tests/protocol.py", "tests/input-probe.py",
         "tests/native-insert.py", "tests/live-input.py", "tests/hud-focus.py", "tests/pointer-click.py", "tools/install-user.py",
         "tools/stage-package.py", "docs/validation.md", "docs/typeless-2.2.1.md", "LICENSE", "NOTICE", "README.md"]
for name in files:
    shutil.copy2(root / name, target / ("build221-test.py" if name == "tests/build221.py" else Path(name).name))
names = ["build221-test.py" if name == "tests/build221.py" else Path(name).name for name in files]
checksums = [hashlib.sha256((target / name).read_bytes()).hexdigest() for name in names]
recipe = '''# Package-local compatibility sources; no vendor binary redistribution.
pkgname=typeless-omarchy
pkgver=@VERSION@
pkgrel=1
pkgdesc='Fcitx5 dictation bridge and opt-in Wayland desktop integration for Typeless'
arch=('x86_64')
url='https://github.com/howiehu/typeless-omarchy'
license=('MIT')
depends=('fcitx5' 'json-c' 'glib2' 'python' 'systemd' 'desktop-file-utils')
makedepends=('cmake' 'gcc' 'pkgconf')
checkdepends=('dbus' 'lua' 'nodejs')
optdepends=('typeless-bin: official Typeless application (AUR)'
            'omarchy: opt-in desktop integration')
options=('!debug')
'''
recipe += "source=(" + "\n        ".join(repr(name) for name in names) + ")\n"
recipe += "sha256sums=(" + "\n            ".join(repr(value) for value in checksums) + ")\n"
recipe += '''
prepare() {
  mkdir -p src data bin tests tools docs helpers runtime
  cp prepare.py update-policy.mjs runtime/
  cp build221.py runtime/
  cp build221-test.py tests/build221.py
  cp vendor-feed.py tests/
  cp check-vendor.py tools/
  cp update-policy-test.mjs tests/
  cp runtime.py desktop.py status-focus.lua hud-pointer.cjs result-routing.cjs tests/
  cp voice.cpp src/
  cp query.cpp src/
  cp query.py query-backend.cpp tests/
  cp typeless-voice-addon.conf typeless.lua data/
  cp gdbus helpers/
  cp typeless-omarchy typeless-omarchy-setup bin/
  cp protocol.py input-probe.py native-insert.py live-input.py hud-focus.py pointer-click.py tests/
  cp install-user.py stage-package.py tools/
  cp validation.md typeless-2.2.1.md docs/
}

build() {
  cmake -S . -B build -DCMAKE_INSTALL_PREFIX=/usr -DCMAKE_BUILD_TYPE=None
  cmake --build build
}

check() {
  ctest --test-dir build --output-on-failure
}

package() {
  DESTDIR="$pkgdir" cmake --install build
  install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}
'''
(target / "PKGBUILD").write_text(recipe.replace("@VERSION@", version))
(target / ".omarchy").mkdir(exist_ok=True)
(target / ".omarchy/package.json").write_text(json.dumps(
    {"source": "local", "sync": False, "rebuild_on": ["fcitx5"]}, indent=2) + "\n")
print(target)
