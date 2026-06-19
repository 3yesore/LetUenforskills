# LetUen Anchor Composition Planner Spec

The anchor composition planner is the future ninth built-in method skill for LetUen. It coordinates anchor selection and composition without assuming the user wants a full workflow.

## 1. Proposed Skill

```yaml
name: asa-anchor-composition-planner
description: Use when selecting and composing skill anchors into a chosen reuse form without assuming a full workflow is required.
internal_meta_skill: true
asa_role: composition_planner
output_contract: composition.anchor_plan
```

## 2. Inputs

- `anchors.json` or `anchors.jsonl`
- user composition request
- existing user skill snapshot
- trigger conflict report
- resource compatibility report
- evidence/risk audit results
- target agent/runtime constraints

## 3. Process

1. Read the user goal and identify desired composition form.
2. Filter anchors by selected source skills, anchor types, reuse modes, evidence confidence, and risk tolerance.
3. Reject anchors that require unavailable resources or unsafe side effects.
4. Build compatibility matrix across selected anchors.
5. Detect trigger, resource, workflow, output, and validation conflicts.
6. Select dispatch policy for overlaps with existing user skills.
7. Generate non-destructive composition outputs.
8. Mark whether the result is temporary, embedded, or solidified.
9. Produce rollback information if any persistent output is requested.

## 4. Outputs

```yaml
schema_version: 1
composition_form: string
selected_anchors:
  - anchor_id
rejected_anchors:
  - anchor_id
compatibility_matrix: path
dispatch_policy: path
outputs:
  - path
    kind: string
    destructive: false
    reversible: true
solidification:
  requested: boolean
  reason: string
  approved: boolean
next_steps:
  - string
```

## 5. Planner Principles

- Do not optimize for a full workflow unless requested.
- Prefer existing user skills when triggers overlap.
- Prefer anchor-level composition over whole-skill replacement.
- Always separate recommendation, dry-run, and apply.
- Always preserve source evidence.
- Always make rejected anchors visible.

## 6. Example Use Cases

### Temporary Composition

User wants to borrow a resource loading anchor from one skill and a validation anchor from another for a one-off task.

Output:

- session prompt bundle
- selected anchors
- no persistent files

### Agent Rule Patch

User wants to add selected trigger/boundary anchors to an existing Codex rules file.

Output:

- sidecar rule patch
- dry-run diff
- dispatch policy
- rollback steps

### New Skill Spec

User wants to turn selected anchors into a new skill.

Output:

- new skill directory
- `SKILL.md`
- references/scripts copied only when portable
- conflict report
