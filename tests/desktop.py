#!/usr/bin/python
"""Exercise setup/repair/removal on an isolated user profile, without a desktop."""
import base64
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest

root = Path(__file__).resolve().parent.parent
loader = importlib.machinery.SourceFileLoader('setup_integration', str(root/'bin/typeless-omarchy-setup'))
spec = importlib.util.spec_from_loader(loader.name, loader)
m = importlib.util.module_from_spec(spec)
loader.exec_module(m)
MENU = '[Desktop Entry]\nName=Typeless-Omarchy\nExec=/usr/bin/typeless-omarchy %U\n'
AUTO = ('[Desktop Entry]\nExec=env TYPELESS_SKIP_SECRET_STORE=1 "/opt/Typeless/typeless" '
        '--system-startup-silent-launch --password-store=basic\nHidden=false\n')

class DesktopTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        m.home = Path(self.temp.name)
        m.desktop = m.home/'applications/typeless-omarchy.desktop'
        m.legacy = m.home/'applications/typeless.desktop'
        m.autostart = m.home/'config/autostart/typeless.desktop'
        m.desktop.parent.mkdir(parents=True)
        m.autostart.parent.mkdir(parents=True)

    def test_menu_survives_vendor_deleting_legacy_entry(self):
        m.legacy.write_text('vendor entry')
        record = {}
        m.install_menu(record, MENU)
        m.legacy.unlink()  # The vendor's observed startup cleanup.
        self.assertEqual(m.desktop.read_text(), MENU)
        m.install_menu(record, MENU)
        m.remove_integration(record)
        self.assertFalse(m.desktop.exists())
        self.assertFalse(m.autostart.exists())  # Never enable an absent autostart.

    def test_migrates_v1_and_preserves_original_backup(self):
        original = b'prior user desktop entry'
        record = {'desktop_installed': MENU,
                  'desktop_before': base64.b64encode(original).decode()}
        m.legacy.write_text(MENU)
        m.install_menu(record, MENU)
        self.assertFalse(m.legacy.exists())
        m.remove_integration(record)
        self.assertEqual(m.legacy.read_bytes(), original)
        self.assertFalse(m.desktop.exists())

    def test_missing_v1_entry_can_be_repaired(self):
        record = {'desktop_installed': MENU, 'desktop_before': None}
        m.install_menu(record, MENU)
        self.assertEqual(m.desktop.read_text(), MENU)
        m.remove_integration(record)
        self.assertFalse(m.legacy.exists())

    def test_repair_preserves_enabled_and_disabled_autostart(self):
        for hidden in ('false', 'true'):
            with self.subTest(hidden=hidden):
                original = AUTO.replace('Hidden=false', 'Hidden='+hidden)
                m.autostart.write_text(original)
                record = {}
                m.repair_autostart(record)
                self.assertIn('/usr/bin/typeless-omarchy --system-startup-silent-launch --password-store=basic',
                              m.autostart.read_text())
                self.assertIn('Hidden='+hidden, m.autostart.read_text())
                m.repair_autostart(record)
                m.remove_integration(record)
                self.assertEqual(m.autostart.read_text(), original)

    def test_vendor_toggle_after_setup_is_not_rolled_back(self):
        m.autostart.write_text(AUTO)
        record = {}
        m.install_menu(record, MENU)
        changed = m.autostart.read_text().replace('Hidden=false', 'Hidden=true')
        m.autostart.write_text(changed)
        m.remove_integration(record)
        self.assertIn('Hidden=true', m.autostart.read_text())
        self.assertNotIn('/usr/bin/typeless-omarchy', m.autostart.read_text())

    def test_autostart_created_after_setup_is_routed_back_on_removal(self):
        record = {}
        m.install_menu(record, MENU)
        m.autostart.write_text(AUTO.replace('/opt/Typeless/typeless', '/usr/bin/typeless-omarchy'))
        m.remove_integration(record)
        self.assertEqual(m.autostart.read_text(), AUTO)

    def test_adopts_matching_manual_menu_without_leaving_it_after_removal(self):
        m.desktop.write_text(MENU)
        record = {}
        m.install_menu(record, MENU)
        m.remove_integration(record)
        self.assertFalse(m.desktop.exists())

    def test_user_edited_menu_refuses_removal_before_changing_files(self):
        record = {}
        m.install_menu(record, MENU)
        m.desktop.write_text('user menu')
        with self.assertRaisesRegex(SystemExit, 'changed'):
            m.remove_integration(record)
        self.assertEqual(m.desktop.read_text(), 'user menu')

    def test_user_autostart_command_is_not_overwritten(self):
        custom = AUTO.replace('/opt/Typeless/typeless', '/custom/launcher')
        m.autostart.write_text(custom)
        m.install_menu({}, MENU)
        self.assertEqual(m.autostart.read_text(), custom)

    def test_user_legacy_entry_is_preserved_during_repair(self):
        m.legacy.write_text('user legacy edit')
        record = {'desktop_installed': MENU, 'desktop_before': None}
        m.install_menu(record, MENU)
        self.assertEqual(m.legacy.read_text(), 'user legacy edit')
        with self.assertRaisesRegex(SystemExit, 'Legacy desktop entry changed'):
            m.remove_integration(record)
        self.assertEqual(m.desktop.read_text(), MENU)

if __name__ == '__main__':
    unittest.main()
