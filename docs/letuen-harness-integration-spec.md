# LetUen Harness Integration Spec

This document defines how the LetUen Skill Anchor Pack plugs into a host project without breaking existing skills, workflows, or user conventions. Harness compliance is the key requirement for reliable skill composition.


## 0. Lightweight Harness Profile

Harness integration should start small:

- L1 extracts anchor notes only.
- L2 creates a composition plan and dispatch policy only when needed.
- L3 applies changes to a project only after explicit approval.

The harness should not require full compatibility matrices, dry-run diffs, or rollback logs unless the user asks to persist or apply changes.

## 1. Harness Responsibilities

The harness is responsible for safe orchestration. Individual skills may propose anchors or compositions, but the harness decides how they are staged, validated, exported, and optionally applied.

The harness must:

- discover source skills without mutating them;
- preserve original skill directory structure;
- assign stable IDs to source skills and anchors;
- attach source evidence to every anchor;
- validate anchor schemas before downstream use;
- detect trigger and resource conflicts;
- select composition forms from user intent;
- export non-destructive artifacts by default;
- require explicit approval before writing into user skill directories;
- keep a reversible record of every patch or generated asset.

## 2. Harness State Machine

```text
collect_sources
  -> detect_skills
  -> snapshot_existing_user_skills
  -> decompose_to_anchors
  -> validate_anchors
  -> score_portability_and_risk
  -> detect_conflicts
  -> plan_composition
  -> dry_run_outputs
  -> export_selected_form
  -> optional_apply
```

`optional_apply` is disabled by default.

## 3. Required Inputs

```yaml
source_skills:
  - skill_id
  - path
  - source_kind: local | github | registry | generated
existing_user_skills:
  - skill_id
  - path
  - trigger_summary
  - scope_summary
user_goal:
  type: composition_form
  description: string
harness_policy:
  preserve_existing_skill_structure: true
  dry_run_first: true
  require_approval_for_mutation: true
  default_dispatch_policy: ask_user
```

## 4. Required Outputs

```text
runs/<run-id>/
  anchors/
    anchors.json
    anchors.jsonl
    anchor_graph.json
  composition/
    composition_request.json
    anchor_selection.json
    compatibility_matrix.json
    composition_plan.json
    dispatch_policy.json
    dry_run_diff.md
    outputs/
      <selected-form-artifacts>
```

## 5. Harness Quality Gates

| Gate | Requirement |
|---|---|
| Schema gate | anchors and plans validate before export |
| Evidence gate | high-confidence anchors require explicit evidence |
| Conflict gate | trigger/resource/output conflicts produce dispatch policy |
| Non-destructive gate | no existing user skill is modified without approval |
| Reversibility gate | every applied change has rollback instructions |
| Form gate | output matches selected composition form |
| Scope gate | temporary composition does not leak into persistent workflow files |

## 6. Trigger Conflict Detection

The harness must compare LetUen-generated triggers with existing user skill triggers.

Conflict categories:

- `exact_overlap`: same trigger wording or same narrow task.
- `semantic_overlap`: different wording but same user intent.
- `broad_shadowing`: LetUen trigger is too broad and may capture existing skill requests.
- `handoff_gap`: neither skill clearly owns the transition.
- `priority_conflict`: both skills claim first response responsibility.

Every conflict must be represented in `dispatch_policy.json`.

## 7. Dispatch Policies

Allowed dispatch policies:

| Policy | Use When |
|---|---|
| `prefer_existing_skill` | User already has a skill with matching trigger |
| `prefer_letuen_composition` | User explicitly asks to use composed anchors |
| `ask_user` | Conflict is ambiguous or high-risk |
| `route_by_anchor_type` | Existing skill handles one anchor type, LetUen handles another |
| `run_both_then_compare` | Useful during testing or model comparison |
| `disabled` | Composition should not auto-trigger |

Default is `ask_user` or `prefer_existing_skill` for existing user workflows.

## 8. Resource Conflict Detection

The harness must detect when anchors require resources that are missing, incompatible, or dangerous to copy.

Resource statuses:

- `portable`: safe to copy/reference.
- `reference_only`: can be read but not copied.
- `requires_adapter`: needs path, runtime, or API adaptation.
- `hard_dependency`: composition fails without it.
- `unsafe_to_copy`: license, secret, or environment risk.

## 9. Optional Apply Protocol

Applying a composition to a project must follow this sequence:

1. produce dry-run diff;
2. list affected files;
3. list trigger changes;
4. list rollback steps;
5. ask for explicit approval;
6. write sidecar files first;
7. only mutate existing files if explicitly approved;
8. write `letuen-apply-log.json`.

## 10. Harness-Native UX

The UI or CLI should ask:

- Do you want temporary composition or persistent output?
- Should existing skills have priority?
- Which anchor types do you want?
- Are file writes allowed?
- Should this become a new skill, a patch, a note, or a workflow insert?

LetUen should never assume that a user wants a full workflow.



