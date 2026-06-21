# post-process Specification

## Purpose
TBD - created by archiving change refine-spec2md-output. Update Purpose after archive.
## Requirements
### Requirement: Post-process — output to spec2md/ directory
After the user confirms the final draft and all output files are written, the system SHALL place output files under `spec2md/{article-name}/` instead of `docs/{article-name}/`.

#### Scenario: Output in spec2md/ directory
- **WHEN** user confirms final draft
- **THEN** system creates `spec2md/{change-name}-{date}/article.md` + `*.png` + `*.drawio`

### Requirement: Post-process — README timeline link
After output files are written and position tracking is done, the system SHALL append a link entry to the project root `README.md` under the `## 需求时间线` (Requirements Timeline) section.

#### Scenario: First link append
- **WHEN** no `## 需求时间线` section exists in `README.md`
- **THEN** system appends `## 需求时间线` section at end of file with a single link entry

#### Scenario: Subsequent link append
- **WHEN** `## 需求时间线` section already exists in `README.md`
- **THEN** system appends a new link entry as the last item under that section

#### Scenario: Link format
- **WHEN** a link entry is appended
- **THEN** the format SHALL be `- [文章标题 - YYYY-MM-DD](spec2md/{article-name}/article.md)`
- **THEN** "文章标题" SHALL be the final confirmed article title
- **THEN** the date SHALL be the generation date

