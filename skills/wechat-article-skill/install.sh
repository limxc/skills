#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="wechat-article-skill"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing $SKILL_NAME..."

# Auto-detect platform
detect_platform() {
  if [ -d "$HOME/.claude/skills" ]; then echo "claude"; return 0; fi
  if [ -d "$HOME/.copilot/skills" ]; then echo "copilot"; return 0; fi
  if [ -d "$HOME/.gemini/skills" ]; then echo "gemini"; return 0; fi
  if [ -d "$HOME/.config/opencode/skills" ]; then echo "opencode"; return 0; fi
  if [ -d "$HOME/.agents" ]; then echo "universal"; return 0; fi
  # Project-level install as fallback
  if [ -d ".git" ] || git rev-parse --git-dir 2>/dev/null; then echo "project"; return 0; fi
  echo "unknown"
}

PLATFORM="${1:-$(detect_platform)}"

case "$PLATFORM" in
  claude)
    TARGET="$HOME/.claude/skills/$SKILL_NAME"
    ;;
  copilot)
    TARGET="$HOME/.copilot/skills/$SKILL_NAME"
    ;;
  gemini)
    TARGET="$HOME/.gemini/skills/$SKILL_NAME"
    ;;
  opencode)
    TARGET="$HOME/.config/opencode/skills/$SKILL_NAME"
    ;;
  universal|agents)
    TARGET="$HOME/.agents/skills/$SKILL_NAME"
    ;;
  project)
    TARGET="$(pwd)/skills/$SKILL_NAME"
    mkdir -p "$(pwd)/skills"
    ;;
  *)
    echo "Unknown platform: $PLATFORM"
    echo "Usage: $0 [claude|copilot|gemini|opencode|universal|project]"
    echo ""
    echo "Detected options:"
    [ -d "$HOME/.claude/skills" ] && echo "  - claude ($HOME/.claude/skills)"
    [ -d "$HOME/.copilot/skills" ] && echo "  - copilot ($HOME/.copilot/skills)"
    [ -d "$HOME/.gemini/skills" ] && echo "  - gemini ($HOME/.gemini/skills)"
    [ -d "$HOME/.config/opencode/skills" ] && echo "  - opencode ($HOME/.config/opencode/skills)"
    [ -d "$HOME/.agents" ] && echo "  - universal ($HOME/.agents/skills)"
    exit 1
    ;;
esac

# Create target directory and copy files
mkdir -p "$TARGET"
cp -r "$SCRIPT_DIR"/* "$TARGET/"
rm -f "$TARGET/install.sh"

# Create symlink in universal path if not already universal
if [ "$PLATFORM" != "universal" ] && [ "$PLATFORM" != "agents" ]; then
  UNIVERSAL_DIR="$HOME/.agents/skills"
  mkdir -p "$UNIVERSAL_DIR"
  if [ ! -e "$UNIVERSAL_DIR/$SKILL_NAME" ]; then
    ln -sf "$TARGET" "$UNIVERSAL_DIR/$SKILL_NAME" 2>/dev/null || true
  fi
fi

echo ""
echo "Skill installed successfully at: $TARGET"
echo ""
echo "To use it, type: /wechat-article"
echo ""
echo "Or in a conversation:"
echo "  /wechat-article"

# Install Python dependencies
if command -v pip3 &>/dev/null; then
  if [ -f "$TARGET/scripts/requirements.txt" ]; then
    echo "Installing Python dependencies..."
    pip3 install -r "$TARGET/scripts/requirements.txt" 2>/dev/null || true
  fi
fi

# Install drawio-skill dependency
echo ""
echo "Installing drawio-skill dependency..."
npx skills add Agents365-ai/365-skills -g 2>/dev/null || echo "Warning: Failed to install drawio-skill. Install manually: npx skills add Agents365-ai/365-skills -g"

# Check draw.io CLI
if ! command -v drawio &>/dev/null; then
  echo "Warning: draw.io CLI not found. Diagram generation requires draw.io Desktop CLI."
  echo "  Download from: https://github.com/jgraph/drawio-desktop/releases"
fi
