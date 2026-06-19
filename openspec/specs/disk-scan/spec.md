# disk-scan Specification

## Purpose
TBD - created by archiving change disk-space-analyzer. Update Purpose after archive.
## Requirements
### Requirement: Scan directory tree
The system SHALL recursively scan a specified directory path on Windows, enumerating all subdirectories and computing their total size.

#### Scenario: Scan top-level directory
- **WHEN** user requests analysis of path `C:\Users\TestUser`
- **THEN** system shall enumerate all immediate subdirectories of that path and compute their sizes

#### Scenario: Recursive scan of large folders
- **WHEN** a subdirectory exceeds 1 GB in size
- **THEN** system shall recurse into that subdirectory to enumerate its children, up to a maximum depth of 5 levels
- **THEN** subdirectories smaller than 1 GB shall not be recursed into

### Requirement: Skip system folders
The system SHALL NOT analyze protected Windows system folders, including but not limited to `Windows`, `Program Files`, `Program Files (x86)`, and `System32`.

#### Scenario: System folder exclusion
- **WHEN** scanning encounters a path matching a known system folder name
- **THEN** system shall skip that folder and note it was excluded

### Requirement: Handle permission errors
The system SHALL gracefully skip directories it does not have permission to access, without halting the scan.

#### Scenario: Access denied
- **WHEN** scanning encounters a directory without read permission
- **THEN** system shall skip that directory and continue scanning sibling directories
- **THEN** system shall report that the directory was skipped due to insufficient permissions

### Requirement: Report folder sizes
The system SHALL report each directory's total size in human-readable units (Bytes, KB, MB, GB).

#### Scenario: Size formatting
- **WHEN** a folder size is 1,500,000,000 bytes
- **THEN** system shall display it as "1.40 GB"

### Requirement: Filter by size threshold
The system SHALL support a minimum size threshold, returning only folders whose size equals or exceeds the threshold.

#### Scenario: Default threshold
- **WHEN** user does not specify a minimum size
- **THEN** system shall use a default threshold of 1 GB

#### Scenario: Custom threshold
- **WHEN** user specifies a minimum size of 500 MB
- **THEN** system shall include only folders >= 500 MB

