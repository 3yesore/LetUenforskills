---
name: asa-trigger-boundary-mapper
description: Use when mapping when a skill should activate, when it should not activate, and what boundaries constrain safe use.
internal_meta_skill: true
asa_role: structure_analyst
output_contract: structure_analysis.activation
---

# ASA Trigger Boundary Mapper

Use this internal meta-skill when a model must determine when a skill should be invoked, when it should not be invoked, and what boundary conditions limit safe use.

This skill fixes the failure mode where an analyst treats examples, keywords, or broad domain terms as universal triggers.

## Inputs

- `SKILL.md` frontmatter description.
- Body sections that mention "use when", "do not", warnings, constraints, or task scope.
- Deterministic content blocks with line references.
- Existing structure analysis context when available.

## Process

1. Extract explicit trigger text exactly when source wording says when to use the skill.
2. Identify semantic triggers from task shape, but mark them inferred.
3. Identify negative triggers and non-goals, especially warnings or scope exclusions.
4. Identify boundary conditions such as required inputs, environment assumptions, permissions, or resource availability.
5. Identify misfire risks: cases that look related but should not invoke the skill.
6. Assign confidence separately to explicit, semantic, and negative triggers.
7. Attach evidence or lower confidence when evidence is weak.

## Output Contract

Return activation content suitable for `structure_analysis.json`:

```yaml
activation:
  explicit_triggers: []
  semantic_triggers: []
  negative_triggers: []
  boundary_conditions: []
  misfire_risks: []
  confidence:
  evidence: []
```


## Anchor-Aware Output

In addition to activation content, emit minimal anchor cards when the source supports them. Keep this lightweight; do not decide dispatch policy inside this skill.

Recommended anchor types:

- `trigger_anchor`: explicit or semantic activation conditions.
- `boundary_anchor`: prerequisites, scope limits, and non-goals.
- `handoff_anchor`: conditions where another skill or composed anchor should take over.
- `misfire_anchor`: false-positive patterns that should not invoke the skill.

Minimal anchor card shape:

```yaml
anchors:
  - id: anchor.<skill_id>.trigger.<slug>
    source_skill_id:
    anchor_type: trigger_anchor
    name:
    summary:
    evidence:
      path:
      quote:
    confidence: low | medium | high
    reuse_modes:
      - reference_only
      - temporary_composition
      - agent_rule_patch
    risks:
      - possible trigger overlap with existing user skills
```

Anchor rules:

- Emit `trigger_anchor` only for source-backed activation conditions.
- Emit `boundary_anchor` for non-goals, prerequisites, permission limits, runtime limits, and false scope assumptions.
- Emit `handoff_anchor` only when source wording or structure implies a transition to another skill, tool, or workflow stage.
- Emit `misfire_anchor` for broad keywords that look related but should not activate the skill.
- Do not choose final dispatch policy here; pass trigger and boundary anchors to `asa-anchor-composition-planner`.

## Evidence Rules

- Explicit trigger claims require direct source quotes.
- Semantic triggers must be marked inferred and should not use high confidence.
- Negative triggers may come from warnings, constraints, or license/safety notes.
- Do not use a source quote longer than needed to prove the trigger.

## Failure Modes

- Do not treat every keyword in `SKILL.md` as a trigger.
- Do not confuse outputs with activation conditions.
- Do not omit non-goals just because the source emphasizes capabilities.
- Do not inflate confidence for inferred semantic matches.

## Quality Rubric

A strong trigger map lets a reader answer:

- When should an agent call this skill?
- What user requests are likely matches?
- What requests are false positives?
- What prerequisites must exist before use?



