---
name: asa-model-comparison-judge
description: Use when comparing multiple model outputs for the same skill decomposition task across quality, omissions, and fit.
internal_meta_skill: true
asa_role: benchmark
output_contract: benchmark.model_comparison + letuen.comparison_anchors
---

# ASA Model Comparison Judge

Use this internal meta-skill when multiple LLM runs analyze the same skill and the project must compare quality, omissions, disagreements, and role suitability.

This skill fixes the failure mode where model comparison only counts output length, treats different wording as meaningful disagreement, or fails to show which model is best for each anchor type during development testing.

## Inputs

- Two or more run directories for the same source skill.
- Run metadata: provider, model, source commit, config, language, and timestamps.
- Structure, workflow, reviewer, pattern, vault, and report artifacts.
- Deterministic quality metrics and reviewer issues.

## Process

1. Confirm compared runs use the same source repository, skill path, and preferably the same commit.
2. Compare completeness across identity, trigger, resource, workflow, evidence, reuse, and bilingual layers.
3. Compare evidence grounding before comparing prose quality.
4. Identify real disagreements: different claims about behavior, role, boundaries, or workflow order.
5. Identify omissions: useful fields present in one run but missing in another.
6. Rate each model by role: structure, workflow, review, reuse, bilingual writing, and Obsidian usefulness.
7. Compare anchors by type so consensus, disagreement, and best-model-per-anchor-type are visible.
8. Explain whether a difference is quality, style, unsupported speculation, or harmless surface variation.
9. Produce benchmark-ready tables and a cautious recommendation for development testing only.

## Output Contract

Return model comparison content suitable for benchmark reports:

```yaml
model_comparison:
  compared_runs: []
  per_model_scores: []
  disagreements: []
  omissions: []
  best_for_role:
  recommendation:
  anchors:
    anchor_consensus:
      - id:
        anchor_type:
        agreed_claim:
        agreeing_models: []
        evidence_basis: direct | structural | inferred | mixed | unknown
        confidence: high | medium | low | unknown
        usable_as_baseline: true | false
        notes:
    anchor_disagreement:
      - id:
        anchor_type:
        disagreement:
        models_involved: []
        competing_claims: []
        likely_cause: missing_evidence | inference_gap | source_ambiguity | model_hallucination | style_difference | unknown
        resolution_action: inspect_source | prefer_evidence_grounded | rerun_model | mark_inconclusive | ignore_style_difference
        severity: high | medium | low
        evidence: []
    best_model_per_anchor_type:
      - anchor_type:
        best_model:
        best_provider:
        reason:
        strengths: []
        weaknesses: []
        use_for_roles: []
        avoid_for_roles: []
        confidence: high | medium | low | unknown
```


## Anchor Output Rules

Emit comparison anchors only for development and benchmark analysis. Do not turn this into a user-facing model selection workflow unless the harness explicitly requests it.

- `anchor_consensus`: a stable finding that multiple models independently agree on for the same anchor type.
- `anchor_disagreement`: a meaningful conflict about behavior, boundary, evidence, workflow order, or reuse safety.
- `best_model_per_anchor_type`: a role-specific recommendation for which model performs best on identity, trigger, resource, workflow, evidence, reuse, reader, or composition anchors.

Prefer evidence-grounded agreement over polished prose. Treat unsupported extra detail as risk. If models differ only in wording or style, mark it as `style_difference` and do not inflate it into a disagreement.

## Evidence Rules

- Do not compare runs from different source commits as if they are equivalent.
- Use reviewer findings and evidence scores before subjective readability.
- Treat longer output as better only when it adds supported, non-repetitive information.
- Mark unsupported extra detail as risk, not advantage.

## Failure Modes

- Do not confuse wording differences with factual disagreement.
- Do not reward hallucinated detail.
- Do not ignore missing evidence because the report reads well.
- Do not produce a single winner when models are better at different roles.

## Quality Rubric

A strong model comparison answers:

- Which model understood the skill more completely?
- Which model stayed most evidence-grounded?
- Which model produced better reusable learning assets?
- Which model should be used for each Agent role?

