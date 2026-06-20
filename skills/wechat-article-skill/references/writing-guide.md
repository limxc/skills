# WeChat Article Writing Guide

## Target Audience

Developers and tech-savvy readers interested in development workflows, AI tools, and productivity.

## Tone & Style

- **Conversational Chinese** — Write as if speaking to a friend, not a formal presentation
- **Professional but warm** — Show enthusiasm for the work without being overly promotional
- **Explain the why** — Readers care about motivations and outcomes, not implementation details
- **Use "我们"** — Inclusive first-person plural creates community feeling

## Article Structure

### Title (3 options)

Craft 3 title options following WeChat best practices:
- **Hook style**: "没想到用 AI 开发还能这样写公众号"
- **How-to style**: "从 Comet 归档到微信公众号：我的写作工作流"
- **Update style**: "开发日志 #1：我们最近做了这些改进"

### Digest

1-2 sentences summarizing the article. Max 120 UTF-8 bytes (about 40 Chinese characters).

### Body

Use this structure as a base, adapt as needed:

1. **Opening hook** (2-3 paragraphs)
   - Set the scene: what's been happening in the project
   - Why now
   - What readers will learn

2. **Body sections** (one per archive or theme)
   - Section heading (###)
   - What was the problem/opportunity
   - What we built/changed
   - Design philosophy (keep brief, skip deep technical details)
   - Impact on users

3. **Editor anchor points** — Mark 2-3 spots with `✏️` where the user should insert their own experience, opinion, or anecdote. For example:
   > ✏️ 在这里加一句你个人的使用感受

4. **Closing** (2-3 paragraphs)
   - What's next
   - Call to action (follow, share, comment)
   - How to engage

### SEO (for WeChat search)

- Include keywords naturally in the first 100 characters
- Use subheadings that contain key terms
- End with hashtags: `#开发日志 #AI #工具`

## Quality Checklist

Before presenting to the user, verify:
- [ ] Title is engaging and under 64 chars
- [ ] Digest is under 120 UTF-8 bytes
- [ ] No markdown syntax incompatible with WeChat
- [ ] 2-3 editor anchor points present
- [ ] Each section has a clear takeaway
- [ ] No internal links to unauthorized sites
- [ ] Article flows naturally when read aloud

## Writing Personas

Inspired by wewrite's persona system. Default to `warm-editor` for this skill.

| Persona | When to use | Characteristics |
|---------|-------------|-----------------|
| warm-editor | Default for dev logs | Warm narrative, story + data, gentle emotion arc |
| midnght-friend | Personal/indie dev blogs | Casual, high self-disclosure, first-person |
| industry-observer | Technical analysis | Neutral, data-first, measured opinions |
| sharp-journalist | News/announcements | Concise, data-driven, strong point of view |

## External References

For advanced formatting (16+ WeChat themes, inline style conversion, dark mode support), integrate with wewrite toolkit:
- https://github.com/oaker-io/wewrite
