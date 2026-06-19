---
name: asa-workflow-trace-builder
description: Use when reconstructing how a skill converts user intent into outputs through ordered steps, resources, and evidence.
internal_meta_skill: true
asa_role: workflow_analyst
output_contract: workflow_analysis.workflow_trace + letuen.workflow_anchors
---

# ASA Workflow Trace Builder

Use this internal meta-skill when a model must reconstruct a skill workflow from user request to final delivery.

This skill fixes the failure mode where workflow analysis becomes a vague list of actions without inputs, outputs, resource usage, actor responsibility, evidence, or reusable workflow anchors.

## Inputs

- Structure analysis for one skill package.
- `SKILL.md` ordered steps, headings, rules, warnings, and output instructions.
- Resource role analysis when available.
- Source snapshot and evidence blocks.

## Process

1. Start from the user intent or task trigger.
2. Identify each step in execution order.
3. For every step, state input, action, output, actor, resources, confidence, and whether it is inferred.
4. Map how each step enables the next step.
5. Extract workflow anchors from reusable step chains, handoffs, replaceable steps, validation gates, and output transitions.
6. Extract decision points, verification points, failure modes, recovery paths, and stop conditions.
7. Separate model actions from script/tool/human/external actions.
8. Build a short pipeline for visual reports and a full step list for detailed reports.
9. Attach evidence to every high-confidence step and every proposed anchor.

## Output Contract

Return workflow trace content suitable for `workflow_analysis.json`:

```yaml
workflow_trace:
  summary:
    zh:
    en:
  pipeline: []
  steps:
    - id:
      name:
        zh:
        en:
      input:
      action:
      output:
      actor: model | script | human | external_tool | unknown
      resources: []
      downstream:
      confidence: high | medium | low | unknown
      inferred: true | false
      evidence: []
  decision_points: []
  verification_points: []
  failure_modes: []
  anchors:
    workflow_anchor:
      - id:
        name:
        description:
        source_steps: []
        reusable_as: prompt_patch | checklist | mini_skill | workflow_module | reference_pattern
        required_inputs: []
        produced_outputs: []
        dependencies: []
        confidence: high | medium | low | unknown
        evidence: []
    handoff_anchor:
      - id:
        from_step:
        to_step:
        handoff_object:
        contract:
        failure_if_missing:
        confidence: high | medium | low | unknown
        evidence: []
    replaceable_step_anchor:
      - id:
        step_id:
        replace_with:
        safe_when:
        unsafe_when:
        user_control: keep_original | choose_alternative | remove | defer
        confidence: high | medium | low | unknown
        evidence: []
    validation_step_anchor:
      - id:
        step_id:
        validation_target:
        pass_signal:
        fail_signal:
        repair_action:
        confidence: high | medium | low | unknown
        evidence: []
    output_transition_anchor:
      - id:
        from_output:
        to_surface:
        transformation:
        preserves: []
        risks: []
        confidence: high | medium | low | unknown
        evidence: []
```


## Anchor Output Rules

Emit anchors only when they help a user borrow, recombine, or simplify the workflow without copying the whole skill.

- `workflow_anchor`: a reusable chain of two or more steps with clear inputs and outputs.
- `handoff_anchor`: a transition contract where one step hands a concrete object to another step.
- `replaceable_step_anchor`: a step that can be swapped, skipped, or delegated without breaking the whole method.
- `validation_step_anchor`: a verification gate that can be reused as a quality rule.
- `output_transition_anchor`: a conversion from analysis output into a reader, report, Obsidian, repo, UI, or other surface.

Each anchor must include source step ids, evidence, confidence, and user-control guidance when replacement is possible. Do not force anchors into a solidified workflow; anchors may remain standalone notes, temporary compositions, or optional modules.

## Evidence Rules

- Explicit ordered steps in source text can be high confidence.
- Steps inferred from adjacent instructions must use `inferred: true`.
- Resource usage should cite either source instruction or resource role evidence.
- Mermaid or pipeline output must not add steps that are absent from the structured step list.

## Failure Modes

- Do not invent hidden execution steps to make the workflow look complete.
- Do not merge planning, context loading, execution, and validation into one vague step.
- Do not claim script execution when the skill only provides a template or reference.
- Do not omit failure modes when the source contains warnings or constraints.

## Quality Rubric

A strong workflow trace lets a reader answer:

- What happens first, next, and last?
- What does each step consume and produce?
- Who performs each step?
- What resources are used?
- How is the result verified or delivered?

