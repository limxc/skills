## ADDED Requirements

### Requirement: Classify folder content
The system SHALL classify each scanned folder into one or more content categories based on its name, path patterns, and contents.

#### Scenario: Classify by folder name
- **WHEN** a folder is named `node_modules`, `.npm`, or `.yarn`
- **THEN** system shall classify it as `dependency-cache`

#### Scenario: Classify by path pattern
- **WHEN** a folder path contains `AppData\Local\Temp`
- **THEN** system shall classify it as `temporary-files`

### Requirement: Content category types
The system SHALL use at minimum the following content categories for classification:
- `dependency-cache` — package manager caches (npm, pip, maven, nuget, etc.)
- `temporary-files` — system/app temp files (Temp, tmp, cache)
- `downloads` — user download folders
- `media` — images, videos, audio files
- `code-build` — build artifacts, compiled output (dist, build, out, obj, bin)
- `documents` — user documents, office files
- `virtualization` — VM images, WSL distros, Docker data
- `user-data` — personal user data (Desktop, Documents, Pictures, etc.)
- `recycle-bin` — Recycle Bin / $Recycle.Bin
- `browser-cache` — browser profile data, cache
- `logs` — application and system logs
- `unknown` — unclassifiable content

#### Scenario: Single category assignment
- **WHEN** a folder content type is clearly identifiable
- **THEN** system shall assign exactly one primary category

#### Scenario: Mixed content
- **WHEN** a folder contains files from multiple categories
- **THEN** system shall assign the dominant category based on total file size per type

### Requirement: Assign cleanup recommendation
The system SHALL assign each scanned folder a cleanup recommendation level based on its category.

#### Scenario: Safe to clean
- **WHEN** a folder is classified as `temporary-files`, `browser-cache`, or `recycle-bin`
- **THEN** system shall mark it as `✅ safe-to-clean`

#### Scenario: Cautious
- **WHEN** a folder is classified as `dependency-cache`, `code-build`, or `logs`
- **THEN** system shall mark it as `⚠️ cautious` and explain what would be affected

#### Scenario: Not recommended
- **WHEN** a folder is classified as `downloads`, `user-data`, `documents`, `media`, or `virtualization`
- **THEN** system shall mark it as `🔍 review-manually` and suggest user inspect before deleting
