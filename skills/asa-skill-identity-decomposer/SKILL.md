---
name: asa-skill-identity-decomposer
description: Use when you need to identify purpose, type, target agent, primary outputs, and core identity before workflow analysis.
internal_meta_skill: true
asa_role: structure_analyst
output_contract: structure_analysis.identity
---

# ASA Skill Identity Decomposer

Use this internal meta-skill when a model must determine the identity, purpose, type, target agent, and primary outputs of a skill package.

This skill fixes the failure mode where an analyst copies frontmatter or jumps directly into workflow without first explaining what the skill actually is.

## Inputs

- Deterministic inventory for one skill package.
- `SKILL.md` frontmatter and core body blocks.
- Package file list and detected resource roles.
- Existing evidence objects when available.

## Process

1. Read the skill name and description from frontmatter.
2. Identify the user problem the skill claims to solve.
3. Classify the primary skill type: `file`, `tool`, `workflow`, `meta`, `domain`, `governance`, or `unknown`.
4. Identify secondary tags only when supported by wording or file structure.
5. Identify target agents only when explicitly named or strongly implied by source context.
6. Identify primary outputs and distinguish final outputs from intermediate artifacts.
7. Write one concise anatomy sentence in Chinese and English.
8. Attach evidence to each high-confidence identity claim.

## Output Contract

Return identity content suitable for `structure_analysis.json`:

```yaml
identity:
  one_line:
    zh:
    en:
  skill_type:
    primary:
    secondary: []
  target_agents: []
  primary_outputs: []
  value_proposition:
    zh:
    en:
  confidence:
    overall:
    notes:
  evidence: []
```


## Anchor-Aware Output

In addition to identity content, emit minimal anchor cards when the source supports them. Keep this lightweight; do not generate a full composition plan from this skill.

Recommended anchor types:

- `identity_anchor`: what the skill is and what problem it solves.
- `value_anchor`: the primary capability or value unit worth borrowing.
- `output_anchor`: final or intermediate output shapes.
- `target_user_anchor`: explicit or strongly implied target agent/user.

Minimal anchor card shape:

```yaml
anchors:
  - id: anchor.<skill_id>.identity
    source_skill_id:
    anchor_type: identity_anchor
    name:
    summary:
    evidence:
      path:
      quote:
    confidence: low | medium | high
    reuse_modes:
      - reference_only
      - temporary_composition
      - learning_note
    risks: []
```

Anchor rules:

- Emit only anchors supported by frontmatter, body text, or deterministic inventory.
- Use `medium` or `low` confidence for inferred target users.
- Do not emit workflow anchors from this skill; workflow anchors belong to the workflow trace method.
- Do not plan composition here; pass anchors to `asa-anchor-composition-planner`.

## Evidence Rules

- Use `explicit` evidence for frontmatter name, description, and directly stated outputs.
- Use `structural` evidence for file-layout conclusions.
- Use `inferred` evidence for target agent or value proposition when not directly stated.
- Do not mark target agents as high confidence unless source text or repository context supports it.

## Failure Modes

- Do not treat every skill as a workflow.
- Do not replace identity analysis with a raw frontmatter copy.
- Do not invent audience or target agent from project popularity.
- Do not claim final outputs from examples unless the skill asks the agent to produce them.

## Quality Rubric

A strong identity decomposition answers:

- What is this skill?
- Who or what is it for?
- What problem does it solve?
- What does it produce?
- What source evidence supports those claims?





