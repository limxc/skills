import os
import tempfile
import unittest
from pathlib import Path

from scripts.scanner import scan, FolderNode
from scripts.formatter import format_report, format_size, _get_top_folders


class TestFormatter(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _create_file(self, path: Path, size: int):
        path.write_bytes(b"x" * size)

    def _create_dir(self, *parts):
        d = self.root.joinpath(*parts)
        d.mkdir(parents=True, exist_ok=True)
        return d

    def test_format_size_bytes(self):
        self.assertEqual(format_size(500), "500.00 B")

    def test_format_size_kb(self):
        self.assertEqual(format_size(2048), "2.00 KB")

    def test_format_size_mb(self):
        self.assertEqual(format_size(1048576), "1.00 MB")

    def test_format_size_gb(self):
        self.assertEqual(format_size(1073741824), "1.00 GB")

    def test_format_size_tb(self):
        self.assertEqual(format_size(1099511627776), "1.00 TB")

    def test_format_size_zero(self):
        self.assertEqual(format_size(0), "0.00 B")

    def test_get_top_folders_returns_top_5(self):
        node = FolderNode("/root")
        for i in range(7):
            child = FolderNode(f"/root/folder{i}", size=(i + 1) * 1000)
            node.children.append(child)
        top = _get_top_folders(node, 5)
        self.assertEqual(len(top), 5)
        top_ids = {id(c) for c in sorted(
            node.children, key=lambda x: x.size, reverse=True)[:5]}
        self.assertEqual(top, top_ids)

    def test_get_top_folders_less_than_5(self):
        node = FolderNode("/root")
        for i in range(3):
            child = FolderNode(f"/root/folder{i}", size=1000)
            node.children.append(child)
        top = _get_top_folders(node, 5)
        self.assertEqual(len(top), 3)

    def test_get_top_folders_empty(self):
        node = FolderNode("/root")
        top = _get_top_folders(node, 5)
        self.assertEqual(len(top), 0)

    def test_report_contains_scanned_header(self):
        for i in range(6):
            d = self._create_dir(f"dir{i}")
            self._create_file(d / f"f{i}.dat", (i + 1) * 1000)
        node = scan(str(self.root), max_depth=2, min_size=1)
        report = format_report(node, 1.5)
        self.assertIn("Scanned:", report)

    def test_report_contains_top_markers(self):
        for i in range(6):
            d = self._create_dir(f"dir{i}")
            self._create_file(d / f"f{i}.dat", (6 - i) * 1000)
        node = scan(str(self.root), max_depth=2, min_size=1)
        report = format_report(node, 0.5)
        top5_count = report.count("[TOP]")
        self.assertLessEqual(top5_count, 5)

    def test_report_top5_sizes_correct(self):
        expected_sizes = {}
        for i in range(6):
            d = self._create_dir(f"dir{i}")
            size = (6 - i) * 1000
            self._create_file(d / f"f{i}.dat", size)
            expected_sizes[f"dir{i}"] = size
        node = scan(str(self.root), max_depth=2, min_size=1)
        report = format_report(node, 0.5)
        sorted_items = sorted(
            expected_sizes.items(), key=lambda x: x[1], reverse=True)
        for name, expected_size in sorted_items[:5]:
            size_str = format_size(expected_size)
            self.assertIn(size_str, report,
                          f"Expected {name} size {size_str} not in report")
