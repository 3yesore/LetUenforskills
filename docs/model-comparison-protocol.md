# Internal Model Comparison Protocol / 内部模型对比协议

## Purpose

Multi-model comparison is an internal development/testing activity, not a user-facing entry or popularity contest. It measures how different models decompose the same skill under the same evidence constraints, provider routes, schemas, and output surfaces.

The primary question is:

> Which model gives the most evidence-grounded, useful, and reusable skill manual for this source?

## Controlled Run Design

A fair comparison requires the same inputs:

- same source repository and commit or archive hash
- same selected skill package
- same deterministic inventory and evidence index
- same meta-skill version and pack size
- same schema version
- same language target
- same quality gates

Only provider/model configuration changes.

## Recommended Model Matrix

Initial China-compatible matrix:

| Route | Role | Notes |
| --- | --- | --- |
| DeepSeek V4 Pro / reasoner-class | quality baseline | use for full decomposition and reviewer calibration |
| DeepSeek Flash / chat-class | speed/cost baseline | compare how much detail is lost under cheaper route |
| Qwen / DashScope current flagship | domestic alternative | validate JSON and bilingual quality |
| Claude current Sonnet/Opus-class | external reasoning reference | include when key is available |
| OpenAI current reasoning/chat model | external structured-output reference | include when key is available |

Model names change quickly. The UI preset registry should store editable provider/model/base URL entries rather than hard-code one permanent list.

## What To Score

### Structural Accuracy

- identifies correct skill name, target runtime, and scope
- detects `SKILL.md` and all important resources
- separates instruction, script, reference, asset, and example roles
- avoids treating unrelated files as core skill logic

### Workflow Quality

- reconstructs ordered steps with clear verbs
- identifies trigger and stop conditions
- finds tool/script/API handoffs
- describes fallback and ambiguity handling
- avoids inventing steps not supported by evidence

### Evidence Grounding

- cites valid source paths and evidence ids
- uses short relevant quotes when needed
- marks inference level honestly
- does not claim unsupported behavior as fact
- keeps reviewer issues visible

### Reuse Value

- extracts concrete reusable patterns
- provides adaptation recipes
- identifies anti-patterns and traps
- distinguishes project-specific details from transferable design

### Reader Quality

- explains enough for non-experts
- gives enough detail for skill designers
- avoids repetition
- keeps Chinese/English toggle coherent
- uses professional terminology consistently

### Operational Quality

- schema pass rate
- retry count
- latency
- token/cost estimate when available
- failure mode and recoverability

## Scoring Rubric

Use a 0-4 score for each dimension:

| Score | Meaning |
| --- | --- |
| 0 | missing or unusable |
| 1 | present but mostly vague or unsupported |
| 2 | partially useful with noticeable gaps |
| 3 | solid, evidence-aware, readable |
| 4 | excellent, specific, reusable, low-noise |

Recommended weights:

- structural accuracy: 20%
- workflow quality: 20%
- evidence grounding: 25%
- reuse value: 15%
- reader quality: 15%
- operational quality: 5%

Evidence grounding gets the largest weight because the project is research/tool-first.

## Disagreement Types

Comparison reports should classify disagreements:

- `missing`: one model omits an important element another model found
- `conflict`: models claim incompatible behavior
- `specificity_gap`: both are directionally correct, but one is much more precise
- `unsupported_extra`: one model adds attractive but unsupported claims
- `terminology_gap`: same idea with confusing or inconsistent labels
- `language_gap`: Chinese/English quality differs materially
- `reuse_gap`: one model finds transferable assets while another only summarizes

## Output Artifacts

Recommended files under a comparison run:

```text
comparison/
  model_matrix.json
  scorecard.json
  disagreement_cases.jsonl
  best_sections.jsonl
  evidence_failures.jsonl
  reader_quality_notes.md
  comparison_report.md
```

`best_sections.jsonl` should point to sections that can be used as prompt examples or benchmark gold references.

## UI Representation

The user-facing report should stay focused on the single-run manual; comparison remains in development/testing artifacts.

Recommended UI blocks:

- model route chips with provider/model/base URL
- scorecard radar or compact bars
- disagreement list grouped by severity
- best excerpt per model, with evidence references
- quality warnings when a model has invalid schema retries or unsupported claims
- “use this model for next run” action in local UI only

Do not add comparison UI to the main report; keep it in development/testing notes until explicitly promoted.

## Test Procedure

1. Run deterministic collection once.
2. Run each model route against the same selected skill.
3. Validate artifacts with schemas.
4. Run deterministic quality checks.
5. Export report/vault/data/graph for each route.
6. Run comparison script on completed runs.
7. Human-review the top disagreement cases.
8. Promote recurring failures into rules, schemas, or meta-skill edits.

## Acceptance Gates

A comparison is publishable when:

- all models used the same source/evidence bundle
- model IDs and provider routes are visible
- no API keys or secrets appear in artifacts
- each score has at least one rationale
- severe unsupported claims are highlighted
- the report distinguishes “best explanation” from “most correct fact”
