import unittest
from unittest.mock import MagicMock, patch

from scripts.categorizer import classify, Recommendation


def make_node(path: str, children=None):
    node = MagicMock()
    node.path = path
    node.children = children or []
    return node


class TestCategorizer(unittest.TestCase):

    def _categorize(self, path: str):
        node = make_node(path)
        classify(node)
        return node.category, node.recommendation

    def test_dependency_cache(self):
        cat, rec = self._categorize(r"C:\project\node_modules")
        self.assertEqual(cat, "dependency-cache")
        self.assertEqual(rec, Recommendation.SAFE)

    def test_temporary_files(self):
        cat, rec = self._categorize(r"C:\Users\Test\AppData\Local\Temp")
        self.assertEqual(cat, "temporary-files")
        self.assertEqual(rec, Recommendation.SAFE)

    def test_browser_cache(self):
        cat, rec = self._categorize(
            r"C:\Users\Test\AppData\Local\Google\Chrome\User Data\Default\Cache")
        self.assertEqual(cat, "temporary-files")
        self.assertEqual(rec, Recommendation.SAFE)

    def test_code_build_bin_obj(self):
        cat, rec = self._categorize(r"C:\project\bin")
        self.assertEqual(cat, "code-build")
        self.assertEqual(rec, Recommendation.CAUTIOUS)

    def test_logs(self):
        cat, rec = self._categorize(r"C:\app\Logs")
        self.assertEqual(cat, "logs")
        self.assertEqual(rec, Recommendation.CAUTIOUS)

    def test_vcs_data(self):
        cat, rec = self._categorize(r"C:\repo\.git")
        self.assertEqual(cat, "vcs-data")
        self.assertEqual(rec, Recommendation.CAUTIOUS)

    def test_downloads(self):
        cat, rec = self._categorize(r"C:\Users\Test\Downloads")
        self.assertEqual(cat, "downloads")
        self.assertEqual(rec, Recommendation.REVIEW)

    def test_user_data(self):
        cat, rec = self._categorize(r"C:\Users\Test\Documents")
        self.assertEqual(cat, "user-data")
        self.assertEqual(rec, Recommendation.REVIEW)

    def test_unknown_fallback(self):
        cat, rec = self._categorize(r"D:\SomeRandom\MyStuff")
        self.assertEqual(cat, "unknown")
        self.assertEqual(rec, Recommendation.REVIEW)

    def test_classify_recursive(self):
        child1 = make_node(r"C:\root\node_modules")
        child2 = make_node(r"C:\root\Downloads")
        root = make_node(r"C:\root", children=[child1, child2])
        classify(root)
        self.assertEqual(child1.category, "dependency-cache")
        self.assertEqual(child1.recommendation, Recommendation.SAFE)
        self.assertEqual(child2.category, "downloads")
        self.assertEqual(child2.recommendation, Recommendation.REVIEW)

    def test_recommendation_label_safe(self):
        self.assertIn("safe-to-clean", Recommendation.SAFE.label)

    def test_recommendation_label_cautious(self):
        self.assertIn("cautious", Recommendation.CAUTIOUS.label)

    def test_recommendation_label_review(self):
        self.assertIn("review-manually", Recommendation.REVIEW.label)

    def test_virtualization(self):
        cat, rec = self._categorize(r"D:\VMs\ubuntu.vhdx")
        self.assertEqual(cat, "virtualization")
        self.assertEqual(rec, Recommendation.REVIEW)

    def test_case_insensitive_temp(self):
        cat, rec = self._categorize(r"C:\USERS\TEST\TEMP")
        self.assertEqual(cat, "temporary-files")

    def test_pycache(self):
        cat, rec = self._categorize(r"C:\project\src\__pycache__")
        self.assertEqual(cat, "temporary-files")
        self.assertEqual(rec, Recommendation.SAFE)

    def test_dist_folder(self):
        cat, rec = self._categorize(r"C:\project\dist")
        self.assertEqual(cat, "code-build")
        self.assertEqual(rec, Recommendation.CAUTIOUS)
