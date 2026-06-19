import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


INTEGRATION_MARKER = "__INTEGRATION_TEST__"

_SKILL_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))

_ENV = {**os.environ, "PYTHONIOENCODING": "utf-8"}


def _run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", cwd=_SKILL_ROOT, env=_ENV)


class TestIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp_dir.name)
        expected = {}
        for i in range(6):
            d = cls.root / f"dir{i}"
            d.mkdir(parents=True, exist_ok=True)
            size = (6 - i) * 1000
            (d / f"f{i}.dat").write_bytes(b"x" * size)
            expected[f"dir{i}"] = size
        cls.expected = expected
        cls.root_path = str(cls.root)

    @classmethod
    def tearDownClass(cls):
        cls.temp_dir.cleanup()

    def test_command_line_invocation(self):
        result = _run([sys.executable, "-m", "scripts", self.root_path,
                       "--min-size", "1", "--max-depth", "2"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Scanned:", result.stdout)
        self.assertIn("Total:", result.stdout)
        self.assertIn("Duration:", result.stdout)

    def test_top5_sizes_match_expected(self):
        result = _run([sys.executable, "-m", "scripts", self.root_path,
                       "--min-size", "1", "--max-depth", "2"])
        sorted_items = sorted(
            self.expected.items(), key=lambda x: x[1], reverse=True)
        from scripts.formatter import format_size
        for name, size in sorted_items[:5]:
            size_str = format_size(size)
            self.assertIn(size_str, result.stdout,
                          f"TOP5 folder {name} size {size_str} not found")

    def test_command_with_empty_dir(self):
        with tempfile.TemporaryDirectory() as empty:
            result = _run([sys.executable, "-m", "scripts", empty,
                           "--min-size", "1", "--max-depth", "2"])
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertIn("Total:", result.stdout)

    def test_command_with_nonexistent_path(self):
        result = _run([sys.executable, "-m", "scripts",
                        r"C:\NONEXISTENT_PATH_FOR_TEST_XYZ",
                        "--min-size", "1", "--max-depth", "2"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_permission_denied_handling(self):
        result = _run([sys.executable, "-m", "scripts", self.root_path,
                       "--min-size", "1", "--max-depth", "5"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_min_size_filter_on_command_line(self):
        with tempfile.TemporaryDirectory() as td:
            td_root = Path(td)
            outer = td_root / "outer"
            outer.mkdir()
            big_dir = outer / "big"
            big_dir.mkdir()
            (big_dir / "big.dat").write_bytes(b"x" * 10000)
            small_dir = outer / "small"
            small_dir.mkdir()
            (small_dir / "small.dat").write_bytes(b"x" * 50)
            result = _run([sys.executable, "-m", "scripts", td,
                           "--min-size", "5000", "--max-depth", "3"])
            self.assertNotIn("small", result.stdout,
                             "min_size filter failed for nested dirs")

    def test_timeout_parameter(self):
        result = _run([sys.executable, "-m", "scripts", self.root_path,
                       "--min-size", "1", "--max-depth", "2", "--timeout", "30"])
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Scanned:", result.stdout)
