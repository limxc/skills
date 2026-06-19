import os
import time

_SYSTEM_DIRS = frozenset({
    "windows", "program files", "program files (x86)",
    "system32", "$recycle.bin", "system volume information",
    "recovery", "perflogs",
})

class FolderNode:
    __slots__ = ("path", "size", "children", "skipped", "category", "recommendation")

    def __init__(self, path: str, size: int = 0, children=None, skipped=None):
        self.path = path
        self.size = size
        self.children = children or []
        self.skipped = skipped or []

    def __repr__(self):
        return f"FolderNode({self.path}, size={self.size})"


def _is_system_dir(name: str) -> bool:
    return name.lower() in _SYSTEM_DIRS


def scan(
    root: str,
    max_depth: int = 5,
    min_size: int = 1_000_000_000,
    progress=None,
    _depth: int = 0,
    _deadline: float = 0,
) -> FolderNode:
    node = FolderNode(root)

    if _deadline and time.time() > _deadline:
        return node

    try:
        entries = list(os.scandir(root))
    except PermissionError:
        node.skipped = [root]
        return node
    except FileNotFoundError:
        node.skipped = [root]
        return node

    total = 0
    children = []
    skipped = []

    for entry in entries:
        try:
            is_dir = entry.is_dir(follow_symlinks=False)
            is_file = entry.is_file(follow_symlinks=False)
        except PermissionError:
            skipped.append(entry.path)
            continue
        except OSError:
            skipped.append(entry.path)
            continue

        if is_dir:
            name = entry.name
            if _is_system_dir(name):
                continue

            if _depth < max_depth:
                sub = scan(
                    entry.path,
                    max_depth,
                    min_size,
                    progress,
                    _depth + 1,
                    _deadline,
                )
                if sub.size >= min_size or _depth == 0:
                    children.append(sub)
                total += sub.size
            else:
                sub = FolderNode(entry.path)
                total += _dir_size(entry.path)
                children.append(sub)
        elif is_file:
            try:
                total += entry.stat(follow_symlinks=False).st_size
            except (PermissionError, OSError):
                pass

    if progress and _depth == 0:
        for c in children:
            if c.size >= min_size:
                progress(c.path, c.size)

    node.size = total
    node.children = sorted(children, key=lambda x: x.size, reverse=True)
    node.skipped = skipped
    return node


def _dir_size(path: str) -> int:
    try:
        with os.scandir(path) as entries:
            total = 0
            for entry in entries:
                try:
                    if entry.is_dir(follow_symlinks=False):
                        total += _dir_size(entry.path)
                    elif entry.is_file(follow_symlinks=False):
                        total += entry.stat(follow_symlinks=False).st_size
                except (PermissionError, OSError):
                    pass
            return total
    except (PermissionError, FileNotFoundError, OSError):
        return 0
