# Built-in Meta-Skills Design

This document defines how Agent Skill Anatomy can use internal decomposition skills to improve LLM analysis quality, report richness, Obsidian outputs, and multi-model comparison. The goal is to make the harness analyze skills with a reusable method, not only with one-off prompts.

本文档定义 Agent Skill Anatomy 如何内置一组“拆解用 meta-skills”，让调用 LLM 时拥有稳定的方法论。目标不是让模型自由总结，而是让模型按一组可复用、可审查、可比较的拆解技能工作。


## 0. LetUen Anchor-Pack Direction

The built-in meta-skills are evolving into the LetUen Skill Anchor Pack. The pack should decompose skills into anchors, preserve user skill structures, support temporary composition, and make workflow solidification optional. See:

- `docs/letuen-usage-guide.md`
- `docs/release-v0.2.0-dev-checklist.md`
- `docs/letuen-capability-evaluation-plan.md`
- `docs/letuen-skill-anchor-pack-design.md`
- `docs/letuen-anchor-schema.md`
- `docs/letuen-composition-forms.md`
- `docs/letuen-harness-integration-spec.md`
- `docs/letuen-non-destructive-invocation-policy.md`
- `docs/letuen-anchor-composition-planner-spec.md`
## 1. Core Idea

Current model agents already have roles:

```text
structure_analyst -> workflow_analyst -> reviewer -> pattern_miner
```

Meta-skills add a method layer underneath those roles:

```text
agent role = execution owner
meta-skill = decomposition method
schema = output contract
artifact = source of truth
report/vault = rendered surface
```

A model call should therefore answer:

> Which agent role is running, which meta-skills guide the reasoning, which schema constrains output, and which evidence artifacts are allowed?

## 2. Why This Matters

### 2.1 Better Quality

Prompts alone tend to drift. A dedicated meta-skill makes the model follow a repeatable procedure:

- identify identity before workflow
- separate trigger from boundary
- map resources to execution stages
- mark inferred claims
- distinguish learning assets from raw patterns

### 2.2 More Diverse Outputs

Different meta-skills focus on different outputs:

- beginner explanation
- expert implementation mapping
- reusable templates
- evidence audit
- comparison metrics
- Obsidian learning cards

This prevents every agent from producing only a generic summary.

### 2.3 Fairer Multi-Model Comparison

When DeepSeek, Claude, Qwen, OpenAI, Kimi, or local models use the same meta-skills, differences become easier to compare:

- Did the model follow the same method?
- Did it miss a layer?
- Did it over-infer evidence?
- Did it produce better learning assets?
- Did it write better bilingual content?

## 3. Design Principles

- **Deterministic first**: collectors still own file discovery, inventory, hashes, paths, and evidence blocks.
- **Meta-skills guide interpretation**: they should not replace schemas or deterministic checks.
- **Small and composable**: each meta-skill should do one thing well.
- **Evidence-bound**: every meta-skill must include evidence rules.
- **Provider-neutral**: no skill should assume Claude/OpenAI-specific behavior unless explicitly marked.
- **Bilingual-ready**: outputs should support Chinese-first rendering and English toggle.
- **No recursive trap**: internal meta-skills should not be analyzed by default as target skills.
- **Report-aware but not report-bound**: meta-skills should produce artifacts that can render to web, vault, graph, and benchmark outputs.

## 4. Proposed Directory Layout

```text
skills/
  asa-skill-identity-decomposer/
    SKILL.md
  asa-trigger-boundary-mapper/
    SKILL.md
  asa-resource-role-analyzer/
    SKILL.md
  asa-workflow-trace-builder/
    SKILL.md
  asa-evidence-grounding-auditor/
    SKILL.md
  asa-reuse-pattern-miner/
    SKILL.md
  asa-reader-layer-writer/
    SKILL.md
  asa-model-comparison-judge/
    SKILL.md
```

Recommended metadata in each `SKILL.md`:

```yaml
---
name: asa-skill-identity-decomposer
description: Internal Agent Skill Anatomy method skill for decomposing skill identity.
internal_meta_skill: true
asa_role: structure_analyst
output_contract: structure_analysis.identity
---
```

Recommended sections:

```text
# Purpose
# When To Use
# Inputs
# Process
# Output Contract
# Evidence Rules
# Failure Modes
# Quality Rubric
# Examples
```

## 5. Meta-Skill Set

### 5.1 Skill Identity Decomposer

Purpose: determine what the skill is before analyzing how it runs.

Responsibilities:

- identify skill name, description, type, target agents, and final outputs
- distinguish workflow, tool, file, domain, governance, meta, and unknown skills
- write a one-line anatomy statement
- capture value proposition and user-facing purpose

Outputs:

```yaml
identity:
  one_line_zh:
  one_line_en:
  skill_type:
  target_agents: []
  primary_outputs: []
  value_proposition:
  confidence:
  evidence: []
```

Common failure modes:

- treating every skill as a workflow
- copying frontmatter without interpretation
- claiming target agents without source evidence

### 5.2 Trigger Boundary Mapper

Purpose: map when a skill should and should not be used.

Responsibilities:

- extract explicit trigger phrases
- infer semantic triggers with lower confidence
- identify negative triggers and non-goals
- detect boundary/risk conditions
- describe likely misfire cases

Outputs:

```yaml
activation:
  explicit_triggers: []
  semantic_triggers: []
  negative_triggers: []
  boundary_conditions: []
  misfire_risks: []
  evidence: []
```

Common failure modes:

- treating examples as universal triggers
- failing to identify “do not use” cases
- using high confidence for semantic inference

### 5.3 Resource Role Analyzer

Purpose: explain what every important file/resource does in the skill.

Responsibilities:

- classify `SKILL.md`, scripts, references, templates, assets, configs, schemas, examples, tests, and license files
- map each resource to a workflow stage
- mark must-read vs on-demand vs optional
- identify reusable resources and brittle dependencies

Outputs:

```yaml
resource_roles:
  - path:
    role:
    stage:
    read_policy: must_read | on_demand | optional | ignore
    reuse_value: high | medium | low | unknown
    risk:
    evidence: []
```

Common failure modes:

- listing files without responsibilities
- ignoring templates because they are not scripts
- treating license files as execution resources

### 5.4 Workflow Trace Builder

Purpose: reconstruct how user intent becomes a final artifact.

Responsibilities:

- build a step-by-step workflow
- identify actors: model, script, human, external tool, unknown
- map inputs, actions, outputs, resource usage, and downstream dependencies
- detect decision points, verification points, recovery paths, and stop conditions

Outputs:

```yaml
workflow_trace:
  summary:
  pipeline: []
  steps:
    - id:
      name:
      input:
      action:
      output:
      actor:
      resources: []
      downstream:
      confidence:
      inferred:
      evidence: []
  decision_points: []
  verification_points: []
  failure_modes: []
```

Common failure modes:

- inventing hidden steps
- merging resource loading and execution into one vague step
- not explaining why steps connect

### 5.5 Evidence Grounding Auditor

Purpose: decide whether the analysis is trustworthy.

Responsibilities:

- classify claims as explicit, structural, inferred, unsupported, or conflicting
- find missing evidence
- detect overlong quotes, vague evidence, and unsupported risk claims
- rate publishability

Outputs:

```yaml
evidence_audit:
  supported_claims: []
  inferred_claims: []
  unsupported_claims: []
  missing_evidence: []
  conflicts: []
  publishable:
  rationale:
```

Common failure modes:

- accepting model summary as evidence
- using file existence to prove behavior without caveat
- hiding unsupported claims because the report sounds good

### 5.6 Reuse Pattern Miner

Purpose: turn one or more skills into reusable assets.

Responsibilities:

- identify transferable design patterns
- write problem/solution/when-to-use/counterexample blocks
- extract templates, checklists, anti-patterns, and extension ideas
- mark whether a pattern is candidate or established

Outputs:

```yaml
reuse_assets:
  patterns: []
  templates: []
  checklists: []
  anti_patterns: []
  extension_ideas: []
```

Common failure modes:

- overgeneralizing from one skill
- copying skill content instead of abstracting method
- producing patterns that are too vague to reuse

### 5.7 Reader Layer Writer

Purpose: convert structured analysis into readable learning surfaces.

Responsibilities:

- write a beginner explanation layer
- write an expert implementation layer
- explain terms and reading order
- avoid repeating identical summary across sections
- keep Chinese default and English available

Outputs:

```yaml
reader_layers:
  beginner:
  expert:
  glossary: []
  reading_order: []
  report_notes: []
  obsidian_notes: []
```

Common failure modes:

- writing only for experts
- using unexplained terms like trigger/workflow/evidence
- repeating the same summary in hero, snapshot, and manual

### 5.8 Model Comparison Judge

Purpose: compare multiple model outputs on the same skill.

Responsibilities:

- compare completeness, grounding, workflow depth, pattern quality, bilingual quality, and Obsidian usefulness
- identify model disagreements and omissions
- mark which model is better for which role
- create benchmark-ready tables

Outputs:

```yaml
model_comparison:
  compared_runs: []
  per_model_scores: []
  disagreements: []
  omissions: []
  best_for_role:
  recommendation:
```

Common failure modes:

- treating different wording as disagreement
- ignoring evidence quality
- comparing outputs from different source commits

## 6. Mapping To Existing Agents

```text
structure_analyst
  uses:
    - asa-skill-identity-decomposer
    - asa-trigger-boundary-mapper
    - asa-resource-role-analyzer

workflow_analyst
  uses:
    - asa-workflow-trace-builder

reviewer
  uses:
    - asa-evidence-grounding-auditor

pattern_miner
  uses:
    - asa-reuse-pattern-miner

report_exporter / vault_exporter
  uses artifacts shaped by:
    - asa-reader-layer-writer

benchmark scripts
  uses:
    - asa-model-comparison-judge
```

The same meta-skill can be referenced by several agents, but only one agent should own writing each artifact field.

## 7. Prompt Integration Strategy

### Phase A: Documentation Only

Create meta-skill files but do not change runtime behavior. This establishes method and review language.

### Phase B: Prompt References

Inject meta-skill text into agent prompts as method context.

Example:

```text
Follow the internal method skill `asa-skill-identity-decomposer` for identity fields.
Follow `asa-trigger-boundary-mapper` for trigger and boundary fields.
Return only schema-valid JSON.
```

### Phase C: Context Loader

Add a deterministic loader that resolves meta-skill paths and includes only the relevant `SKILL.md` content for each agent.

Recommended config:

```yaml
meta_skills:
  enabled: true
  root: skills
  exclude_from_source_analysis: true
  agent_map:
    structure_analyst:
      - asa-skill-identity-decomposer
      - asa-trigger-boundary-mapper
      - asa-resource-role-analyzer
```

### Phase D: Schema Expansion

Expand artifacts to include richer outputs.

Candidate fields:

```yaml
structure_analysis:
  identity: {}
  activation: {}
  resource_roles: []
  reader_hints: {}

workflow_analysis:
  workflow_trace: {}
  pipeline: []
  implementation_map: []

review_report:
  evidence_audit: {}

patterns:
  reuse_assets: {}
```

### Phase E: Multi-Model Calibration

Run the same source skill with and without meta-skills, then compare:

- step count
- missing evidence
- unsupported claims
- reusable assets count
- report readability
- bilingual quality
- reviewer issue count

## 8. Runtime Guardrails

### 8.1 Avoid Recursive Analysis

Internal meta-skills should not be target skills by default.

Rules:

- exclude `internal_meta_skill: true`
- exclude paths matching `skills/asa-*`
- allow explicit override with `--include-internal-skills`

### 8.2 Control Context Size

Meta-skill `SKILL.md` files should be concise. Examples and long rubrics should move to `references/` and only load when needed.

### 8.3 Preserve Deterministic Authority

Meta-skills must not override deterministic facts such as:

- file paths
- hashes
- repository metadata
- source commit
- collected inventory
- evidence block IDs

### 8.4 Schema Is Still The Contract

Meta-skills guide reasoning, but schemas decide what can be persisted.

## 9. Quality Evaluation

A meta-skill-enhanced run should be better on at least three axes:

- **Completeness**: more layers filled without hallucination.
- **Grounding**: fewer unsupported claims and clearer evidence types.
- **Readability**: better beginner/expert explanation separation.
- **Reuse**: more actionable templates/checklists/patterns.
- **Comparison**: clearer model differences on same source.

Suggested before/after benchmark:

```text
source: anthropics/skills
skill: algorithmic-art
models:
  - deepseek-v4-pro
  - deepseek-v4-flash
variants:
  - baseline prompts
  - meta-skills enabled
metrics:
  - workflow_steps
  - evidence_score
  - reviewer_issues
  - reusable_assets
  - reader_layer_quality
  - obsidian_score
```

## 10. Implementation Plan

### Step 1: Create Meta-Skill Documents

Status: complete for the initial 8-skill method set.

- Added internal `skills/asa-*` directories for identity, trigger/boundary, resource roles, workflow tracing, evidence auditing, reuse mining, reader layering, and model comparison.
- Wrote concise `SKILL.md` contracts for all 8 method skills.
- Marked each method skill as `internal_meta_skill: true`.

### Step 2: Exclude Internal Meta-Skills From Source Discovery

Status: complete for default discovery.

- Collector excludes `internal_meta_skill: true`.
- Collector excludes `skills/asa-*` as a deterministic path guardrail.
- Regression tests cover frontmatter exclusion and path-prefix exclusion.
- Explicit override remains future work if benchmark scenarios need to analyze internal method skills directly.

### Step 3: Prompt-Level Integration

Status: complete for the initial 8-skill method set.

- Added a deterministic `asa.meta_skills` loader.
- Appended relevant internal method skills to `structure_analyst`, `workflow_analyst`, `reviewer`, and `pattern_miner` system prompts.
- Registered reader-layer and model-comparison methods for exporters and benchmark helpers.
- Kept schemas, user payloads, CLI commands, and provider interfaces unchanged.
- Added regression coverage confirming method context reaches Agent provider calls and every mapped method skill exists.

### Step 4: Schema Expansion

Status: complete for first-pass optional method fields.

- Added optional schema support for `identity`, `activation`, `resource_roles`, `workflow_trace`, `evidence_audit`, and `reuse_assets`.
- Kept old artifacts valid; exporters prefer new fields and fall back to legacy structure/workflow/review fields.

### Step 5: Real Run Calibration

Status: partially complete.

- Completed a DeepSeek V4 Pro real run for `anthropics/skills` → `algorithmic-art` at `runs/20260613T183941Z`.
- Exported report, vault, data, and graph-ready artifacts under `dist/deepseek-v4-pro-manual/`.
- Follow-up calibration remains: rerun the same source after meta-skill prompt integration, then compare against Flash and at least one additional model.

### Step 6: Report/Vault/Data/Graph Upgrade

Status: complete for the first integrated output pass.

- Web Report renders method layer, resource roles, workflow trace, evidence audit, and reuse assets.
- Obsidian Vault mirrors method layer, evidence audit, reuse assets, and workflow trace details.
- Data export writes flattened JSONL/CSV files for skills, resource roles, workflow trace, evidence audit, and reuse assets.
- Graph export writes canonical `graph-data.json` and `graph.mmd` from the same data rows.

## 11. Closed Design Defaults

The meta-skill layer now uses these working decisions:

- Meta-skills are versioned as a method pack, starting with `asa-meta-skills-v1`.
- Meta-skills influence existing stage schemas first; separate schemas are only added when comparison/calibration proves a new artifact is needed.
- Custom user meta-skills are allowed later through an explicit opt-in directory, not through default source discovery.
- Benchmark and comparison reports must show whether meta-skills were enabled and which pack size was used.
- Small-context or fast domestic models receive compact method packs; high-quality runs can use standard/full packs.

Detailed runtime design: `docs/llm-skill-integration-design.md`.

## 12. Recommended Next Work
The implementation foundation is now in place. Recommended next work is calibration and productization rather than more method scaffolding:

1. Run a fresh before/after benchmark with meta-skills enabled versus the earlier DeepSeek V4 Pro baseline.
2. Compare DeepSeek V4 Pro, DeepSeek Flash, Claude, Qwen, and one OpenAI-compatible model on the same skill source.
3. Surface `graph-data.json` in the Graph UI with edge filtering by relation type and confidence.
4. Add a local WebUI/API path that writes provider config safely without storing keys in generated artifacts.
5. Decide whether custom user meta-skills should be allowed, and if so, keep them separate from internal `skills/asa-*`.


