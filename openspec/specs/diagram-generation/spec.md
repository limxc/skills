# diagram-generation Specification

## Purpose
TBD - created by archiving change migrate-to-drawio-skill. Update Purpose after archive.
## Requirements
### Requirement: LLM generates .drawio XML from natural language description
The system SHALL use drawio-skill to transform a natural language description (e.g., "微服务电商架构图，包含 API Gateway、Auth/User/Order 微服务、Kafka 消息队列") into a `.drawio` XML file conforming to the draw.io format specification.

#### Scenario: Generate architecture diagram
- **WHEN** user describes an architecture scenario in natural language
- **THEN** the system SHALL produce a valid `.drawio` XML file with the appropriate shapes, edges, and layout

#### Scenario: Generate flow diagram
- **WHEN** user describes a business process or workflow
- **THEN** the system SHALL produce a `.drawio` XML file with semantic flow shapes (parallelogram I/O, diamond decisions)

#### Scenario: Generate ML/deep learning diagram
- **WHEN** user describes a neural network architecture
- **THEN** the system SHALL produce a `.drawio` XML file with tensor shape annotations and layer-type color coding

### Requirement: Export PNG using drawio-skill default high-quality settings
The system SHALL use draw.io desktop CLI (`drawio --export`) to export the `.drawio` file to PNG format using drawio-skill's default export settings. The output image SHALL be of sufficient quality for WeChat article use (high-DPI for Retina downscaling).

#### Scenario: Standard export
- **WHEN** draw.io CLI exports a `.drawio` file to PNG
- **THEN** the output PNG SHALL be valid and render correctly

#### Scenario: Custom dimension override
- **WHEN** user specifies custom dimensions in the description
- **THEN** the system SHALL use the user-specified dimensions

### Requirement: Self-check and auto-fix exported images
The system SHALL perform a self-check on the exported PNG by reading pixel data to detect label overlap, text truncation, and line stacking. If issues are detected, the system SHALL automatically fix them (up to 2 rounds) before presenting to the user.

#### Scenario: Auto-fix overlapping labels
- **WHEN** the exported PNG contains overlapping labels
- **THEN** the system SHALL detect the overlap and adjust the layout, then re-export

#### Scenario: No issues found
- **WHEN** the exported PNG passes all self-checks
- **THEN** the system SHALL present the image to the user without modification

### Requirement: Iterative feedback loop (up to 5 rounds)
The system SHALL support user feedback and iterative refinement. After presenting a generated image, the user MAY describe modifications, and the system SHALL adjust the `.drawio` XML and re-export accordingly, for up to 5 rounds.

#### Scenario: User requests modification
- **WHEN** user says "move the database node to the left and add a cache layer"
- **THEN** the system SHALL modify the `.drawio` XML, re-export, show the updated image, and wait for further feedback

#### Scenario: Max iteration reached
- **WHEN** 5 feedback rounds are exhausted
- **THEN** the system SHALL present the current version and ask the user to accept or restart

### Requirement: Use brand icons and official shape library
The system SHALL support searching and using 10,000+ official draw.io shapes (AWS, Azure, GCP, Cisco, Kubernetes, UML, BPMN, ER) via drawio-skill's shapesearch mechanism, and 321 AI/LLM brand icons (OpenAI, Claude, Gemini, etc.) via the aiicons mechanism.

#### Scenario: Use AWS Lambda shape
- **WHEN** user requests "add an AWS Lambda function"
- **THEN** the system SHALL use the exact official draw.io style for AWS Lambda shape

#### Scenario: Use AI brand icon
- **WHEN** user requests "add Claude AI icon"
- **THEN** the system SHALL use the Claude brand icon from drawio-skill's aiicons library

