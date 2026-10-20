"""Profile guards and patch placement with small synthetic vendor fixtures."""
import importlib.util
from pathlib import Path
import unittest
root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('prepare',root/'runtime/prepare.py')
m = importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
p = m.build221_profile()
class ProfileTest(unittest.TestCase):
    def test_guarded_221_profile_and_changed_anchor_refusal(self):
        sources={p.MAIN:(' '.join([p.AUTOSTART_ANCHOR,p.DESKTOP_ANCHOR,p.HUD_ANCHOR,p.UPDATER_ANCHOR])).encode(),
                 p.ENTRY:p.RESULT_ANCHOR.encode(),p.SETTINGS:p.SETTINGS_ANCHOR.encode()}
        class Archive:
            def read(self,name):return sources[name]
            def entries(self):return ((name,{}) for name in sources)
        previous=p.EXPECTED
        try:
            p.EXPECTED={name:m.sha(value) for name,value in sources.items()}
            patched=p.patch(Archive(),vars(m))
            self.assertEqual(set(patched),set(sources))
            self.assertIn(b'typelessOmarchyAutostartExecutable(_0x318469)',patched[p.MAIN])
            self.assertIn(b'typelessOmarchyManagedDesktop(_0x3e5f1e)',patched[p.MAIN])
            self.assertIn(b'Ug(positions)',patched[p.MAIN])
            self.assertIn(b'updater:ve',patched[p.MAIN])
            self.assertIn(b"_0x1b8a5c.handle('typeless-omarchy:has-input'",patched[p.MAIN])
            self.assertIn(b'_0x841c83()',patched[p.SETTINGS])
            self.assertIn(p.RESULT_HOOK.encode(),patched[p.ENTRY])
            sources[p.ENTRY]+=b'changed'
            with self.assertRaisesRegex(ValueError,'Unsupported Typeless 2.2.1'):
                p.patch(Archive(),vars(m))
            p.EXPECTED[p.ENTRY]=m.sha(sources[p.ENTRY])
            sources[p.MAIN]=sources[p.MAIN].replace(p.HUD_ANCHOR.encode(),b'changed')
            p.EXPECTED[p.MAIN]=m.sha(sources[p.MAIN])
            with self.assertRaisesRegex(ValueError,'patch anchor changed'):
                p.patch(Archive(),vars(m))
        finally:p.EXPECTED=previous
if __name__=='__main__':unittest.main()
