"""Audited Typeless 2.2.1 x86_64 patch profile; no vendor modules included."""
MAIN = 'dist/main/index.js'
ENTRY = 'dist/renderer/static/js/BT1_b3hq.mjs'
SETTINGS = 'dist/renderer/static/js/BRBPsUW-.mjs'
EXPECTED = {
    MAIN: 'c72aa54d5afc7608aafef67579b72ac96d86ffe5c76c1237acd732eeaffdbf88',
    ENTRY: 'ba45eb71fd0d440041bc0aa8761a104b5e260308249efef1193de194767b79f7',
    SETTINGS: 'f5093bcfae879545c27ec8b67daebb8704bac5187c7e483bd18abfb053ab6b59',
}
AUTOSTART_ANCHOR = r"Fu=_0x318469=>_0x14f789(0xa09)+ja+'=1\x20\x22'+_0x318469+"
DESKTOP_ANCHOR = '_0x5458ff[_0x1299dd(0x6f7)](_0x51f31b),Zf(_0x3e5f1e);'
HUD_ANCHOR = 'lo=(_0x4c3901,_0x202aaa)=>{const _0x3cc6da=_0x14f789;'
UPDATER_ANCHOR = "['setupIPC'](){const _0x2fef14=_0x14f789;"
SETTINGS_ANCHOR = "const _0x5b79fe=await window['ipcRenderer']['invoke']('updater:check-for-update');"
RESULT_ANCHOR = 'if(!_0x4e0558)return;const [_0x2d4a11,_0x1bb582]=await ur()'
RESULT_HOOK = """if(!_0x4e0558)return;
if(!await window.ipcRenderer.invoke('typeless-omarchy:has-input')){
  await _0x49f861(_0x52d5ad.userPrompt??'',_0x1c7053,_0x52d5ad.webMetadata||{},_0xf39fb3);
  return;
}
const [_0x2d4a11,_0x1bb582]=await ur()"""


def patch(archive, common):
    sources = {name: archive.read(name) for name in EXPECTED}
    for name, digest in EXPECTED.items():
        if common['sha'](sources[name]) != digest:
            raise ValueError('Unsupported Typeless 2.2.1 build: ' + name)

    def once(source, anchor, replacement):
        if source.count(anchor) != 1:
            raise ValueError('Typeless 2.2.1 patch anchor changed: ' + anchor[:55])
        return source.replace(anchor, replacement)

    main, entry, settings = (sources[name].decode() for name in (MAIN, ENTRY, SETTINGS))
    main = once(main, AUTOSTART_ANCHOR, AUTOSTART_ANCHOR.replace(
        '+_0x318469+', '+typelessOmarchyAutostartExecutable(_0x318469)+'))
    main = once(main, DESKTOP_ANCHOR,
        'if(!typelessOmarchyManagedDesktop(_0x3e5f1e)){' + DESKTOP_ANCHOR + '}')
    main = once(main, HUD_ANCHOR,
        HUD_ANCHOR + 'typelessOmarchyHudState(_0x4c3901,_0x202aaa);')
    updater = common['UPDATER_HOOK'][len(common['UPDATER_ANCHOR']):]
    updater = updater.replace('_0x11c115', '_0x1b8a5c').replace('updater:we', 'updater:ve').replace('_0x375e04', '_0x3744fa')
    main = once(main, UPDATER_ANCHOR, UPDATER_ANCHOR + updater)
    policy = common['UPDATER_POLICY'].replace('_0x375e04', '_0x3744fa').replace('_0x47aeda', '_0x3f0c01')
    hud = common['HUD_STATE'].replace('og(positions)', 'Ug(positions)')
    preflight = common['MAIN_HOOK'].replace('_0x11c115', '_0x1b8a5c')
    main = common['AUTOSTART_ROUTER'] + common['DESKTOP_GUARD'] + hud + policy + main + preflight
    entry = once(entry, RESULT_ANCHOR, RESULT_HOOK)
    settings_hook = SETTINGS_ANCHOR + """if(_0x5b79fe?.managedByPackageManager){
  _0x841c83();await window.ipcRenderer.invoke('typeless-omarchy:show-update-policy');return;
}"""
    settings = once(settings, SETTINGS_ANCHOR, settings_hook)
    return {MAIN: main.encode(), ENTRY: entry.encode(), SETTINGS: settings.encode()}
