## ADDED Requirements

### Requirement: Change selection with question tool
The system SHALL display pending changes and ask the user for each change whether to include it, skip it, or hide it permanently, using the `question` tool at the x.x hierarchy level.

#### Scenario: Single change selection
- **WHEN** user runs `/spec2md` and pending changes exist
- **THEN** system uses `question` tool to ask per-change: write article / hide / skip

### Requirement: Skeleton matching and confirmation
The system SHALL automatically match a writing skeleton based on change metadata and use `question` tool for user confirmation at the x.x layer.

#### Scenario: Single change skeleton
- **WHEN** exactly 1 change is selected
- **THEN** system recommends SCQA skeleton and uses `question` tool for confirmation

### Requirement: drawio diagram generation
The system SHALL load drawio-skill to generate diagrams based on change content, with auto-retry (≤2 rounds).

#### Scenario: Architecture diagram generation
- **WHEN** the change involves architecture changes
- **THEN** system generates architecture diagram via drawio-skill

### Requirement: Draft display and modification via direct chat
The system SHALL display the full draft inline and collect modification feedback through direct conversation (not `question` tool) at the x.x.x hierarchy level.

#### Scenario: Draft inline display
- **WHEN** draft is ready
- **THEN** system shows full article inline (not written to file yet)

#### Scenario: Modification cycles
- **WHEN** user requests a change via direct chat
- **THEN** system applies the change and re-displays the full article with `📝` markers on changed sections

### Requirement: Final draft output to docs/
The system SHALL write the confirmed final draft to `docs/{change-name}-{date}/article.md`, along with diagram images and drawio source files.

#### Scenario: Output structure
- **WHEN** user confirms final draft
- **THEN** system creates `docs/{change-name}-{date}/article.md` + `*.png` + `*.drawio`

### Requirement: Dependency check — openspec only
The system SHALL only check for openspec project structure. wewrite and WeChat publish config checks SHALL be removed.

#### Scenario: openspec check
- **WHEN** Pre-1 runs
- **THEN** system checks `openspec/changes/` directory exists
- **THEN** system does NOT check for wewrite or WeChat publish config

### Requirement: Position tracking after publication
The system SHALL mark selected changes as processed via `position.py processed` after the article is finalized.

#### Scenario: Post-write position update
- **WHEN** article is finalized and output files are written
- **THEN** system runs `position.py processed <change-dir-1> ...`
