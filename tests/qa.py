"""Regression checks for truthful QA status and report data minimization."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

root = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location('qa_runner', root / 'tools/qa.py')
qa = importlib.util.module_from_spec(spec)
spec.loader.exec_module(qa)


class QaReportTest(unittest.TestCase):
    def test_empty_hyprland_config_errors_variants(self):
        for text in ('[]', '[""]', '["  "]'):
            self.assertTrue(qa.clean_config_response(text))
        for text in ('["a real config error"]', '{}', 'null', '[false]'):
            self.assertFalse(qa.clean_config_response(text))

    def test_failure_not_promoted_to_pass_and_no_app_output(self):
        report = qa.Report(['headless'])
        self.assertFalse(report.run('failure', [sys.executable, '-c',
                          'print("PRIVATE-SYNTHETIC-OUTPUT"); raise SystemExit(7)']))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'result.json'
            self.assertEqual(report.save(path), 1)
            data = path.read_text()
            self.assertNotIn('PRIVATE-SYNTHETIC-OUTPUT', data)
            saved = json.loads(data)
            self.assertEqual(saved['automated_status'], 'fail')
            self.assertEqual(saved['release_acceptance'], 'pending_manual')
            self.assertTrue(all(x == 'not_run' for x in saved['manual'].values()))
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)
            with self.assertRaises(FileExistsError):
                report.save(path)

    def test_missing_prerequisite_is_blocked(self):
        report = qa.Report(['desktop'])
        self.assertFalse(report.run('missing', ['/nonexistent/typeless-qa-command']))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'result.json'
            self.assertEqual(report.save(path), 1)
            self.assertEqual(json.loads(path.read_text())['automated_status'], 'blocked')

    def test_success_still_needs_manual_gate(self):
        report = qa.Report(['headless'])
        self.assertTrue(report.run('ok', [sys.executable, '-c', 'pass']))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'result.json'
            self.assertEqual(report.save(path), 0)
            saved = json.loads(path.read_text())
            self.assertEqual(saved['automated_status'], 'pass')
            self.assertEqual(saved['release_acceptance'], 'pending_manual')


if __name__ == '__main__':
    unittest.main()
