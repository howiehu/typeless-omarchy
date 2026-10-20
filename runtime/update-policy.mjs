// Original package-managed update policy. No downloads, installers or shell calls.
export function configurePackageUpdates({ ipcMain, updater, controller, active,
  platform, version, showPolicy }) {
  if (!active || platform !== 'linux') return false;

  updater.autoDownload = false;
  updater.autoInstallOnAppQuit = false;
  controller.updateStatus = 'managed';
  controller.updateInfo = null;
  controller.latestVersion = null;
  controller.error = null;

  const info = Object.freeze({ managedByPackageManager: true, currentVersion: version });
  let showing;
  const explain = async () => {
    if (!showing) showing = Promise.resolve().then(showPolicy).finally(() => { showing = undefined; });
    await showing;
    return info;
  };
  // The version diagnostic shares check-for-update with About. Return an explicit
  // managed result; only About asks to display the explanation, never onboarding.
  ipcMain.handle('updater:check-for-update', async () => info);
  ipcMain.handle('updater:check-update-and-download-silently', async () => null);
  ipcMain.handle('updater:download-update', explain);
  ipcMain.handle('updater:quit-and-install', explain);
  ipcMain.handle('typeless-omarchy:show-update-policy', explain);
  return true;
}
