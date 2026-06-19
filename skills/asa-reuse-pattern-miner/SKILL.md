---
name: asa-reuse-pattern-miner
description: Use when extracting reusable patterns, templates, checklists, anti-patterns, and transfer rules from analyzed skills.
internal_meta_skill: true
asa_role: pattern_miner
output_contract: patterns.reuse_assets + letuen.reuse_anchors
---

# ASA Reuse Pattern Miner

Use this internal meta-skill when a model must convert one or more analyzed skills into reusable design assets.

This skill fixes the failure mode where pattern mining becomes a loose summary instead of reusable anchors, composition candidates, anti-patterns, and optional solidification templates that another author can apply.

## Inputs

- Skill summaries and source paths.
- Structure analysis, workflow analysis, and reviewer outputs.
- Resource roles, workflow steps, evidence strength, and reusable artifacts.
- Optional model comparison notes when available.

## Process

1. Identify mechanisms that can transfer beyond one repository.
2. Separate concrete implementation details from reusable design principles.
3. For each candidate pattern, write problem, solution, when-to-use, counterexample, and evidence.
4. Mark pattern maturity as `candidate`, `emerging`, or `established` based on example count and mechanism similarity.
5. Extract checklists only when steps are actionable.
6. Extract templates only when placeholders and usage boundaries are clear.
7. Record anti-patterns when the source exposes a likely failure mode.
8. Convert transferable mechanisms into reuse, composition-candidate, anti-pattern, and solidification-template anchors.
9. Avoid copying source text; abstract the method and point back to evidence.

## Output Contract

Return reusable assets suitable for `patterns.json` and Obsidian notes:

```yaml
reuse_assets:
  patterns: []
  templates: []
  checklists: []
  anti_patterns: []
  extension_ideas: []
  anchors:
    reuse_anchor:
      - id:
        name:
        problem:
        reusable_mechanism:
        when_to_use: []
        when_not_to_use: []
        source_patterns: []
        reuse_modes:
          - reference_only
          - temporary_composition
          - prompt_patch
          - workflow_step
          - learning_note
        portability: high | medium | low
        confidence: high | medium | low | unknown
        evidence: []
    composition_candidate_anchor:
      - id:
        name:
        selected_anchors: []
        composition_form: reference_only | temporary_composition | prompt_patch | agent_rule_patch | workflow_insert | tool_adapter | template_pack | quality_gate | learning_note | full_workflow_blueprint | new_skill_spec
        user_goal:
        expected_output:
        required_adapters: []
        conflict_risks: []
        preserve_existing_skills: true
        solidification_required: true | false
        confidence: high | medium | low | unknown
        evidence: []
    anti_pattern_anchor:
      - id:
        name:
        failure_mode:
        appears_when: []
        avoid_by: []
        affected_anchor_types: []
        severity: high | medium | low
        evidence: []
    solidification_template_anchor:
      - id:
        name:
        target_form: full_workflow_blueprint | new_skill_spec | template_pack | quality_gate
        use_only_when: []
        required_sections: []
        required_anchors: []
        optional_anchors: []
        non_destructive_output:
        rollback_note:
        evidence: []
```


## Anchor Output Rules

Emit anchors that let users split, borrow, combine, or optionally solidify useful parts of a skill without forcing a full workflow.

- `reuse_anchor`: a transferable mechanism that can stand alone as a note, prompt patch, checklist, or workflow step.
- `composition_candidate_anchor`: a suggested combination of anchors for a concrete user goal, with composition form and conflict risks.
- `anti_pattern_anchor`: a reusable warning that prevents bad recombination, overgeneralization, or unsafe copying.
- `solidification_template_anchor`: an optional template for turning selected anchors into a larger workflow, quality gate, template pack, or new skill.

A composition candidate must state whether solidification is required. Default to `solidification_required: false` unless the selected goal cannot work as a temporary composition. Preserve existing user skills by default and represent conflicts as risks or adapters, not overwrites.

## Evidence Rules

- Every pattern example should include `skill_id`, `source_path`, and evidence when available.
- A one-skill pattern is only a `candidate` unless there is strong external evidence.
- Similar names are not enough; compare mechanism, workflow role, and resource usage.
- If reviewer confidence is low, downgrade pattern confidence.

## Failure Modes

- Do not overgeneralize from one skill.
- Do not create generic advice that cannot be applied.
- Do not call a pattern established without multiple matching examples.
- Do not copy examples as templates without explaining how to adapt them.

## Quality Rubric

A strong reuse pattern asset answers:

- What problem does this pattern solve?
- What mechanism makes it reusable?
- When should it not be used?
- What evidence shows the mechanism works in the analyzed skill?

