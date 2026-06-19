# LLM Skill Runtime Design / 调用 LLM 的 Skill 化设计

## Purpose

Agent Skill Anatomy should not only analyze external skills; it should also use internal skills to guide its own LLM calls. This makes outputs more consistent, richer, and easier to compare across providers.

The design keeps deterministic artifacts as source of truth. Internal skills improve interpretation quality; they do not replace schemas, evidence rules, or quality gates.

## Design Principle

Use internal meta-skills as bounded method modules:

- Each meta-skill describes one thinking task.
- The runtime injects only the method skills needed by the current agent stage.
- The LLM must output schema-valid JSON, not freeform skill notes.
- The report/vault/data exporters decide presentation.

## Runtime Shape

```text
source repo
  -> deterministic collector
  -> evidence bundle
  -> agent stage resolver
  -> meta-skill context pack
  -> provider call
  -> schema validation
  -> quality review
  -> report/vault/data/graph/cinema exports
```

## Stage-to-Skill Mapping

| Runtime Stage | Internal Skills | Output Focus |
| --- | --- | --- |
| Structure Analyst | `asa-skill-identity-decomposer`, `asa-trigger-boundary-mapper`, `asa-resource-role-analyzer` | identity, activation, resource roles |
| Workflow Analyst | `asa-workflow-trace-builder`, `asa-resource-role-analyzer` | step chain, handoffs, fallback, stop condition |
| Reviewer | `asa-evidence-grounding-auditor` | evidence audit, unsupported claims, confidence review |
| Pattern Miner | `asa-reuse-pattern-miner` | reusable patterns, adaptation notes, anti-patterns |
| Export Writer | `asa-reader-layer-writer` | beginner/expert reader layers, section ordering |
| Comparator | `asa-model-comparison-judge` | cross-model agreement, disagreement, ranking |

## Context Pack Format

A provider prompt receives a compact context pack:

```yaml
method_context:
  version: asa-meta-skills-v1
  stage: workflow_analyst
  loaded_skills:
    - asa-workflow-trace-builder
    - asa-resource-role-analyzer
  rules:
    - cite evidence ids for important claims
    - mark inference level when direct evidence is missing
    - keep output schema-valid
  output_contract: workflow-analysis.schema.json
```

The full `SKILL.md` text should be trimmed to the sections required by the stage:

- purpose
- when to use
- process
- output contract
- evidence rules
- failure modes

Examples can be omitted for smaller context models unless calibration proves they improve output quality.

## Provider-Specific Strategy

Different LLMs need different prompt budgets and strictness levels.

| Provider Family | Recommended Injection | Notes |
| --- | --- | --- |
| Claude | richer method text + examples | strong long-context reasoning, good for reviewer/writer |
| DeepSeek V4 Pro | concise method text + explicit schema rules | good reasoning, needs strict JSON boundaries |
| DeepSeek Flash | compact method bullets only | optimize for cost/latency; expect more fallback review |
| Qwen / DashScope | compact method text + bilingual labels | strong China-compatible route; verify JSON stability |
| Moonshot / Kimi | compact method + evidence bundles | useful for long context experiments |
| OpenAI-compatible generic | safest compact profile | assume unknown capability until calibrated |

Provider differences must be recorded in run metadata so report readers know which model produced each analysis.

## Prompt Budget Policy

The runtime should select one of three method-pack sizes:

### Compact

- skill name
- goal
- 5-8 rules
- output fields

Use for small-context or fast models.

### Standard

- compact content
- process steps
- evidence rules
- common failure modes

Use as default.

### Full

- standard content
- examples
- quality rubric

Use for high-quality calibration runs or expensive reviewer passes.

## Guardrails

- Internal `skills/asa-*` are never analyzed as source skills unless explicitly overridden for benchmark tests.
- The LLM cannot add new files, paths, evidence ids, or schema keys that do not exist.
- Meta-skill guidance never changes deterministic extraction results.
- A stage may fail closed if schema validation fails after retry.
- Unsupported claims stay visible in review artifacts rather than being hidden.
- API keys are never written to config examples, artifacts, docs, or exports.

## Artifact Additions

Recommended optional metadata in each agent artifact:

```json
{
  "method_context": {
    "enabled": true,
    "version": "asa-meta-skills-v1",
    "loaded_skills": ["asa-workflow-trace-builder"],
    "pack_size": "standard"
  },
  "provider_context": {
    "provider": "deepseek",
    "model": "deepseek-reasoner",
    "base_url": "https://api.deepseek.com"
  }
}
```

These fields support later debugging and model comparison.

## Quality Impact Hypothesis

Meta-skill injection should improve:

- trigger/boundary specificity
- workflow step completeness
- resource role clarity
- evidence grounding
- reuse asset quality
- bilingual reader usefulness

It may hurt:

- output length on smaller models
- schema validity if the prompt becomes too complex
- latency and token cost

The benchmark protocol must measure both sides.

## Implementation Checklist

- Keep `src/asa/meta_skills.py` as the resolver.
- Add pack-size selection to config after calibration.
- Record method context in agent outputs.
- Add tests that compact/standard/full packs include expected sections.
- Add model comparison views that show whether meta-skills were enabled.
- Add docs for users who want custom method skills later.
