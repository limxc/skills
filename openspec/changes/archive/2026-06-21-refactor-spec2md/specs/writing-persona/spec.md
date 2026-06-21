## ADDED Requirements

### Requirement: Persona selection from style.yaml
The system SHALL load writing personas from `<skill-dir>/style.yaml` and offer the user top 3 candidates based on topic keyword matching with selected changes.

#### Scenario: Persona matched by topic
- **WHEN** user has selected changes with descriptions containing topic keywords
- **THEN** system sorts personas by topic similarity and presents top 3

#### Scenario: No matching topic
- **WHEN** no topic keywords match any persona
- **THEN** system defaults to the 3 most recently used personas

### Requirement: Persona display with style sample
Each persona candidate SHALL include a style excerpt from `style.yaml` so the user can judge the writing tone before selecting.

#### Scenario: Persona selection with sample
- **WHEN** system presents persona options
- **THEN** each option includes a sample text excerpt from the persona's example field

### Requirement: Persona injection into writing prompt
The selected persona's style description SHALL be injected into the writing prompt to guide article generation.

#### Scenario: Article generated with persona
- **WHEN** user confirms a persona
- **THEN** the writing prompt includes the persona's style description, tone, and vocabulary preferences
