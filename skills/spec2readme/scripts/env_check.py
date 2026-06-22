#!/usr/bin/env python3
"""Cross-platform environment check for the spec2readme skill.

Checks:
- creating-mermaid-diagrams skill installation
- mmdc CLI availability
- Puppeteer / Chrome headless shell availability (auto-installs if missing)

Exit codes:
    0  ready
    1  critical dependency missing (creating-mermaid-diagrams or mmdc)
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path


def skill_home() -> Path:
    """Return the user-level skills directory."""
    home = Path.home()
    return home / ".agents" / "skills"


def _run_npx(cmd: list[str], **kwargs):
    """Run an npx command.

    On Windows, npx is a .cmd wrapper and must be run through the shell.
    On Unix-like systems, npx can be invoked directly.
    """
    if sys.platform == "win32":
        return subprocess.run(" ".join(cmd), shell=True, **kwargs)
    return subprocess.run(cmd, **kwargs)


def check_creating_mermaid_diagrams() -> bool:
    return (skill_home() / "creating-mermaid-diagrams" / "SKILL.md").is_file()


def check_npx() -> bool:
    return shutil.which("npx") is not None


def check_mmdc() -> bool:
    """Check for mmdc in PATH or available via npx."""
    if shutil.which("mmdc"):
        return True
    if not check_npx():
        return False
    try:
        _run_npx(
            ["npx", "mmdc", "--version"],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except Exception:
        return False


def check_chrome() -> tuple[bool, bool]:
    """Return (is_available, install_attempted)."""
    if not check_npx():
        return False, False
    try:
        result = _run_npx(
            ["npx", "puppeteer", "browsers", "list"],
            check=False,
            capture_output=True,
            text=True,
        )
        available = "chrome-headless-shell" in result.stdout
        if available:
            return True, False

        install = _run_npx(
            ["npx", "puppeteer", "browsers", "install", "chrome-headless-shell"],
            check=False,
            capture_output=True,
            text=True,
        )
        installed = install.returncode == 0 and "chrome-headless-shell" in install.stdout
        return installed, True
    except Exception:
        return False, False


def main() -> int:
    status = {
        "creating_mermaid_diagrams": check_creating_mermaid_diagrams(),
        "npx": check_npx(),
        "mmdc": check_mmdc(),
        "chrome": False,
        "chrome_install_attempted": False,
        "ready": False,
        "messages": [],
    }

    if not status["npx"]:
        status["messages"].append(
            "npx not found. Make sure Node.js / npm is installed and npx is in PATH."
        )

    if not status["creating_mermaid_diagrams"]:
        status["messages"].append(
            "creating-mermaid-diagrams skill not found. Install with:\n"
            "  npx skills add https://github.com/Agents365-ai/mermaid-skill"
        )

    if not status["mmdc"]:
        status["messages"].append(
            "mmdc CLI not found. Install with:\n"
            "  npm install -g @mermaid-js/mermaid-cli"
        )

    if not status["creating_mermaid_diagrams"]:
        status["messages"].append(
            "creating-mermaid-diagrams skill not found. Install with:\n"
            "  npx skills add https://github.com/Agents365-ai/mermaid-skill"
        )

    if not status["mmdc"]:
        status["messages"].append(
            "mmdc CLI not found. Install with:\n"
            "  npm install -g @mermaid-js/mermaid-cli"
        )

    status["chrome"], status["chrome_install_attempted"] = check_chrome()
    if not status["chrome"]:
        status["messages"].append(
            "Chrome headless shell not available. Diagram generation may fail; "
            "consider skipping diagrams or installing Chrome manually."
        )

    status["ready"] = (
        status["creating_mermaid_diagrams"] and status["mmdc"]
    )

    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
