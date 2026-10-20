#!/usr/bin/python
"""Build a private, version-checked runtime overlay; never edit vendor files."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile

VENDOR = Path('/opt/Typeless')
MAIN = 'dist/main/bootstrapPrimaryInstance-D2WJURak.js'
ENTRY = 'dist/renderer/static/js/CLnu4epW.mjs'
STARTUP = 'dist/main/index-Dhin5iqu.js'
SETTINGS = 'dist/renderer/static/js/klfO6li7.mjs'
EXPECTED = {
    SETTINGS: '0fcf499c7deaa51421ee817e002c07a87567522d4b5102bea65cd7960bc473fb',
    MAIN: '8d14b7b340113c2bd52943e453bd8c37c3d381c434955765e3d403b66f201c8c',
    ENTRY: '83099ef43191ad8b38d30d6b3f89a43bb78b87ecbe98c1b98db7f6ca1a5c7c62',
    STARTUP: '1bc651a7f4d003b9edf4057f1575b637b4f6d30f65137877b7d167639d3a3d8c',
}
AUTOSTART_ANCHOR = r"pe=_0x49b402=>_0x2ac4ce(0x128)+S+'=1\x20\x22'+_0x49b402+"
AUTOSTART_ROUTER = """const typelessOmarchyAutostartExecutable = executable =>
  process.env.TYPELESS_OMARCHY_ACTIVE === '1' ? '/usr/bin/typeless-omarchy' : executable;
"""
AUTOSTART_HOOK = AUTOSTART_ANCHOR.replace(
    "+_0x49b402+", "+typelessOmarchyAutostartExecutable(_0x49b402)+")
DESKTOP_ANCHOR = '_0x14ba1d[_0x74312e(0xbc8)](_0x5b1f2c),Cu(_0x12df98);'
DESKTOP_GUARD = r'''const typelessOmarchyManagedDesktop = text =>
  process.env.TYPELESS_OMARCHY_ACTIVE === '1' &&
  text.split(/\r?\n/).includes('X-Typeless-Omarchy-Managed=true') &&
  text.split(/\r?\n/).includes('Exec=/usr/bin/typeless-omarchy %U');
'''
DESKTOP_HOOK = 'if(!typelessOmarchyManagedDesktop(_0x12df98)){' + DESKTOP_ANCHOR + '}'
HUD_POINTER_ANCHOR = "Jr=(_0xcbba16,_0x5ae9ae)=>{const _0x238f1b=_0x1cd5da;"
HUD_POINTER_HOOK = HUD_POINTER_ANCHOR + "typelessOmarchyHudState(_0xcbba16,_0x5ae9ae);"
# Wayland does not apply the vendor's shaped/ignored window input as expected.
# Report idle state through this internal HUD title; Hyprland excludes that
# exact window from hit-testing. Main/login/answer window titles are untouched.
HUD_STATE = r'''const typelessOmarchyHudWindows = new WeakMap();
const typelessOmarchyHudState = (window, positions) => {
  if (process.env.TYPELESS_OMARCHY_ACTIVE !== '1' || !process.env.WAYLAND_DISPLAY ||
      !window || window.isDestroyed()) return;
  const regions = og(positions).filter(r => [r.x,r.y,r.width,r.height].every(Number.isFinite));
  const title = regions.length ? 'Status [' + regions.map(r => [r.x,r.y,r.width,r.height].map(Math.ceil).join(',')).join(';') + ']' : 'Status (idle)';
  if (!typelessOmarchyHudWindows.has(window)) {
    window.on('page-title-updated', event => {
      event.preventDefault();
      const wanted = typelessOmarchyHudWindows.get(window);
      if (window.getTitle() !== wanted) window.setTitle(wanted);
    });
  }
  typelessOmarchyHudWindows.set(window, title);
  if (window.getTitle() !== title) window.setTitle(title);
};
'''
UPDATER_ANCHOR = "['setupIPC'](){const _0x514746=_0x1cd5da;"
UPDATER_POLICY = r'''import {configurePackageUpdates as typelessOmarchyConfigureUpdates} from 'file:///usr/lib/typeless-omarchy/runtime/update-policy.mjs';
const typelessOmarchyShowUpdatePolicy = () => {
  const zh = _0x375e04.getLocale().startsWith('zh');
  return _0x47aeda.showMessageBox({type:'info',title:'Typeless',buttons:[zh?'确定':'OK'],
    message:zh?'Typeless 通过包管理器更新':'Typeless updates are managed through packages',
    detail:zh?'请通过 Omarchy 的 AUR 更新流程更新 typeless-bin，并安装与之匹配的 Typeless-Omarchy。当前兼容层已验证官方 2.2.0 构建；新构建需先完成适配验证。':'Update typeless-bin through the Omarchy AUR workflow and use a matching Typeless-Omarchy release. This compatibility layer validates the official 2.2.0 build; new builds require compatibility validation.'});
};
'''
UPDATER_HOOK = UPDATER_ANCHOR + """if(typelessOmarchyConfigureUpdates({
  ipcMain:_0x11c115,updater:we,controller:this,
  active:process.env.TYPELESS_OMARCHY_ACTIVE === '1',platform:process.platform,
  version:_0x375e04.getVersion(),showPolicy:typelessOmarchyShowUpdatePolicy}))return;"""
SETTINGS_ANCHOR = "const _0x242200=await window['ipcRenderer']['invoke']('updater:check-for-update');"
SETTINGS_HOOK = SETTINGS_ANCHOR + """if(_0x242200?.managedByPackageManager){
  _0x4aed12();await window.ipcRenderer.invoke('typeless-omarchy:show-update-policy');return;
}"""
IPC = "typeless-omarchy:has-input"
MAIN_HOOK = r'''
// Independent Typeless-Omarchy compatibility hook: no text or account data.
import {connect as typelessOmarchyConnect} from 'node:net';
_0x11c115.handle('typeless-omarchy:has-input', () => new Promise(resolve => {
  const runtime = process.env.XDG_RUNTIME_DIR;
  if (!runtime || !runtime.startsWith('/')) { resolve(false); return; }
  let done = false, reply = '';
  const socket = typelessOmarchyConnect(runtime + '/typeless-voice-ime/inject.sock');
  const finish = value => { if (!done) { done = true; socket.destroy(); resolve(value); } };
  socket.setTimeout(250, () => finish(false));
  socket.on('error', () => finish(false));
  socket.on('connect', () => socket.end('{"op":"status"}'));
  socket.on('data', data => { reply += data.toString(); if (reply.length > 64) finish(false); });
  socket.on('end', () => finish(reply === 'FOCUSED_EDITABLE'));
  socket.on('close', () => finish(false));
}));
'''
RESULT_ANCHOR = "if(!_0xebd390)return;const [_0x113491,_0x54fdc2]=await fr()"
RESULT_HOOK = """if(!_0xebd390)return;
if(!await window.ipcRenderer.invoke('typeless-omarchy:has-input')){
  await _0x814f0e(_0x296bb1.userPrompt??'',_0x166d45,_0x296bb1.webMetadata||{},_0xc7ce8);
  return;
}
const [_0x113491,_0x54fdc2]=await fr()"""

def sha(data):
    return hashlib.sha256(data).hexdigest()

class Archive:
    def __init__(self, path):
        self.path = path
        with path.open('rb') as stream:
            prefix = stream.read(16)
            _, header_size, _, json_size = struct.unpack('<4I', prefix)
            self.base = 8 + header_size
            self.header = json.loads(stream.read(json_size))

    def entries(self, node=None, prefix=''):
        node = self.header if node is None else node
        for name, entry in node['files'].items():
            path = prefix + name
            if 'files' in entry:
                yield from self.entries(entry, path + '/')
            elif 'offset' in entry:
                yield path, entry

    def read(self, name):
        entries = dict(self.entries())
        entry = entries[name]
        with self.path.open('rb') as stream:
            stream.seek(self.base + int(entry['offset']))
            return stream.read(entry['size'])

    def write(self, path, changed):
        entries = sorted(self.entries(), key=lambda item: int(item[1]['offset']))
        original = {name: (int(entry['offset']), entry['size']) for name, entry in entries}
        offset = 0
        for name, entry in entries:
            entry['offset'] = str(offset)
            if name in changed:
                data = changed[name]
                entry['size'] = len(data)
                if 'integrity' in entry:
                    block = entry['integrity']['blockSize']
                    entry['integrity'].update(hash=sha(data), blocks=[sha(data[i:i+block]) for i in range(0,len(data),block)])
            offset += entry['size']
        raw = json.dumps(self.header, separators=(',', ':'), ensure_ascii=False).encode()
        payload = struct.pack('<I', len(raw)) + raw
        payload += b'\0' * (-len(payload) % 4)
        pickle = struct.pack('<I', len(payload)) + payload
        with self.path.open('rb') as source, path.open('wb') as target:
            target.write(struct.pack('<2I', 4, len(pickle)) + pickle)
            for name, entry in entries:
                if name in changed:
                    target.write(changed[name])
                    continue
                position, remaining = original[name]
                source.seek(self.base + position)
                while remaining:
                    chunk = source.read(min(remaining, 1024*1024))
                    if not chunk: raise ValueError('Truncated vendor archive')
                    target.write(chunk)
                    remaining -= len(chunk)

def prepare(cache):
    archive = Archive(VENDOR / 'resources/app.asar')
    sources = {name: archive.read(name) for name in EXPECTED}
    for name, digest in EXPECTED.items():
        if sha(sources[name]) != digest:
            raise ValueError('Unsupported Typeless build; runtime compatibility patches were not applied')
    settings = sources[SETTINGS].decode()
    if settings.count(SETTINGS_ANCHOR) != 1:
        raise ValueError('Vendor About update handler changed')
    entry = sources[ENTRY].decode()
    if entry.count(RESULT_ANCHOR) != 1:
        raise ValueError('Vendor completion handler changed')
    startup = sources[STARTUP].decode()
    if startup.count(AUTOSTART_ANCHOR) != 1:
        raise ValueError('Vendor autostart command builder changed')
    main = sources[MAIN].decode()
    if main.count(DESKTOP_ANCHOR) != 1:
        raise ValueError('Vendor desktop cleanup changed')
    if main.count(HUD_POINTER_ANCHOR) != 1:
        raise ValueError('Vendor HUD pointer handler changed')
    if main.count(UPDATER_ANCHOR) != 1:
        raise ValueError('Vendor updater IPC handler changed')
    main = main.replace(HUD_POINTER_ANCHOR, HUD_POINTER_HOOK).replace(UPDATER_ANCHOR, UPDATER_HOOK)
    changed = {SETTINGS: settings.replace(SETTINGS_ANCHOR, SETTINGS_HOOK).encode(), MAIN: (DESKTOP_GUARD + HUD_STATE + UPDATER_POLICY + main.replace(DESKTOP_ANCHOR, DESKTOP_HOOK) + MAIN_HOOK).encode(),
               ENTRY: entry.replace(RESULT_ANCHOR, RESULT_HOOK).encode(),
               STARTUP: (AUTOSTART_ROUTER + startup.replace(AUTOSTART_ANCHOR, AUTOSTART_HOOK)).encode()}
    vendor_stat = (VENDOR / 'typeless').stat()
    archive_stat = archive.path.stat()
    key = sha(Path(__file__).read_bytes() + str((vendor_stat.st_ino, vendor_stat.st_size, vendor_stat.st_mtime_ns,
              archive_stat.st_ino,archive_stat.st_size,archive_stat.st_mtime_ns)).encode())[:24]
    cache.mkdir(parents=True, exist_ok=True, mode=0o700)
    final = cache / key
    if (final / 'ready').exists():
        return final / 'typeless'
    stage = Path(tempfile.mkdtemp(prefix='.prepare-', dir=cache))
    try:
        for child in VENDOR.iterdir():
            if child.name == 'resources': continue
            if child.name == 'typeless':
                # A symlink would resolve /proc/self/exe back to the vendor directory.
                subprocess.run(['cp', '--reflink=auto', str(child), str(stage / child.name)], check=True)
            else:
                (stage / child.name).symlink_to(child)
        resources = stage / 'resources'
        resources.mkdir()
        for child in (VENDOR / 'resources').iterdir():
            if child.name != 'app.asar': (resources / child.name).symlink_to(child)
        archive.write(resources / 'app.asar', changed)
        (stage / 'ready').write_text('Typeless 2.2.0; local compatibility overlay\n')
        try:
            stage.rename(final)
        except OSError:
            if not (final / "ready").exists():
                raise
        return final / 'typeless'
    finally:
        if stage.exists(): shutil.rmtree(stage)

if __name__ == '__main__':
    try:
        cache = Path(sys.argv[1]) if len(sys.argv)>1 else Path(os.environ.get('XDG_CACHE_HOME', Path.home()/'.cache'))/'typeless-omarchy/runtime'
        print(prepare(cache))
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        print('Typeless-Omarchy: '+str(error), file=sys.stderr)
        sys.exit(1)
