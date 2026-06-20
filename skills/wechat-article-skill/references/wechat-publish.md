# WeChat Publishing Guide

## Prerequisites

To publish to WeChat draft box, you need:

1. **WeChat Official Account** (微信公众号) — any type (Subscription/Service)
2. **AppID** and **AppSecret** — from the WeChat Official Account backend
   - Login at https://mp.weixin.qq.com/
   - Go to 开发 → 基本配置 → AppID / AppSecret
   - Note: AppSecret is only shown once; regenerate if lost

## Configuration

### Option A: CLI arguments (quick)

```bash
python3 <skill>/scripts/publish.py article.md \
  --appid wx1234567890abcdef \
  --secret abcdef1234567890abcdef1234567890
```

### Option B: Config file (recommended)

Create `<project-root>/config.yaml`:
```yaml
wechat:
  appid: wx1234567890abcdef
  secret: abcdef1234567890abcdef1234567890
```

Then run:
```bash
python3 <skill>/scripts/publish.py article.md --config config.yaml
```

### Option C: Using wewrite toolkit

For rich formatting with 16+ themes:
```bash
# Install
git clone --depth 1 https://github.com/oaker-io/wewrite.git ~/.agents/skills/wewrite
cd ~/.agents/skills/wewrite && pip install -r requirements.txt

# Preview with theme
python3 toolkit/cli.py preview article.md --theme sspai

# Publish
python3 toolkit/cli.py publish article.md \
  --appid wx... --secret ... \
  --theme professional-clean \
  --cover cover.png
```

## What the Publish Script Does

1. **Convert** markdown to WeChat-compatible HTML
2. **Upload local images** to WeChat CDN (replaces local paths with WeChat URLs)
3. **Upload cover image** as permanent material (returns media_id)
4. **Create draft** via WeChat Draft API (`/cgi-bin/draft/add`)
5. Return `media_id` — the draft is now in your WeChat backend draft box

## After Publishing

1. Go to https://mp.weixin.qq.com/ → 草稿箱
2. Find the new draft
3. Review formatting, images, and layout
4. Add any final touches (cover image, original link, etc.)
5. Publish or schedule

## Troubleshooting

| Error | Likely Cause | Solution |
|-------|-------------|----------|
| `errcode=40001` | Invalid AppSecret | Regenerate secret |
| `errcode=40013` | Invalid AppID | Check AppID |
| `errcode=45009` | API rate limit | Wait and retry |
| `errcode=41005` | Missing media data | Check image path |
| `errcode=40035` | Invalid JSON | Check for non-UTF-8 chars in HTML |
| Title too long | Over 64 chars | Shorten title |
| Digest too long | Over 120 UTF-8 bytes | Shorten digest |

## WeChat HTML Limitations

- Only supports: h1-h4, p, strong, em, blockquote, ul/ol, a, img, code, pre
- No `<style>` tags — use inline styles only
- No `<script>` tags — stripped automatically
- `<table>` is supported but styling is limited
- External links become `[上标注脚]` in article body with reference list at end
- Dark mode: inject `data-darkmode-*` attributes for compatibility

For full formatting support, use wewrite toolkit's converter which handles all these constraints automatically.
