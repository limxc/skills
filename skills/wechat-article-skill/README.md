# wechat-article-skill

Generate WeChat public account (微信公众号) articles from Comet development archives.

## What it does

After completing Comet workflow changes, `/wechat-article` reads the archived changes and generates a WeChat article summarizing what was built, designed, and fixed. The article is presented for review, then published to your WeChat draft box.

## Installation

```bash
# Clone to your agent's skills directory
git clone <this-repo> ~/.agents/skills/wechat-article-skill
```

### Platform-specific paths

| Tool | Path |
|------|------|
| OpenCode | `~/.config/opencode/skills/` |
| Claude Code | `~/.claude/skills/` |
| Gemini CLI | `~/.gemini/skills/` |
| Universal | `~/.agents/skills/` |

### Quick install

```bash
# Auto-detect
bash install.sh

# Or specify platform
bash install.sh opencode
```

## Usage

After a Comet change is archived:

```
/wechat-article
```

The skill will:
1. Find unprocessed archives
2. Read proposal, design, and tasks
3. Generate a WeChat article
4. Ask for your review
5. Publish to WeChat draft box

## Requirements

- Python 3.8+
- `requests` library
- Comet workflow (for archive creation)
- WeChat Official Account AppID and AppSecret (for publishing)

## Optional Dependencies

- [wewrite](https://github.com/oaker-io/wewrite) — rich WeChat formatting with 16+ themes
- [wechat-article-skills](https://github.com/aiworkskills/wechat-article-skills) — multi-skill WeChat suite

## License

MIT
