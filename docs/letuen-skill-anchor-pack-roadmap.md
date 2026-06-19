# LetUen Skill Anchor Pack Roadmap

This roadmap upgrades the current eight internal meta-skills into a standalone LetUen Skill Anchor Pack.

## v0.1.0 Current State

- Eight internal method skills are packaged; a ninth planner-only skill is now staged for v0.2.0 development.
- Each skill has trigger-first frontmatter.
- Package can be installed locally.
- The skills are still primarily analysis-stage methods.


## Lightweight Implementation Rule

Do not implement the full pack all at once. The next implementation step should be small:

1. Add `asa-anchor-composition-planner` as a planner-only skill.
2. Update existing skills to emit minimal anchor cards. ✅ identity decomposer emits identity/value/output anchors; trigger mapper emits trigger/boundary/handoff anchors; resource analyzer emits resource/template/tool/dependency anchors; workflow trace builder emits workflow/handoff/replaceable-step/validation/output-transition anchors; evidence auditor emits evidence/risk/confidence/unsupported-claim anchors; reuse miner emits reuse/composition-candidate/anti-pattern/solidification-template anchors; reader layer writer emits anchor-card/learning-note/operator-guide anchors; model comparison judge emits consensus/disagreement/best-model-per-anchor-type anchors
3. Validate L1 anchor notes before implementing L2 composition plans.
4. Add compatibility matrix only after real overlap examples exist.
5. Add project apply only after non-destructive dry-run behavior is stable.
## v0.2.0 Target

Goal: turn the package into an anchor-aware decomposition and composition pack.

Required changes:

1. Add `asa-anchor-composition-planner`. ✅ initial planner-only skill added
2. Add `ANCHOR_SCHEMA.md` to release package.
3. Add `COMPOSITION_FORMS.md` to release package.
4. Add `CALL_ORDER.md` to release package.
5. Update existing skills to emit or consume anchors. ✅ all internal method skills now emit or consume minimal LetUen anchors for v0.2.0 development.
6. Add examples for at least one real decomposed skill. ✅ sample-skill anchor composition example added
7. Add harness compatibility notes and non-destructive invocation policy. ✅ export-anchors, plan-composition, and export-letuen CLI paths added

## v0.3.0 Target

Goal: support project-level composition dry-runs.

Required changes:

1. Generate `.letuen/compositions/<id>/` sidecar outputs.
2. Generate dispatch policies for trigger overlap.
3. Generate dry-run diffs for optional application.
4. Export Obsidian anchor cards.
5. Add compatibility matrix visualization using Obsidian native links and Graph View.

## Release Package Structure

```text
letuen-skill-anchor-pack/
  README.md
  CALL_ORDER.md
  ANCHOR_SCHEMA.md
  COMPOSITION_FORMS.md
  HARNESS_INTEGRATION.md
  NON_DESTRUCTIVE_INVOCATION.md
  examples/
    algorithmic-art/
      anchors.json
      composition_request.prompt_patch.yaml
      composition_plan.prompt_patch.yaml
  skills/
    asa-anchor-composition-planner/
    asa-skill-identity-decomposer/
    asa-trigger-boundary-mapper/
    asa-resource-role-analyzer/
    asa-workflow-trace-builder/
    asa-evidence-grounding-auditor/
    asa-reuse-pattern-miner/
    asa-reader-layer-writer/
    asa-model-comparison-judge/
```

## Acceptance Criteria

- User can choose temporary composition without generating a workflow.
- User can generate a new skill without modifying existing skills.
- Trigger conflicts produce a dispatch policy.
- Existing user skills remain primary by default.
- Every selected anchor has evidence and risk metadata.
- Obsidian output uses native links and Graph View rather than custom graph clutter.




