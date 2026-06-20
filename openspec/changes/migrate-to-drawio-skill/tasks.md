## 1. Dependency Installation

- [ ] 1.1 Install drawio-skill via `npx skills add Agents365-ai/365-skills -g`
- [ ] 1.2 Verify draw.io Desktop CLI is operational (`drawio --version`)
- [ ] 1.3 Verify drawio-skill loads correctly (`/drawio` trigger available)
- [ ] 1.4 Remove `diagrams` from Pre-1 Python dependency check in SKILL.md

## 2. Update SKILL.md Pre-3 Phase

- [ ] 2.1 Update Pre-3.3 instruction to use drawio-skill for diagram generation instead of YAML spec + diagram.py flow
- [ ] 2.2 Add drawing-type selection logic matching drawio-skill's 6 presets (architecture, ML, flow, UML, sequence, ER)
- [ ] 2.3 Add 1080px width export requirement to WeChat Image Rule section
- [ ] 2.4 Add drawio-skill as a dependency in the Pre-1 dependency check
- [ ] 2.5 Update the scripts table to reflect new diagram.py role
- [ ] 2.6 Update the skill description metadata to indicate drawio-skill integration

## 3. Pre-3 Delegation to drawio-skill

- [ ] 3.1 Update Pre-3.3 instructions to load drawio-skill SKILL.md and delegate diagram generation (same pattern as Step 4-7 delegating to wewrite)
- [ ] 3.2 Add natural language description template for drawio-skill invocation, including 1080px width and WeChat quality requirements
- [ ] 3.3 Remove `scripts/diagram.py` (no longer needed) and the `diagrams` Python package dependency
- [ ] 3.4 Remove YAML spec generation from Pre-3 flow

## 4. Update Install Scripts

- [ ] 4.1 Update `install.ps1` to install drawio-skill after wechat-article-skill
- [ ] 4.2 Update `install.sh` to install drawio-skill after wechat-article-skill
- [ ] 4.3 Verify draw.io CLI presence during installation
- [ ] 4.4 Update requirements.txt to remove `diagrams` package

## 5. Update Documentation

- [ ] 5.1 Update `references/complete-flow.md` to reflect new drawio-skill flow in Pre-3
- [ ] 5.2 Update `AGENTS.md` to reflect new diagram generation approach
