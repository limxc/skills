import os
import re
from enum import Enum


class Recommendation(Enum):
    SAFE = "safe"
    CAUTIOUS = "cautious"
    REVIEW = "review"

    @property
    def label(self) -> str:
        return {
            Recommendation.SAFE: "\u2705 safe-to-clean",
            Recommendation.CAUTIOUS: "\u26a0\ufe0f cautious",
            Recommendation.REVIEW: "\U0001F50D review-manually",
        }[self]


_RULES = [
    (re.compile(r"(node_modules|\.npm|\.yarn|\.pnpm|bower_components|jspm_packages)", re.I),
     "dependency-cache", Recommendation.SAFE),
    (re.compile(r"(Temp|tmp|cache)", re.I),
     "temporary-files", Recommendation.SAFE),
    (re.compile(r"(AppData[\\/]Local[\\/](Google|Microsoft[\\/]Edge|Brave|Chromium|Opera))", re.I),
     "browser-cache", Recommendation.SAFE),
    (re.compile(r"(\$Recycle\.Bin|Recycler)", re.I),
     "recycle-bin", Recommendation.SAFE),
    (re.compile(r"(__pycache__|\.pyc|\.pyo)", re.I),
     "code-build", Recommendation.CAUTIOUS),
    (re.compile(r"(bin|obj|\.vs|\.idea)", re.I),
     "code-build", Recommendation.CAUTIOUS),
    (re.compile(r"(dist|build|out|target|\.next|\.nuxt|release)", re.I),
     "code-build", Recommendation.CAUTIOUS),
    (re.compile(r"Logs?", re.I),
     "logs", Recommendation.CAUTIOUS),
    (re.compile(r"(\.git|\.svn|\.hg)", re.I),
     "vcs-data", Recommendation.CAUTIOUS),
    (re.compile(r"Downloads", re.I),
     "downloads", Recommendation.REVIEW),
    (re.compile(r"(Desktop|Documents|Pictures|Music|Videos|OneDrive)", re.I),
     "user-data", Recommendation.REVIEW),
    (re.compile(r"(\.vhd|\.vhdx|\.vmdk|\.ova|wsl)", re.I),
     "virtualization", Recommendation.REVIEW),
]


def _classify_single(path: str) -> tuple:
    for pattern, category, rec in _RULES:
        if pattern.search(path):
            return category, rec
    return ("unknown", Recommendation.REVIEW)


def classify(node) -> None:
    cat, rec = _classify_single(node.path)
    node.category = cat
    node.recommendation = rec
    for child in node.children:
        classify(child)
