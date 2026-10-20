import importlib.util
from pathlib import Path
import unittest
root=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('check_vendor',root/'tools/check-vendor.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FeedTest(unittest.TestCase):
    def test_version_metadata(self):
        self.assertEqual(m.feed_version("version: 2.2.1\nfiles:\n  - url: unrelated"),'2.2.1')
        self.assertEqual(m.feed_version("version: '2.2.0'\n"),'2.2.0')
        for text in ['version: invalid','version: 2.2.1\nversion: 2.2.0','version: 2.2.1; arbitrary']:
            with self.assertRaises(ValueError):m.feed_version(text)
if __name__=='__main__':unittest.main()
