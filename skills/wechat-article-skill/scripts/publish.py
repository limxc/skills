#!/usr/bin/env python3
"""Publish a markdown article as WeChat draft.

Usage:
    python publish.py article.md --appid wx... --secret ...
    python publish.py article.md --config config.yaml
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
import mimetypes

import requests


# WeChat API endpoints
WECHAT_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
WECHAT_UPLOAD_IMG_URL = "https://api.weixin.qq.com/cgi-bin/media/uploadimg"
WECHAT_UPLOAD_THUMB_URL = "https://api.weixin.qq.com/cgi-bin/material/add_material"
WECHAT_DRAFT_URL = "https://api.weixin.qq.com/cgi-bin/draft/add"

API_TIMEOUT = 30
_TOKEN_CACHE: dict = {}


def get_access_token(appid: str, secret: str) -> str:
    import time
    now = time.time()
    if appid in _TOKEN_CACHE:
        cached = _TOKEN_CACHE[appid]
        if now < cached["expires_at"]:
            return cached["access_token"]

    resp = requests.get(
        WECHAT_TOKEN_URL,
        params={"grant_type": "client_credential", "appid": appid, "secret": secret},
        timeout=API_TIMEOUT,
    )
    data = resp.json()
    if "access_token" not in data:
        raise ValueError(f"WeChat token error: {data}")
    token = data["access_token"]
    _TOKEN_CACHE[appid] = {
        "access_token": token,
        "expires_at": now + data.get("expires_in", 7200) - 300,
    }
    return token


def upload_image(access_token: str, image_path: str) -> str:
    path = Path(image_path)
    ct = mimetypes.guess_type(image_path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        resp = requests.post(
            WECHAT_UPLOAD_IMG_URL,
            params={"access_token": access_token},
            files={"media": (path.name, f, ct)},
            timeout=API_TIMEOUT,
        )
    data = resp.json()
    if "url" not in data:
        raise ValueError(f"WeChat upload_image error: {data}")
    return data["url"]


def upload_thumb(access_token: str, image_path: str) -> str:
    path = Path(image_path)
    ct = mimetypes.guess_type(image_path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        resp = requests.post(
            WECHAT_UPLOAD_THUMB_URL,
            params={"access_token": access_token, "type": "image"},
            files={"media": (path.name, f, ct)},
            timeout=API_TIMEOUT,
        )
    data = resp.json()
    if "media_id" not in data:
        raise ValueError(f"WeChat upload_thumb error: {data}")
    return data["media_id"]


def create_draft(
    access_token: str,
    title: str,
    html: str,
    digest: str = "",
    thumb_media_id: Optional[str] = None,
    author: Optional[str] = None,
):
    article = {
        "title": title,
        "author": author or "",
        "digest": digest,
        "content": html,
        "show_cover_pic": 1,
    }
    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id

    resp = requests.post(
        WECHAT_DRAFT_URL,
        params={"access_token": access_token},
        data=json.dumps({"articles": [article]}, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json; charset=utf-8"},
        timeout=API_TIMEOUT,
    )
    data = resp.json()
    if data.get("errcode", 0) != 0:
        raise ValueError(f"WeChat create_draft error: {data}")
    if "media_id" not in data:
        raise ValueError(f"WeChat create_draft: missing media_id: {data}")
    return data["media_id"]


def guess_title(markdown_text: str) -> str:
    """Extract the first # heading as title."""
    for line in markdown_text.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def guess_digest(html: str, max_bytes: int = 120) -> str:
    """Generate a digest from HTML content."""
    import re
    text = re.sub(r"<[^>]+>", "", html)
    text = re.sub(r"\s+", " ", text).strip()
    # Truncate by UTF-8 bytes (WeChat limit)
    encoded = text.encode("utf-8")
    if len(encoded) <= max_bytes:
        return text[:200]
    # Find safe truncation point
    truncated = encoded[:max_bytes].decode("utf-8", errors="ignore")
    return truncated


def convert_markdown_to_html(markdown_text: str) -> str:
    """Basic markdown to HTML conversion for WeChat.

    For rich formatting, use wewrite's converter instead.
    WeChat supports: h1-h4, p, strong, em, blockquote, ul/ol, a, img, code, pre.
    """
    import re

    lines = markdown_text.splitlines()
    html_parts = []
    in_code_block = False
    code_buffer = []

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("```"):
            if in_code_block:
                code = "\n".join(code_buffer)
                html_parts.append(f"<pre><code>{_escape_html(code)}</code></pre>")
                code_buffer = []
                in_code_block = False
            else:
                in_code_block = True
            continue

        if in_code_block:
            code_buffer.append(line)
            continue

        if not stripped:
            html_parts.append("<p></p>")
            continue

        # Headings
        if stripped.startswith("# ") and not stripped.startswith("## "):
            html_parts.append(f"<h1>{stripped[2:]}</h1>")
            continue
        if stripped.startswith("## ") and not stripped.startswith("### "):
            html_parts.append(f"<h2>{stripped[3:]}</h2>")
            continue
        if stripped.startswith("### ") and not stripped.startswith("#### "):
            html_parts.append(f"<h3>{stripped[4:]}</h3>")
            continue
        if stripped.startswith("#### "):
            html_parts.append(f"<h4>{stripped[5:]}</h4>")
            continue

        # Blockquote
        if stripped.startswith("> "):
            text = _inline_to_html(stripped[2:].strip())
            html_parts.append(f"<blockquote><p>{text}</p></blockquote>")
            continue

        # Unordered list
        if stripped.startswith("- ") or stripped.startswith("* "):
            text = _inline_to_html(stripped[2:].strip())
            html_parts.append(f"<li>{text}</li>")
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            html_parts.append("<hr>")
            continue

        # Paragraph
        text = _inline_to_html(stripped)
        html_parts.append(f"<p>{text}</p>")

    # Close any open code block
    if in_code_block and code_buffer:
        code = "\n".join(code_buffer)
        html_parts.append(f"<pre><code>{_escape_html(code)}</code></pre>")

    # Wrap consecutive <li> in <ul>
    result = []
    in_list = False
    for part in html_parts:
        if part.startswith("<li>"):
            if not in_list:
                in_list = True
                result.append("<ul>")
            result.append(part)
        else:
            if in_list:
                result.append("</ul>")
                in_list = False
            result.append(part)
    if in_list:
        result.append("</ul>")

    return "\n".join(result)


def _inline_to_html(text: str) -> str:
    """Convert inline markdown to HTML."""
    import re
    text = _escape_html(text)
    # Images: ![alt](url)
    text = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img src="\2" alt="\1" />', text)
    # Links: [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', text)
    # Bold: **text**
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    # Italic: *text*
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    # Inline code: `text`
    text = re.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    return text


def _escape_html(text: str) -> str:
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    return text


def _load_config(config_path: str) -> dict:
    import yaml
    with open(config_path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    parser = argparse.ArgumentParser(description="Publish markdown as WeChat draft")
    parser.add_argument("input", help="Markdown file path")
    parser.add_argument("--appid", help="WeChat AppID")
    parser.add_argument("--secret", help="WeChat AppSecret")
    parser.add_argument("--config", help="YAML config file with wechat.appid/secret")
    parser.add_argument("--title", help="Article title (default: from # heading)")
    parser.add_argument("--author", help="Article author")
    parser.add_argument("--digest", help="Article digest (max 120 UTF-8 bytes)")
    parser.add_argument("--cover", help="Cover image path")
    parser.add_argument("--dry-run", action="store_true", help="Only convert, don't publish")

    args = parser.parse_args()

    # Resolve credentials
    appid = args.appid
    secret = args.secret
    if args.config:
        cfg = _load_config(args.config)
        wechat = cfg.get("wechat", {})
        appid = appid or wechat.get("appid")
        secret = secret or wechat.get("secret")

    # Read markdown
    md_path = Path(args.input)
    md_text = md_path.read_text(encoding="utf-8")

    # Convert to HTML
    html = convert_markdown_to_html(md_text)

    # Resolve title
    title = args.title or guess_title(md_text) or md_path.stem

    # Resolve digest
    digest = args.digest or guess_digest(html)

    if args.dry_run:
        output_path = md_path.with_suffix(".html")
        output_path.write_text(html, encoding="utf-8")
        print(f"=== WeChat Article Preview ===")
        print(f"Title: {title}")
        print(f"Digest: {digest}")
        print(f"HTML: {output_path}")
        print(f"\nTo publish with rich formatting, use wewrite toolkit:")
        print(f"  python3 wewrite/toolkit/cli.py publish {args.input} --appid {appid or '<appid>'} --secret <secret>")
        return

    if not appid or not secret:
        print("Error: --appid and --secret required (or --config)", file=sys.stderr)
        sys.exit(1)

    # Publish
    print(f"Step 1/3: Getting access token...")
    token = get_access_token(appid, secret)

    # Upload images
    import re as regex
    img_pattern = regex.compile(r'<img[^>]+src="([^"]+)"')
    for img_src in img_pattern.findall(html):
        if img_src.startswith(("http://", "https://")):
            continue
        img_path = Path(img_src)
        if not img_path.is_absolute():
            img_path = md_path.parent / img_src
        if img_path.exists():
            print(f"  Uploading image: {img_src}")
            wechat_url = upload_image(token, str(img_path))
            html = html.replace(img_src, wechat_url)
        else:
            print(f"  Warning: image not found: {img_src}")

    # Upload cover
    thumb_id = None
    if args.cover:
        print(f"  Uploading cover: {args.cover}")
        thumb_id = upload_thumb(token, args.cover)

    print(f"Step 2/3: Creating draft...")
    media_id = create_draft(
        access_token=token,
        title=title,
        html=html,
        digest=digest,
        thumb_media_id=thumb_id,
        author=args.author,
    )

    print(f"Step 3/3: Done!")
    print(f"\nDraft created in WeChat draft box!")
    print(f"  Title: {title}")
    print(f"  media_id: {media_id}")
    print(f"\nGo to your WeChat Official Account backend to review and publish.")


if __name__ == "__main__":
    main()
