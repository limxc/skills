---
comet_change: refine-spec2article-interaction
role: technical-design
canonical_spec: openspec
---

# Design: Add Draft Review Step Before Final Article Generation

## Context

The `spec2article-wechat` skill converts Comet development archives into WeChat public account articles. Currently, the Pre-3 phase processes change materials, generates images, and immediately creates a draft file, then passes it to the wewrite pipeline. There is no opportunity for the user to review and adjust the full article text before it enters the automated writing/publishing pipeline.

## Goals / Non-Goals

**Goals:**
- Add a full-draft review step between image confirmation and final file generation
- Allow iterative user feedback and adjustment cycles
- Enforce interactive mode when entering the wewrite pipeline

**Non-Goals:**
- No changes to wewrite's internal logic
- No changes to Pre-1 environment setup or Pre-2 change selection
- No changes to image generation logic

## Decisions

1. **Draft Presentation**: The agent presents the full draft text inline (not as a file), and the user provides feedback per-section or overall. The agent adjusts and re-presents.
2. **Adjustment Cycle**: No hard limit on iterations. The user decides when the draft is satisfactory.
3. **Finalization**: Only after user confirmation does the agent write the `.md` file to `spec2article-wechat-output/`.
4. **wewrite Interactive Mode**: Prepend `[交互模式]` directive to the wewrite prompt, explicitly listing pause points: title, skeleton, images, preview, publish.

## Workflow Change

```
Before:
  3.1 Read changes → 3.2 Generate images → 3.3 Confirm images → 3.4 Write draft → wewrite

After:
  3.1 Read changes → 3.2 Generate images → 3.3 Confirm images →
  3.4 Present draft → User feedback → Adjust (loop) →
  3.5 Write final draft → wewrite (interactive mode enforced)
```

## Risks / Trade-offs

- Additional interaction step increases session length, but prevents wasted effort from publishing unsatisfactory content
- Unlimited loops could theoretically extend sessions, but user naturally decides when satisfied — no agent-imposed cutoff
