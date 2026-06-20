# draft-review Specification

## Purpose
TBD - created by archiving change refine-spec2article-interaction. Update Purpose after archive.
## Requirements
### Requirement: Draft review before final generation

The system SHALL present the full draft to the user for review before writing the final article file. The agent SHALL collect user feedback, apply adjustments, and repeat until the user confirms satisfaction.

#### Scenario: User reviews draft and requests changes

- **WHEN** agent presents the full draft text to the user
- **THEN** user can provide specific feedback, and agent adjusts the draft accordingly

#### Scenario: User confirms draft is ready

- **WHEN** user confirms the draft meets expectations
- **THEN** agent writes the final `.md` file to `spec2article-wechat-output/article-{date}.md`

#### Scenario: Multiple adjustment rounds

- **WHEN** user requests further changes after an adjustment
- **THEN** agent continues to present updated drafts and collect feedback until user confirms

### Requirement: wewrite interactive mode enforcement

The system SHALL enforce interactive mode when entering the wewrite pipeline (Step 4-8). The agent MUST pause at every decision point (title selection, skeleton choice, image decisions, preview confirmation, publish confirmation) using the question tool.

#### Scenario: Interactive mode activation

- **WHEN** agent loads wewrite SKILL.md
- **THEN** agent prepends `[交互模式]` directive requiring question tool pauses at all decision points

#### Scenario: Decision point pause

- **WHEN** wewrite reaches a decision point (title, skeleton, image, preview, publish)
- **THEN** agent MUST use the question tool to get user confirmation before proceeding

