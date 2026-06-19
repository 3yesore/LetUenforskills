# LetUen Anchor Schema

This document defines the canonical data contracts for LetUen anchors and compositions. These schemas are intentionally harness-oriented: every anchor must be traceable, composable, reversible, and safe to project into a user's repository without mutating existing skills by default.


## 0. Schema Weight Policy

LetUen uses two schema weights:

- **Minimal Anchor Card**: used for L1 extraction, UI display, Obsidian notes, and quick composition.
- **Normalized Anchor Contract**: used for exports, project integration, model comparison, and persistent composition.

The full contract below should not be forced into every prompt or UI card. The harness may progressively enrich minimal anchors as the user moves from L1 to L2 or L3.

### Minimal Anchor Card

```yaml
id: string
source_skill_id: string
anchor_type: string
name: string
summary: string
evidence:
  path: string
  quote: string
confidence: low | medium | high
reuse_modes:
  - reference_only
  - temporary_composition
risks:
  - string
```

## 1. Skill Anchor

```yaml
schema_version: 1
id: anchor.<source_skill_id>.<local_name>
source_skill_id: string
source_skill_name: string
source_package_path: string
anchor_type: trigger_anchor | boundary_anchor | resource_anchor | instruction_anchor | workflow_anchor | tool_anchor | template_anchor | evidence_anchor | validation_anchor | output_anchor | reuse_anchor | risk_anchor
name:
  zh: string
  en: string
description:
  zh: string
  en: string
source_evidence:
  - path: string
    quote: string
    evidence_type: explicit_instruction | inferred_from_structure | resource_reference | workflow_order | output_contract | reviewer_note
    confidence: low | medium | high
portability:
  score: low | medium | high
  reasons:
    - string
risk:
  score: low | medium | high
  notes:
    - string
requires:
  anchors:
    - anchor_id
  resources:
    - path_or_uri
  tools:
    - tool_name
  environment:
    - env_or_runtime_requirement
compatible_with:
  anchor_types:
    - anchor_type
  anchors:
    - anchor_id
incompatible_with:
  anchor_types:
    - anchor_type
  anchors:
    - anchor_id
reuse_modes:
  - reference_only
  - temporary_composition
  - prompt_fragment
  - agent_rule_patch
  - embedded_in_existing_workflow
  - workflow_step
  - tool_adapter
  - template_pack
  - quality_gate
  - learning_note
  - full_workflow
  - new_skill
harness_contract:
  input_shape: object | markdown | file_path | command | none
  output_shape: object | markdown | file_path | command | none
  side_effects: none | reads_files | writes_files | runs_commands | network
  requires_user_approval: boolean
  reversible: boolean
composition_notes:
  zh: string
  en: string
```

## 2. Composition Request

A composition request captures what the user wants. It prevents LetUen from assuming that full workflow solidification is desired.

```yaml
schema_version: 1
goal:
  type: reference_only | temporary_composition | prompt_patch | agent_rule_patch | workflow_insert | tool_adapter | template_pack | quality_gate | learning_note | full_workflow_blueprint | new_skill_spec
  description: string
constraints:
  avoid_full_workflow: boolean
  preserve_existing_skill_structure: true
  target_agent: codex | claude | cursor | gemini | generic
  target_project_path: string | null
  allowed_side_effects:
    - none
    - reads_files
    - writes_files
    - runs_commands
  require_dry_run: boolean
selected_anchor_types:
  - anchor_type
selected_source_skills:
  - skill_id
excluded_source_skills:
  - skill_id
preferred_outputs:
  - markdown
  - json
  - patch
  - skill_directory
  - obsidian_note
```

## 3. Anchor Selection

```yaml
schema_version: 1
request_id: string
selected_anchors:
  - anchor_id: string
    reason: string
    evidence_confidence: low | medium | high
    portability_score: low | medium | high
    risk_score: low | medium | high
    selected_reuse_mode: string
rejected_anchors:
  - anchor_id: string
    reason: string
missing_anchors:
  - need: string
    reason: string
```

## 4. Compatibility Matrix

```yaml
schema_version: 1
anchors:
  - anchor_id
matrix:
  - left_anchor: anchor_id
    right_anchor: anchor_id
    compatibility: incompatible | risky | compatible | strong_fit
    dimensions:
      trigger_fit: low | medium | high
      resource_fit: low | medium | high
      workflow_fit: low | medium | high
      output_fit: low | medium | high
      risk_fit: low | medium | high
      user_value: low | medium | high
    conflicts:
      - string
    required_adapters:
      - string
    notes: string
```

## 5. Composition Plan

```yaml
schema_version: 1
request_id: string
composition_form: string
summary:
  zh: string
  en: string
anchors:
  - anchor_id
execution_order:
  - anchor_id
adapters:
  - name: string
    purpose: string
    input_anchor: anchor_id
    output_anchor: anchor_id
outputs:
  - path: string
    kind: prompt_patch | agent_rule_patch | workflow_insert | tool_adapter | template_pack | quality_gate | learning_note | full_workflow_blueprint | new_skill_spec
    destructive: false
    reversible: true
harness_policy:
  dispatch_policy: prefer_existing_skill | prefer_letuen_composition | ask_user | run_both_then_compare | disabled
  conflict_resolution: string
  dry_run_required: boolean
```

## 6. Validation Rules

- Every anchor must have at least one evidence item or be explicitly marked as inferred with non-high confidence.
- Every composition must state whether it is temporary, embedded, or solidified.
- Every output must be non-destructive by default.
- Any trigger overlap must produce a dispatch policy.
- Any file write must be represented as a reversible patch or a new sidecar file unless the user explicitly approves mutation.


