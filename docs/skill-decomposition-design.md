# Skill Decomposition Design

This document defines the decomposition method for Agent Skill Anatomy. The goal is to deconstruct agent skills and workflow repositories completely enough that later LLM analysis, reports, Obsidian vaults, graphs, and model comparisons all share the same evidence-first foundation.

本文档定义 Agent Skill Anatomy 的拆解方法。核心目标不是直接让 LLM 写总结，而是先把 skill/repo 拆成稳定、完整、可追溯的事实层，再让选定 LLM 基于事实层分析、审查、复用和教学化。

## 1. Design Goals

- **Complete decomposition first**: collect files, roles, content blocks, links, dependencies, workflow signals, and evidence before any LLM interpretation.
- **Evidence-first analysis**: LLM conclusions must cite deterministic evidence IDs. Unsupported or inferred conclusions must be explicitly marked.
- **Provider-neutral analysis**: OpenAI, Claude, DeepSeek, Qwen, Kimi, local models, and other OpenAI-compatible endpoints should run the same agent roles and schemas.
- **Multi-output reuse**: the same artifacts should power web reports, cinematic repo views, Obsidian vaults, graph views, data exports, and benchmark comparisons.
- **Model comparison ready**: different LLM outputs must be stored independently so their disagreements, omissions, and grounding quality can be compared.

## 2. Pipeline Overview

The decomposition pipeline is split into two chains:

```text
source repo
  ↓
deterministic decomposition chain
  ↓
evidence-indexed fact layer
  ↓
LLM analysis chain for each selected model
  ↓
review / comparison / learning outputs
  ↓
report, vault, graph, data, repo UI
```

### 2.1 Deterministic Decomposition Chain

This chain should rely on rules, parsers, filesystem inspection, and static extraction. It should avoid LLM interpretation.

Responsibilities:

- capture repo metadata and file tree
- detect skill packages
- classify file roles
- split text files into content blocks
- extract links, imports, commands, env vars, and external references
- extract workflow signals such as sequence, conditions, fallback, warnings, and stop conditions
- build a canonical evidence index
- emit deterministic summary and coverage warnings

### 2.2 LLM Analysis Chain

This chain runs after deterministic artifacts exist. Every selected model runs the same agent sequence with the same schema contracts.

Responsibilities:

- interpret structure, activation, boundaries, inputs, and outputs
- reconstruct workflow nodes and failure paths
- analyze tools, permissions, secrets, and risk
- identify reusable assets and reusable workflow patterns
- review grounding and output quality
- create learning notes and Obsidian-ready content
- compare model outputs when multiple models are selected

## 3. Deterministic Artifacts

All deterministic artifacts live under:

```text
runs/<run-id>/deterministic/
```

LLM agents may read these artifacts, but must not overwrite them.

### 3.1 `repo_snapshot.json`

Purpose: describe the collected repository.

Required content:

- source type: `github` or `local`
- repo URL or local path
- owner/name when GitHub source exists
- branch and commit when available
- collection timestamp
- total files, directories, bytes, max depth
- language counts
- root-level files

Used by:

- report overview
- model prompt context
- run comparison across commits and repos

### 3.2 `skill_packages.json`

Purpose: identify every detected skill package.

Required content:

- `skill_id`
- display name
- root path
- `SKILL.md` path when present
- layout type, such as `anthropic_skill`, `agent_skill_standard`, `loose_skill`, or `unknown`
- detection confidence
- package files
- known directories: `scripts`, `references`, `assets`, `examples`, `tests`
- detection rules used

Used by:

- skill list
- per-skill report pages
- Obsidian skill notes
- graph skill nodes

### 3.3 `file_inventory.json`

Purpose: classify every file into a role.

Recommended file roles:

- `skill_definition`
- `script`
- `reference`
- `asset`
- `example`
- `config`
- `test`
- `documentation`
- `license`
- `unknown`

Required content:

- path
- size
- extension
- detected language
- role
- related `skill_id`, if any
- hash
- detected-by rules

Used by:

- coverage checks
- dependency graph
- reviewer missing-file checks
- repo-level statistics

### 3.4 `content_blocks.json`

Purpose: split textual files into evidence-addressable blocks.

Recommended block types:

- `frontmatter`
- `heading`
- `paragraph`
- `list_item`
- `ordered_step`
- `code_block`
- `blockquote`
- `table`
- `link`

Required content:

- `block_id`
- path
- related `skill_id`
- type
- heading level and parent heading when available
- text
- line start and line end
- stable block hash

Used by:

- evidence index
- workflow signal extraction
- LLM prompts
- report source citations

### 3.5 `dependency_index.json`

Purpose: capture relationships between files, tools, packages, URLs, APIs, env vars, and commands.

Recommended dependency types:

- `markdown_link`
- `local_file_reference`
- `python_import`
- `js_import`
- `shell_command`
- `external_url`
- `env_var`
- `api_endpoint`
- `mcp_server`
- `cli_tool`

Required content:

- dependency ID
- source path
- source line or block ID
- related `skill_id`
- dependency type
- target
- target kind: `local_file`, `package`, `url`, `command`, `env`, `api`, `unknown`
- resolved status when local resolution is possible

Used by:

- tool/risk analysis
- resource graph
- reuse analysis
- missing dependency warnings

### 3.6 `workflow_signals.json`

Purpose: extract possible workflow clues without creating a full workflow narrative.

Recommended signal types:

- `sequence`
- `condition`
- `fallback`
- `requirement`
- `warning`
- `tool_use`
- `human_confirmation`
- `stop_condition`
- `output`

Required content:

- signal ID
- `skill_id`
- path
- block ID
- signal type
- marker text, such as `first`, `then`, `if`, `unless`, `fallback`, `stop`, `ask user`
- source text
- line start and line end

Used by:

- Workflow Analyst
- failure mode detection
- flow visualization

### 3.7 `evidence_index.json`

Purpose: provide canonical evidence IDs for all later claims.

Recommended evidence types:

- `direct`: directly stated in source text
- `derived`: derived by deterministic parsing
- `structural`: derived from file structure or path
- `missing`: expected item not found
- `ambiguous`: source exists but interpretation is unclear

Required content:

- `evidence_id`
- related `skill_id`
- path
- block ID when applicable
- line start and line end
- short quote or structural fact
- evidence type
- source artifact name
- tags such as `activation`, `boundary`, `tool`, `workflow`, `risk`, `reuse`

Rules:

- quotes must be short and source-local
- evidence IDs are stable within a run
- LLM outputs must cite existing evidence IDs

### 3.8 `deterministic_summary.json`

Purpose: provide mechanical counts, coverage, and warnings.

Recommended content:

- repo ID
- skill count
- file count
- script/reference/asset counts
- external URL count
- env var count
- skills with scripts/references/assets
- unknown file role count
- missing `SKILL.md` count
- warnings with type, path, and message

Used by:

- report header
- run overview
- LLM prompt summary
- quality gating

## 4. LLM Agent Roles

All LLM outputs live under:

```text
runs/<run-id>/analysis/<model-id>/
```

Each selected model should run a complete independent analysis chain. Mixed-provider ensemble runs must be stored separately under an explicit ensemble strategy name.

### 4.1 Structure Analyst

Output: `structure_analysis.json`

Purpose:

- identify skill identity and purpose
- extract use conditions and do-not-use conditions
- describe boundaries, inputs, and outputs
- summarize confidence and evidence grounding

Inputs:

- `repo_snapshot.json`
- `skill_packages.json`
- `file_inventory.json`
- `content_blocks.json`
- `evidence_index.json`

Required per-skill sections:

- `identity`
- `activation`
- `boundaries`
- `inputs`
- `outputs`
- `confidence`

Evidence rules:

- every important field must contain `evidence_ids`
- inferred items require `inference_level: inferred`

### 4.2 Workflow Analyst

Output: `workflow_analysis.json`

Purpose:

- reconstruct the skill workflow
- identify action nodes, condition nodes, fallback nodes, tool-call nodes, stop nodes, and output nodes
- identify human confirmation points
- list failure modes and recovery strategies

Inputs:

- `content_blocks.json`
- `workflow_signals.json`
- `dependency_index.json`
- `evidence_index.json`
- `structure_analysis.json`

Required per-skill sections:

- workflow summary
- nodes
- edges
- human confirmation points
- failure modes
- workflow completeness
- confidence

Rules:

- if steps are not explicit, set `workflow_completeness: low`
- inferred edges and nodes must be marked as inferred

### 4.3 Tool & Risk Analyst

Output: `tool_risk_analysis.json`

Purpose:

- identify required tools, packages, APIs, and runtimes
- identify permissions and environment needs
- identify secrets and credential handling
- score risk and give mitigation recommendations

Inputs:

- `file_inventory.json`
- `dependency_index.json`
- `content_blocks.json`
- `workflow_analysis.json`
- `evidence_index.json`

Risk dimensions:

- file read/write
- network access
- API keys and secrets
- shell commands
- browser automation
- database or deployment operations
- external service dependency
- large file/resource usage
- privacy-sensitive data
- destructive operations

### 4.4 Reuse Analyst

Output: `reuse_analysis.json`

Purpose:

- identify reusable workflows, prompts, scripts, references, templates, safety rules, and output formats
- estimate portability and adaptation cost
- propose reusable pattern candidates

Inputs:

- `skill_packages.json`
- `file_inventory.json`
- `content_blocks.json`
- `workflow_analysis.json`
- `tool_risk_analysis.json`
- `evidence_index.json`

Reusable asset types:

- `workflow_pattern`
- `prompt_pattern`
- `script`
- `reference`
- `template`
- `evaluation_rule`
- `safety_rule`
- `agent_role`
- `output_format`

Required fields:

- asset ID
- asset type
- title
- description
- reuse value
- portability
- adaptation needed
- conditions
- evidence IDs

### 4.5 Quality Reviewer

Output: `quality_review.json`

Purpose:

- verify evidence grounding
- identify unsupported claims
- identify over-inference
- check missing coverage
- check schema validity and specificity
- determine publishability

Inputs:

- all deterministic artifacts
- all previous analysis artifacts for the same model

Review dimensions:

- evidence grounding
- coverage
- specificity
- risk awareness
- reuse quality
- schema validity
- bilingual quality when bilingual output is enabled

Issue types:

- `missing_evidence`
- `invalid_evidence_id`
- `unsupported_claim`
- `over_inference`
- `missing_file_coverage`
- `missing_dependency_coverage`
- `schema_violation`
- `generic_or_vague_output`

### 4.6 Learning Curator

Output: `learning_notes.json`

Purpose:

- turn reviewed analysis into learning material
- generate Obsidian note plans
- summarize reusable lessons
- produce tutorial outlines and pattern cards

Inputs:

- deterministic artifacts
- analysis artifacts
- `quality_review.json`

Learning output types:

- skill note
- workflow pattern note
- reusable asset note
- risk note
- tutorial step
- glossary term
- comparison note

Rules:

- learning notes should prefer approved or low-risk conclusions
- disputed or unsupported content must be marked visibly

### 4.7 Model Comparator

Output directory:

```text
runs/<run-id>/comparison/
```

Outputs:

- `model_comparison.json`
- `disagreement_cases.json`
- `model_scorecard.json`

Purpose:

- compare multiple model outputs on the same deterministic facts
- identify disagreements and omissions
- score grounding and usefulness
- show which model performed best by task type

Comparison dimensions:

- identity agreement
- activation agreement
- workflow agreement
- risk agreement
- reuse agreement
- missing fields
- unsupported claims
- evidence usage quality
- specificity
- hallucination tendency
- Chinese/English explanation quality

## 5. Artifact Directory Layout

Recommended run layout:

```text
runs/<run-id>/
  deterministic/
    repo_snapshot.json
    skill_packages.json
    file_inventory.json
    content_blocks.json
    dependency_index.json
    workflow_signals.json
    evidence_index.json
    deterministic_summary.json

  analysis/
    <model-id>/
      structure_analysis.json
      workflow_analysis.json
      tool_risk_analysis.json
      reuse_analysis.json
      quality_review.json
      learning_notes.json

  comparison/
    model_comparison.json
    disagreement_cases.json
    model_scorecard.json

  exports/
    report/
    vault/
    graph/
    data/
```

## 6. Evidence and Inference Rules

- Deterministic artifacts are the source of truth.
- LLM outputs are interpretations, not facts.
- Every important LLM claim must cite `evidence_ids`.
- Claims without direct support must include `inference_level: inferred`.
- Unsupported claims must be kept visible for review rather than silently removed.
- Reviewers must reject outputs that cite nonexistent evidence IDs.
- Model comparison must not merge competing claims into a single truth unless a later human or deterministic rule resolves it.

## 7. User-Facing Feedback Forms

The decomposition system should generate multiple feedback surfaces from the same artifacts.

### 7.1 Web Report

Purpose: professional reading and review.

Recommended sections:

- repo overview
- deterministic coverage
- skill inventory
- per-skill structure
- workflow reconstruction
- tool/risk analysis
- reusable assets
- evidence grounding
- reviewer findings
- model comparison when available

### 7.2 Cinematic Repo Page

Purpose: first impression and process explanation.

Recommended role:

- explain the decomposition process visually
- show `Source / Core / Resources / Workflow / Evidence / Report`
- link to detailed report sections
- later support real run data instead of project demo text

### 7.3 Obsidian Vault

Purpose: learning and long-term knowledge reuse.

Recommended notes:

- one skill note per package
- one reusable pattern note per pattern
- one risk note per significant risk class
- one source map / MOC
- model comparison notes when multiple models are used

### 7.4 Graph View

Purpose: relationship understanding.

Recommended nodes:

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

Recommended edges:

- contains
- references
- depends_on
- supports_claim
- uses_tool
- produces
- inferred_from
- disagrees_with

### 7.5 Review Cards

Purpose: actionable feedback.

Each card should focus on one issue or one improvement:

- unsupported claim
- missing evidence
- risky tool use
- unclear activation condition
- weak fallback path
- reusable asset candidate
- model disagreement

## 8. Implementation Priorities

Recommended implementation order:

1. Stabilize deterministic artifacts and evidence IDs.
2. Make LLM agent outputs schema-valid and evidence-bound.
3. Add deterministic quality checks for missing evidence and invalid evidence IDs.
4. Update web report to show fact vs analysis separation.
5. Update Obsidian exporter to consume reviewed analysis.
6. Add graph export from deterministic + analysis artifacts.
7. Add model comparison once at least two providers are reliable.

## 9. Closed Design Defaults

The first implementation pass uses these decisions so product and runtime work can continue without ambiguity:

- Line/path evidence is acceptable for first-pass reports; block hashes can be added later for stricter reproducibility.
- LLM prompts receive compressed evidence bundles by default; full content blocks are reserved for high-context calibration runs.
- Quality review is hybrid: deterministic checks catch structural/evidence failures, while the reviewer model handles semantic coherence.
- Bilingual UI copy is handled by report/export layers; analyst artifacts may include bilingual summaries when useful.
- Public reports may show inferred content only when it is labeled and confidence-bounded.
- Model comparison scores both raw model outputs and reviewed/quality-filtered outputs, but user-facing recommendations prefer reviewed outputs.

See also:

- `docs/report-manual-spec.md`
- `docs/llm-skill-integration-design.md`
- `docs/model-comparison-spec.md`
- `docs/graph-data-surface-spec.md`

## 10. Working Defaults
Until changed, use these defaults:

- deterministic artifacts are immutable after extraction
- one model runs a full independent chain
- `evidence_index.json` is mandatory before LLM analysis
- all LLM artifacts must pass JSON schema validation
- all major claims must cite evidence IDs
- inferred claims are allowed but must be marked
- default public report hides unsupported claims from narrative sections but keeps them in review cards
- default language is Chinese, with English available through the UI/report toggle

