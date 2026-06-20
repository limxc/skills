## 1. Dependency Installation

- [x] 1.1 Install drawio-skill via `npx skills add Agents365-ai/365-skills -g`
- [x] 1.2 Verify draw.io Desktop CLI is operational (`drawio --version`)
- [x] 1.3 Verify drawio-skill loads correctly (`/drawio` trigger available)
- [x] 1.4 Remove `diagrams` from Pre-1 Python dependency check in SKILL.md

## 2. Update SKILL.md Pre-3 Phase

- [x] 2.1 Update Pre-3.3 instruction to use drawio-skill for diagram generation instead of YAML spec + diagram.py flow
- [x] 2.2 Add drawing-type selection logic matching drawio-skill's 6 presets (architecture, ML, flow, UML, sequence, ER)
- [x] 2.3 Add WeChat Image Rule update (drawio-skill default settings, Microsoft YaHei font)
- [x] 2.4 Add drawio-skill as a dependency in the Pre-1 dependency check
- [x] 2.5 Update the scripts table to reflect removed diagram.py
- [x] 2.6 Update the skill description metadata to indicate drawio-skill integration

## 3. Pre-3 Delegation to drawio-skill

- [x] 3.1 Update Pre-3.3 instructions to load drawio-skill SKILL.md and delegate diagram generation
- [x] 3.2 Add natural language description template for drawio-skill invocation
- [x] 3.3 Remove `scripts/diagram.py` (no longer needed) and the `diagrams` Python package dependency
- [x] 3.4 Remove YAML spec generation from Pre-3 flow

## 4. Update Install Scripts

- [x] 4.1 Update `install.ps1` to install drawio-skill after wechat-article-skill
- [x] 4.2 Update `install.sh` to install drawio-skill after wechat-article-skill
- [x] 4.3 Verify draw.io CLI presence during installation
- [x] 4.4 Update requirements.txt to remove `diagrams` package (no requirements.txt found, no action needed)

## 5. Update Documentation

- [x] 5.1 Update `references/complete-flow.md` to reflect new drawio-skill flow in Pre-3
- [x] 5.2 Update `AGENTS.md` to reflect new diagram generation approach
