# User-Facing Output Design

This document defines what users should see after running Agent Skill Anatomy. It translates deterministic decomposition artifacts and LLM analysis artifacts into readable, navigable, and reusable product surfaces.

本文档定义用户在完成一次 Agent Skill Anatomy 拆解后最终看到什么。核心目标是把确定性拆解、LLM 分析、reviewer 反馈和复用资产组织成清晰的用户体验，而不是只输出一次性报告。

## 1. Output Principles

- **Report as the hub**: the web report is the primary professional reading surface and should link to every other output.
- **Cinematic page as explanation**: the repo cinematic page explains the decomposition process and acts as a visual entry, not the source of all detail.
- **Skill detail as the core learning unit**: each skill must have a deep page that explains identity, activation, workflow, evidence, risk, and reuse.
- **Evidence always reachable**: users should be able to trace important claims back to source paths, quotes, blocks, or deterministic artifacts.
- **Facts and analysis separated**: deterministic facts, LLM interpretation, and reviewer findings must be visually distinguishable; model comparison stays in development/testing artifacts.
- **Multiple output modes**: users should choose Web Report, Obsidian, Graph, or JSON/Data depending on their workflow.
- **Chinese by default, English optional**: public UI and reports should default to Chinese and support EN toggle.

## 2. User Flow

Recommended navigation:

```text
Home / Run Setup
  ↓
Cinematic Repo Page
  ↓
Repo Report Home
  ├─ Skill Detail Pages
  ├─ Evidence & Quality
  ├─ Reusable Assets
  ├─ Model Analysis / Model Comparison
  ├─ Obsidian Vault
  ├─ Graph View
  └─ JSON/Data Artifacts
```

## 3. Home / Run Setup

Purpose: let users start a decomposition run.

User should see:

- GitHub URL or local path input
- model/provider selector
- custom endpoint settings
- output format selector
- run progress timeline
- handoff into report outputs

Primary data sources:

- user input
- provider registry
- local config examples
- run status metadata

Key actions:

- start decomposition
- configure model
- test provider connection
- open latest report
- choose output surface

## 4. Cinematic Repo Page

Purpose: explain the decomposition process and provide an attractive visual entry.

User should see stages:

1. `Source`: repo snapshot, file count, skill count, commit
2. `Core`: detected skill packages and `SKILL.md` structure
3. `Resources`: scripts, references, assets, examples
4. `Workflow`: extracted workflow signals and reconstructed process
5. `Evidence`: evidence index and reviewer grounding
6. `Report`: output surfaces and final artifacts

Final state:

- six equal cards in a two-column layout
- each card links to the matching report section
- cards should stay visually calm when idle
- optional pointer-driven micro interaction is allowed, but no automatic frame-by-frame motion by default

Primary data sources:

- `deterministic_summary.json`
- `skill_packages.json`
- `file_inventory.json`
- `workflow_signals.json`
- `evidence_index.json`
- report/export manifest

## 5. Repo Report Home

Purpose: the main professional report surface.

Recommended sections:

### 5.1 Executive Summary

User should see:

- repo identity
- run timestamp
- selected model(s)
- number of skills detected
- high-level findings
- quality status

Sources:

- `repo_snapshot.json`
- `deterministic_summary.json`
- `quality_review.json`
- `model_comparison.json`, when available

### 5.2 Decomposition Coverage

User should see:

- total files
- skill packages
- scripts/references/assets counts
- evidence count
- unknown files
- coverage warnings

Sources:

- `deterministic_summary.json`
- `file_inventory.json`
- `skill_packages.json`
- `evidence_index.json`

### 5.3 Skill Inventory

User should see:

- skill list
- purpose
- status
- risk level
- reuse score
- quality status
- links to skill detail pages

Sources:

- `skill_packages.json`
- `structure_analysis.json`
- `tool_risk_analysis.json`
- `reuse_analysis.json`
- `quality_review.json`

### 5.4 Workflow Map

User should see:

- common workflow stages
- per-skill workflow completeness
- action/condition/fallback counts
- human confirmation points

Sources:

- `workflow_signals.json`
- `workflow_analysis.json`

### 5.5 Resource & Dependency Map

User should see:

- scripts/references/assets usage
- external URLs
- packages and CLI tools
- environment variables and APIs
- central reusable files

Sources:

- `file_inventory.json`
- `dependency_index.json`
- `reuse_analysis.json`

### 5.6 Evidence & Quality

User should see:

- evidence count by type
- unsupported claims
- missing evidence
- over-inference
- reviewer status
- issue cards with suggested fixes

Sources:

- `evidence_index.json`
- `quality_review.json`
- deterministic quality rules

### 5.7 Reusable Assets

User should see:

- workflow patterns
- prompt patterns
- scripts
- templates
- references
- safety/evaluation rules
- portability and adaptation notes

Sources:

- `reuse_analysis.json`
- `learning_notes.json`

### 5.8 Model Analysis / Comparison

User should see:

- selected model metadata
- model-specific scores
- grounding quality
- disagreement cases when multiple models run
- best model by task type

Sources:

- `analysis/<model-id>/*`
- `comparison/model_comparison.json`
- `comparison/model_scorecard.json`

### 5.9 Export Hub

User should see links to:

- Obsidian Vault
- Graph View
- JSON/Data artifacts
- skill detail pages
- cinematic repo page

Sources:

- export manifest
- file paths under `exports/`, `site/`, or `dist/`

## 6. Single Skill Detail Page

Purpose: the main learning unit for one skill.

Recommended sections:

1. Skill identity
2. Activation and do-not-use conditions
3. Boundaries and risks
4. Inputs and outputs
5. Workflow reconstruction
6. Tools and permissions
7. Resources and dependencies
8. Evidence table
9. Reuse suggestions
10. Reviewer feedback
11. Model differences, if available

Each section should separate:

- deterministic facts
- model analysis
- reviewer feedback
- unsupported/inferred claims

## 7. Obsidian Vault

Purpose: long-term learning and knowledge reuse.

Recommended folders:

```text
00 Maps/
01 Repo/
02 Skills/
03 Workflows/
04 Reusable Assets/
05 Quality/
06 Model Comparison/
07 Sources/
```

Recommended note types:

- repo MOC
- skill note
- workflow pattern note
- reusable asset note
- risk note
- quality note
- model comparison note
- source/evidence note

## 8. Graph View

Purpose: relationship exploration.

Recommended node types:

- repo
- skill
- file
- content block
- workflow node
- tool
- dependency
- evidence
- reusable asset
- model analysis
- review issue

Recommended edge types:

- contains
- references
- depends_on
- uses_tool
- supports_claim
- produces
- inferred_from
- reviews
- disagrees_with

Current implementation:

- `asa export-data` writes `data/graph-data.json` and `data/graph.mmd`.
- `site/graph/` first attempts to load `../data/graph-data.json`; if unavailable it falls back to the Cinema manifest demo graph.
- Current node groups are run, skill, resource, workflow_step, evidence, and reuse.
- Current edge groups are contains_skill, uses_resource, has_step, next_step, step_uses_resource, has_evidence_audit, and has_reuse_asset.

## 9. JSON/Data Artifacts

Purpose: developer reuse, benchmarking, and future UI layers.

User should see:

- deterministic artifacts
- model analysis artifacts
- comparison artifacts
- export manifest
- schema version

UI should provide:

- artifact browser
- raw JSON link
- download bundle
- schema reference link

## 10. Review Cards

Purpose: actionable feedback.

Each card should show:

- issue type
- severity
- target artifact and JSON path
- explanation
- suggested fix
- evidence IDs
- affected skill

Recommended issue categories:

- unsupported claim
- invalid evidence ID
- missing evidence
- over-inference
- missing file coverage
- missing dependency coverage
- risky tool use
- weak fallback path
- vague or generic analysis

## 11. Source Mapping

Every visible section should declare its source class:

- `deterministic`: extracted by rules/parsers
- `analysis`: produced by selected LLM
- `review`: produced by reviewer or quality rules
- `comparison`: produced by model comparison
- `export`: generated output path or manifest

UI can display these as small source labels so users understand whether they are reading facts, analysis, review, or comparison.

## 12. Initial Implementation Target

The first implementation pass should add the following to the existing static report:

- report navigation hub
- decomposition coverage section
- workflow map placeholder section
- resource/dependency section
- reusable assets section
- model analysis section
- export hub section
- source labels for deterministic/analysis/review/export

This creates the user-facing skeleton before real deterministic artifacts and full analysis schemas are fully implemented.
