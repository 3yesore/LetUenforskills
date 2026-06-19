---
name: asa-anchor-composition-planner
description: Use when selecting and composing skill anchors into a chosen reuse form without assuming a full workflow is required.
internal_meta_skill: true
asa_role: composition_planner
output_contract: composition.anchor_plan
---

# ASA Anchor Composition Planner

Use this internal meta-skill when LetUen has extracted anchors and must decide how to combine them for a user goal without forcing workflow solidification.

This skill fixes the failure mode where every useful skill fragment is turned into a heavy new workflow or new skill even when the user only wants a temporary composition, prompt patch, rule patch, learning note, or partial workflow insert.

## Inputs

- Minimal Anchor Cards or normalized anchors.
- User composition goal and preferred reuse form.
- Existing user skill snapshot when available.
- Trigger overlap and resource conflict notes when available.
- Evidence and risk scores from reviewer/auditor stages.
- Target agent or host project constraints.

## Process

1. Identify the user's requested reuse form before selecting anchors.
2. Prefer the lightest useful output: `reference_only`, `temporary_composition`, `prompt_patch`, or `learning_note` unless the user asks for persistence.
3. Select anchors whose `reuse_modes` match the requested form.
4. Reject anchors with missing hard dependencies unless an adapter is explicitly available.
5. Detect trigger overlap with existing user skills and choose a dispatch policy.
6. Keep existing user skills primary by default when overlap is ambiguous.
7. Produce a non-destructive plan that can be reviewed before any file changes.
8. Escalate to workflow or new skill output only when explicitly requested.

## Output Contract

Return a planner-only composition plan suitable for `composition_plan.json`:

```yaml
schema_version: 1
composition_form: reference_only | temporary_composition | prompt_patch | agent_rule_patch | workflow_insert | tool_adapter | template_pack | quality_gate | learning_note | full_workflow_blueprint | new_skill_spec
summary:
  zh:
  en:
selected_anchors:
  - anchor_id:
    reason:
    selected_reuse_mode:
rejected_anchors:
  - anchor_id:
    reason:
conflicts:
  - conflict_type: trigger_overlap | resource_missing | output_mismatch | runtime_assumption | none
    description:
    resolution:
dispatch_policy:
  mode: prefer_existing_skill | prefer_letuen_composition | ask_user | route_by_anchor_type | run_both_then_compare | disabled
  reason:
outputs:
  - kind: prompt_patch | agent_rule_patch | workflow_insert | tool_adapter | template_pack | quality_gate | learning_note | full_workflow_blueprint | new_skill_spec
    path:
    destructive: false
    reversible: true
solidification:
  requested: false
  reason:
next_steps: []
```

## Lightweight Rules

- Do not require a full compatibility matrix for L1 anchor notes.
- Do not produce dry-run diffs unless the user asks to apply changes to a project.
- Do not generate a new skill unless the requested form is `new_skill_spec`.
- Do not modify existing user skills.
- Do not enable auto-trigger behavior by default.

## Dispatch Defaults

- Use `prefer_existing_skill` when a user skill already owns the same trigger.
- Use `ask_user` when trigger ownership is unclear.
- Use `route_by_anchor_type` when LetUen contributes only a validation, resource, or template anchor.
- Use `disabled` for reference-only and learning-note outputs.

## Failure Modes

- Do not treat anchor composition as workflow generation by default.
- Do not hide rejected anchors.
- Do not ignore trigger conflicts.
- Do not claim a composition is safe without evidence and risk metadata.
- Do not mutate project files from this planner skill.

## Quality Rubric

A strong anchor composition plan answers:

- What is the user's lightest useful reuse form?
- Which anchors are selected and why?
- Which anchors were rejected and why?
- Does this conflict with existing user skills?
- Is this temporary, embedded, or solidified?
- What should the harness export next without destructive changes?
