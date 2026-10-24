"""The callable-table API used by source scanners must not hang config loading."""
from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent


class ConfigScanTest(unittest.TestCase):
    def test_callable_proxy_scan_finishes_without_runtime_operations(self):
        # Match the scanner's proxy semantics, rather than an ordinary empty list.
        # Every numeric lookup returns the proxy: ipairs cannot terminate on it.
        chunk = '''
local calls = 0
local noop
noop = setmetatable({}, {
  __index = function() return noop end,
  __call = function() calls = calls + 1; return noop end,
})
hl = setmetatable({}, { __index = function() return noop end })
o = { window = function() calls = calls + 1 end }
dofile(arg[1])
assert(calls == 0, "source scan executed compositor runtime operations")
print("SCAN_COMPLETED")
'''
        result = subprocess.run(['lua', '-', str(ROOT / 'data/typeless.lua')],
                                input=chunk, text=True, capture_output=True, timeout=2)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), 'SCAN_COMPLETED')


if __name__ == '__main__':
    unittest.main()
