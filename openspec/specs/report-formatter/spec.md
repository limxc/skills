# report-formatter Specification

## Purpose
TBD - created by archiving change disk-space-analyzer. Update Purpose after archive.
## Requirements
### Requirement: Format as tree table
The system SHALL format scan results as a tree-structured table showing folder hierarchy, size, category, and recommendation.

#### Scenario: Top-level table
- **WHEN** scan results are ready
- **THEN** system shall output a table with columns: Folder Path | Size | Category | Recommendation

#### Scenario: Tree indentation
- **WHEN** showing nested folders (recursion result)
- **THEN** system shall indent child folders under their parent using tree characters (├── └──)

### Requirement: Sort by size
The system SHALL sort folders by size in descending order, with the largest folder first.

#### Scenario: Descending sort
- **WHEN** displaying scan results
- **THEN** folders at the same hierarchy level shall be ordered from largest to smallest

### Requirement: Show summary
The system SHALL display a summary at the top of the report showing total scanned path, total analyzed size, number of folders found, and scan duration.

#### Scenario: Summary line
- **WHEN** scan completes
- **THEN** system shall display: "Scanned: C:\Users | Total: 85.3 GB | Folders >1GB: 12 | Duration: 3.2s"

### Requirement: Highlight large offenders
The system SHALL visually highlight the top 5 largest folders (of the top-level scan) to draw user attention.

#### Scenario: Top 5 emphasis
- **WHEN** more than 5 folders are returned
- **THEN** the 5 largest folders shall be marked with a visual indicator (e.g. `**` or `[TOP]`)

