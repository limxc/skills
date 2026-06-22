#!/usr/bin/env python3
"""Shared utilities for spec2readme scripts."""

import os
from pathlib import Path


def find_project_root(env_var: str = "SPEC2README_PROJECT_ROOT") -> Path:
    """Locate the project root directory.

    Priority:
    1. Environment variable override (if set and points to a directory).
    2. Walk upward from cwd looking for openspec/, .git/, or AGENTS.md.
    3. Fall back to current working directory.
    """
    env_root = os.environ.get(env_var)
    if env_root:
        path = Path(env_root)
        if path.is_dir():
            return path.resolve()

    cwd = Path.cwd().resolve()
    for parent in [cwd, *cwd.parents]:
        if (
            (parent / "openspec").is_dir()
            or (parent / ".git").is_dir()
            or (parent / "AGENTS.md").is_file()
        ):
            return parent
    return cwd


def resolve_change_path(change_arg: str, project_root: Path) -> Path:
    """Resolve a change directory path or directory name to an existing directory.

    If ``change_arg`` is already a directory path, return it resolved.
    Otherwise look for it under ``openspec/changes/`` and
    ``openspec/changes/archive/`` relative to ``project_root``.
    """
    change_path = Path(change_arg)
    if change_path.is_dir():
        return change_path.resolve()

    candidates = [
        project_root / "openspec" / "changes" / change_arg,
        project_root / "openspec" / "changes" / "archive" / change_arg,
    ]
    for cand in candidates:
        if cand.is_dir():
            return cand.resolve()
    return change_path
