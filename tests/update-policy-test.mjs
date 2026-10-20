import assert from 'node:assert/strict';
import { configurePackageUpdates } from '../runtime/update-policy.mjs';

function fixture(overrides = {}) {
  const handlers = new Map();
  let dialogs = 0, dangerous = 0;
  const dangerousCall = () => { dangerous++; throw new Error('vendor updater must not run'); };
  const state = {
    ipcMain: { handle(name, fn) { assert(!handlers.has(name)); handlers.set(name, fn); } },
    updater: { autoDownload: true, autoInstallOnAppQuit: true,
      checkForUpdates: dangerousCall, downloadUpdate: dangerousCall, quitAndInstall: dangerousCall },
    controller: { updateStatus: 'downloaded', updateInfo: { downloadedFile: '/fixture/pending.deb' },
      latestVersion: '99.0.0', error: 'stale' },
    active: true, platform: 'linux', version: '2.2.0',
    showPolicy: async () => { dialogs++; }, ...overrides,
  };
  return { state, handlers, get dialogs() { return dialogs; }, get dangerous() { return dangerous; } };
}

for (const overrides of [{ active: false }, { platform: 'darwin' }]) {
  const f = fixture(overrides);
  assert.equal(configurePackageUpdates(f.state), false);
  assert.equal(f.handlers.size, 0);
  assert.equal(f.state.updater.autoDownload, true);
  assert.equal(f.state.controller.updateStatus, 'downloaded');
}
const f = fixture();
assert.equal(configurePackageUpdates(f.state), true);
assert.equal(f.state.updater.autoDownload, false);
assert.equal(f.state.updater.autoInstallOnAppQuit, false);
assert.equal(f.state.controller.updateInfo, null);
assert.equal(f.state.controller.latestVersion, null);
assert.equal(f.state.controller.updateStatus, 'managed');
for (let i = 0; i < 30; i++) {
  assert.equal(await f.handlers.get('updater:check-update-and-download-silently')(), null);
}
assert.equal(f.dialogs, 0);
const info = await f.handlers.get('updater:check-for-update')();
assert.deepEqual(info, { managedByPackageManager: true, currentVersion: '2.2.0' });
assert.equal(info.version, undefined); // Never claim the installed version is latest.
assert.equal(info.downloadedFile, undefined);
assert.equal(f.dialogs, 0); // Shared version diagnostic must not interrupt onboarding.
for (const channel of ['updater:download-update', 'updater:quit-and-install', 'typeless-omarchy:show-update-policy']) {
  assert.deepEqual(await f.handlers.get(channel)(), info);
}
assert.equal(f.dialogs, 3);
assert.equal(f.dangerous, 0);
assert.equal(f.handlers.size, 5);
let closeDialog;
const coalesced = fixture({ showPolicy: () => new Promise(resolve => { closeDialog = resolve; }) });
configurePackageUpdates(coalesced.state);
const a = coalesced.handlers.get('updater:quit-and-install')();
const b = coalesced.handlers.get('updater:download-update')();
await Promise.resolve();
assert.equal(typeof closeDialog, 'function');
closeDialog();
assert.deepEqual(await a, await b);
console.log('PASS package-managed update routes, pending cache, quiet polling, diagnostic isolation and coalesced dialog');
