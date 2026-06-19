# LLM Skill Integration Design / 内置分析 Skill 设计

## 1. Purpose

Agent Skill Anatomy should not rely on one large generic prompt for every model call. It should package its own decomposition method as internal skills and inject the relevant method into each agent stage.

This improves output quality because the model receives a concrete operating procedure instead of a vague request to “analyze the skill”.

## 2. Core Idea

The runtime owns a small library of internal meta-skills:

- identity decomposition
- trigger and boundary mapping
- resource role analysis
- workflow tracing
- evidence grounding
- reusable pattern mining
- reader-layer writing
- model comparison judging

These are not target skills. They are method instructions used by analysis agents.

## 3. Invocation Model

Each model call receives four context layers:

1. **Agent role**: structure analyst, workflow analyst, reviewer, pattern miner, etc.
2. **Meta-skill method**: the relevant internal `SKILL.md` content.
3. **Evidence bundle**: deterministic source excerpts and artifact references.
4. **Schema contract**: the JSON output shape that must validate before persistence.

The schema remains the final contract. Meta-skills guide reasoning; they do not replace validation.

## 4. Stage Mapping

| Runtime stage | Internal method skills | Output focus |
| --- | --- | --- |
| `structure_analyst` | identity decomposer, trigger mapper, resource role analyzer | what the skill is, when it activates, what resources mean |
| `workflow_analyst` | workflow trace builder, resource role analyzer | ordered behavior, decision points, failure modes |
| `reviewer` | evidence grounding auditor | unsupported claims, missing evidence, confidence errors |
| `pattern_miner` | reuse pattern miner | reusable assets, templates, design patterns |
| report/vault exporters | reader layer writer | beginner/expert/reuse layers |
| benchmark/comparison | model comparison judge | disagreement, evidence coverage, model strengths |

## 5. Context Packaging

Context should be compact and predictable.

Recommended package:

```text
SYSTEM:
  agent role
  global evidence rules
  relevant internal meta-skill excerpt

USER:
  source package summary
  deterministic evidence bundle
  previous stage artifacts if needed
  output schema reminder
```

Rules:

- Include only the meta-skills required by the current stage.
- Prefer short method sections over entire long documents for small-context models.
- Preserve evidence IDs exactly.
- Never include API keys or local secrets in prompt context.
- Keep internal meta-skills excluded from normal source inventory.

## 6. Provider Compatibility

The integration must work across OpenAI-compatible providers and domestic Chinese model providers.

Provider assumptions:

- Some providers support strict JSON Schema poorly.
- Some models follow Chinese instructions better than English instructions.
- Some models produce verbose narrative before JSON.
- Some small/fast models need shorter evidence bundles.

Runtime response:

- Keep schema validation and retry outside the model.
- Use provider capability metadata to decide prompt strictness and max context.
- Prefer Chinese-first instructions for Chinese model routes.
- Keep stage outputs independent so weak stages can be rerun.

## 7. Quality Advantages

Internal meta-skills should improve:

- completeness of decomposition
- consistency across models
- evidence citation rate
- workflow step specificity
- reusable asset extraction
- bilingual reader quality
- comparability of model outputs

They also make failures easier to diagnose: if a stage is weak, the corresponding method skill can be edited independently from code.

## 8. Guardrails

Internal skills must not become hidden authority.

- Deterministic artifacts remain source of truth.
- Internal skills cannot assert facts about a target repo.
- Every repo-specific claim still needs evidence.
- Internal skills are versioned with the run metadata.
- Reports must show whether meta-skills were enabled.
- Benchmarks should compare with and without meta-skills.

## 9. Custom User Meta-Skills

Custom analysis skills can be supported later, but the default open-source path should be conservative.

Recommended policy:

- Allow custom meta-skill directories only through explicit config.
- Require `internal_meta_skill: true` frontmatter.
- Require declared compatible stages.
- Validate size limits before prompt injection.
- Record custom skill names and hashes in run metadata.

## 10. Artifact Metadata

Each run should eventually record:

```json
{
  "meta_skills": {
    "enabled": true,
    "version": "local-git-sha-or-hash",
    "stage_map": {
      "structure_analyst": ["asa-skill-identity-decomposer"]
    }
  }
}
```

This enables reproducibility and model comparison.

## 11. Acceptance Checklist

The integration is acceptable when:

- Internal meta-skills are excluded from target discovery.
- Each agent receives only relevant method skills.
- Stage outputs remain schema-valid.
- Reports show method-layer outputs in human-readable form.
- Benchmarks can run the same source with meta-skills enabled and disabled.
- Small-context providers can use compressed method excerpts.
