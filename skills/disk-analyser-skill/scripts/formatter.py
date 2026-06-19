import os


def format_size(size: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} PB"


def _format_node(node, is_last: bool = True, prefix: str = "", top_n: set = None) -> list:
    lines = []
    connector = "\u2514\u2500\u2500 " if is_last else "\u251c\u2500\u2500 "
    indent = "    " if is_last else "\u2502   "

    name = os.path.basename(node.path) or node.path
    size_str = format_size(node.size)

    if hasattr(node, "category"):
        category = node.category
        rec = node.recommendation.label if hasattr(node, "recommendation") else ""
    else:
        category = ""
        rec = ""

    top_mark = ""
    if top_n is not None and id(node) in top_n:
        top_mark = "  [TOP]"

    if node.skipped:
        line = f"{prefix}{connector}{name}  skipped  (permission denied)"
    else:
        line = f"{prefix}{connector}{name}  {size_str:>10}  {category:<20} {rec}{top_mark}"

    lines.append(line)

    if node.children:
        for i, child in enumerate(node.children):
            is_last_child = i == len(node.children) - 1
            child_prefix = prefix + indent
            lines.extend(_format_node(
                child, is_last_child, child_prefix, top_n
            ))

    return lines


def format_report(root, duration: float) -> str:
    skipped_count = len(root.skipped)
    top_n = _get_top_folders(root, 5)

    total_size_str = format_size(root.size)
    skipped_str = f" | Skipped: {skipped_count} paths" if skipped_count else ""

    header = (
        f"Scanned: {root.path} | Total: {total_size_str}"
        f"{skipped_str} | Duration: {duration:.1f}s"
    )
    sep = "\u2500" * len(header)

    lines = [header, sep]
    for i, child in enumerate(root.children):
        is_last = i == len(root.children) - 1
        lines.extend(_format_node(child, is_last, "", top_n))

    return "\n".join(lines)


def _get_top_folders(node, n: int = 5) -> set:
    sorted_children = sorted(node.children, key=lambda x: x.size, reverse=True)
    return {id(c) for c in sorted_children[:n]}
