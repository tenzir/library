"""Run with `python3 -I -m unittest` semantics: python3 -I test_check.py"""

import importlib.util
import pathlib
import tempfile
import types
import unittest

SPEC = importlib.util.spec_from_file_location("check", pathlib.Path(__file__).with_name("check.py"))
check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(check)


def kinds(line, internal=()):
    return {kind for kind, _ in check.findings(line, internal)}


class Privacy(unittest.TestCase):
    def test_clean(self):
        for line in ("10.20.1.11 -> 192.0.2.10 www.shop.example ada@office.example",
                     "S-1-5-21-1111111111-2222222222-3333333333-1001 02:00:0a:14:01:0b",
                     "OS build 10.0.26100.32131 at DEMO-WIN-01.example.test",
                     "user@example.invalid 2026-01-01T10:00:00Z"):
            self.assertEqual(kinds(line), set(), line)

    def test_findings(self):
        for line, kind in (("from 8.8.8.8 port 53", "public IPv4 address"),
                           ("mail to someone@gmail.com", "mail address"),
                           ("GET http://tenzir.com/x", "host name"),
                           ("S-1-5-21-1757393335-992402403-2468010962-500", "security identifier"),
                           ("00:1b:44:11:3a:b7", "vendor MAC address"),
                           ("fe80::a57f:d003:b903:74c5", "link-local IPv6 address"),
                           ("password=hunter2hunter2", "secret"),
                           ("AKIA" + "A" * 16, "secret")):
            self.assertIn(kind, kinds(line), line)
        self.assertIn("internal name", kinds("C:/Users/LAB-DC", ["lab-dc"]))


class Replay(unittest.TestCase):
    def run_replay(self, *lines):
        with tempfile.NamedTemporaryFile("w", suffix=".ndjson") as handle:
            handle.write("\n".join(lines) + "\n")
            handle.flush()
            return check.replay(types.SimpleNamespace(
                file=handle.name, start="2026-11-25T12:00:00Z", stable=None, epochs=False, show=False))

    ID = "12345678-1234-4234-8234-1234567890a"

    def test_clean(self):
        self.assertFalse(self.run_replay(f"2026-11-25T12:00:00Z {self.ID}b", f"2026-11-25T12:01:00Z {self.ID}c"))

    def test_stale_date(self):
        self.assertTrue(self.run_replay("2026-08-27T12:00:00Z", "2026-08-27T12:00:00Z"))

    def test_epoch(self):
        self.assertTrue(self.run_replay("t=1793696949", "t=1793696949"))

    def test_equal_ids(self):
        self.assertTrue(self.run_replay(f"{self.ID}b", f"{self.ID}b"))

    def test_odd_records(self):
        self.assertTrue(self.run_replay("2026-11-25T12:00:00Z"))

    def test_unrendered(self):
        self.assertTrue(self.run_replay("\u001etime|", "\u001etime|"))


if __name__ == "__main__":
    unittest.main()
