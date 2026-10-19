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
files = ["CMakeLists.txt", "src/voice.cpp", "data/typeless-voice-addon.conf",
         "runtime/prepare.py", "tests/runtime.py", "tests/result-routing.cjs", "helpers/gdbus", "data/typeless.lua", "bin/typeless-omarchy",
         "bin/typeless-omarchy-setup", "tests/protocol.py", "tests/input-probe.py",
         "tests/native-insert.py", "tests/live-input.py", "tools/install-user.py",
         "tools/stage-package.py", "docs/validation.md", "LICENSE", "README.md"]
for name in files:
    shutil.copy2(root / name, target / Path(name).name)
names = [Path(name).name for name in files]
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
checkdepends=('dbus')
optdepends=('typeless-bin: official Typeless application (AUR)'
            'omarchy: opt-in desktop integration')
options=('!debug')
'''
recipe += "source=(" + "\n        ".join(repr(name) for name in names) + ")\n"
recipe += "sha256sums=(" + "\n            ".join(repr(value) for value in checksums) + ")\n"
recipe += '''
prepare() {
  mkdir -p src data bin tests tools docs helpers runtime
  cp prepare.py runtime/
  cp runtime.py result-routing.cjs tests/
  cp voice.cpp src/
  cp typeless-voice-addon.conf typeless.lua data/
  cp gdbus helpers/
  cp typeless-omarchy typeless-omarchy-setup bin/
  cp protocol.py input-probe.py native-insert.py live-input.py tests/
  cp install-user.py stage-package.py tools/
  cp validation.md docs/
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
