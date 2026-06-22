#!/usr/bin/env python3
"""Cross-platform environment check for the spec2readme skill.

Checks:
- creating-mermaid-diagrams skill installation
- mmdc CLI availability (binary + --version)
- mmdc end-to-end render test (generates a tiny .mmd → PNG to verify Chrome/Puppeteer pipeline)
- Puppeteer / Chrome headless shell availability (auto-installs if missing)

Exit codes:
    0  ready (all checks pass including render test)
    1  critical dependency missing (creating-mermaid-diagrams, mmdc, or render test failed)
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile


def _run_mmdc(cmd: list[str], **kwargs):
    """Run mmdc with platform-appropriate shell handling."""
    if sys.platform == "win32":
        return subprocess.run(" ".join(cmd), shell=True, **kwargs)
    return subprocess.run(cmd, **kwargs)


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


def check_mmdc_render() -> tuple[bool, str]:
    """Run a real mmdc render test to verify the full pipeline.

    Generates a minimal .mmd file, renders it with mmdc, and checks the
    output PNG exists. This catches Chrome/Puppeteer issues that a simple
    ``mmdc --version`` would miss.

    Returns (success, error_message).
    """
    mmd_content = "graph TD;\n    A-->B;\n"
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            mmd_file = Path(tmpdir) / "test.mmd"
            png_file = Path(tmpdir) / "test.png"
            mmd_file.write_text(mmd_content, encoding="utf-8")

            result = _run_mmdc(
                ["mmdc", "-i", str(mmd_file), "-o", str(png_file)],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                stderr = result.stderr.strip()
                return False, stderr.splitlines()[-1] if stderr else "mmdc render failed"

            if not png_file.is_file() or png_file.stat().st_size == 0:
                return False, "mmdc render produced no output file"

            return True, ""
    except subprocess.TimeoutExpired:
        return False, "mmdc render timed out (30s)"
    except FileNotFoundError:
        return False, "mmdc not found in PATH"
    except Exception as e:
        return False, str(e)


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
        "mmdc_render": False,
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

    status["chrome"], status["chrome_install_attempted"] = check_chrome()
    if not status["chrome"]:
        status["messages"].append(
            "Chrome headless shell not available. May cause render failure; "
            "install with: npx puppeteer browsers install chrome-headless-shell"
        )

    if status["mmdc"]:
        status["mmdc_render"], render_err = check_mmdc_render()
        if not status["mmdc_render"]:
            status["messages"].append(
                "mmdc render test failed. Attempting auto-repair (install Chrome headless)...\n"
                f"  Error: {render_err}"
            )
            # Attempt auto-repair: install Chrome and retry render
            _run_npx(
                ["npx", "puppeteer", "browsers", "install", "chrome-headless-shell"],
                check=False,
                capture_output=True,
                text=True,
            )
            status["mmdc_render"], render_err = check_mmdc_render()
            if status["mmdc_render"]:
                status["messages"].append("Auto-repair successful: mmdc render test passed after Chrome install.")
            else:
                status["messages"].append(
                    "Auto-repair failed. mmdc is installed but cannot produce output.\n"
                    f"  Error: {render_err}\n"
                    "  Manual fix: npx puppeteer browsers install chrome-headless-shell\n"
                    "  or use Kroki API fallback."
                )

    status["ready"] = (
        status["creating_mermaid_diagrams"]
        and status["mmdc"]
        and status["mmdc_render"]
    )

    print(json.dumps(status, ensure_ascii=False, indent=2))
    return 0 if status["ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
