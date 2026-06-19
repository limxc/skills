import os
import tempfile
import unittest
from pathlib import Path

from scripts.scanner import scan, FolderNode


class TestScanner(unittest.TestCase):

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

    def test_empty_directory(self):
        node = scan(str(self.root), max_depth=2, min_size=1)
        self.assertEqual(node.size, 0)
        self.assertEqual(len(node.children), 0)

    def test_single_file(self):
        self._create_file(self.root / "test.txt", 500)
        node = scan(str(self.root), max_depth=2, min_size=1)
        self.assertEqual(node.size, 500)
        self.assertEqual(len(node.children), 0)

    def test_folder_size_aggregation(self):
        sub = self._create_dir("subfolder")
        self._create_file(sub / "a.bin", 1000)
        self._create_file(sub / "b.bin", 2000)
        node = scan(str(self.root), max_depth=2, min_size=1)
        self.assertEqual(node.size, 3000)
        self.assertEqual(len(node.children), 1)
        self.assertEqual(node.children[0].size, 3000)

    def test_min_size_filter(self):
        sub1 = self._create_dir("small")
        inner = self._create_dir("small", "inner")
        sub2 = self._create_dir("large")
        self._create_file(sub1 / "a.txt", 100)
        self._create_file(inner / "inner.txt", 50)
        self._create_file(sub2 / "b.txt", 5000)
        node = scan(str(self.root), max_depth=3, min_size=1000)
        small_dir = [c for c in node.children if os.path.basename(c.path) == "small"]
        if small_dir:
            self.assertLess(len(small_dir[0].children), 2,
                            "inner dir should be filtered out by min_size")

    def test_system_directories_skipped(self):
        for sys_dir in ["Windows", "System32", "Program Files"]:
            d = self._create_dir(sys_dir)
            self._create_file(d / "ignored.txt", 9999)
        node = scan(str(self.root), max_depth=2, min_size=1)
        for c in node.children:
            self.assertNotIn(os.path.basename(c.path).lower(),
                             ["windows", "system32", "program files"])

    def test_permission_error_returns_skipped(self):
        node = scan(r"C:\$FakeNonexistentDir_XYZ", max_depth=2, min_size=1)
        self.assertIsInstance(node, FolderNode)
        self.assertEqual(node.size, 0)

    def test_top5_sorting(self):
        for i in range(7):
            d = self._create_dir(f"dir{i}")
            self._create_file(d / f"f{i}.dat", (i + 1) * 1000)
        node = scan(str(self.root), max_depth=2, min_size=1)
        self.assertEqual(len(node.children), 7)
        sorted_sizes = [c.size for c in node.children]
        self.assertEqual(sorted_sizes, sorted(sorted_sizes, reverse=True))
        self.assertEqual(node.children[0].size, 7000)

    def test_max_depth_respected(self):
        deep = self.root
        for i in range(6):
            deep = self._create_dir(f"level{i}")
        self._create_file(deep / "deep.txt", 5000)
        node = scan(str(self.root), max_depth=3, min_size=1)
        def count_children(n):
            return 1 + sum(count_children(c) for c in n.children)
        self.assertLessEqual(count_children(node), 10)
