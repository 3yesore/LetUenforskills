# Benchmark Spec

Benchmarks measure whether Agent Skill Anatomy can produce evidence-grounded, reusable, provider-neutral analysis across different model families. They are not generic chatbot benchmarks; each fixture should exercise a concrete harness role and artifact schema.

## Objectives

- Compare providers and models by role, not only by aggregate score.
- Catch regressions in schema compliance, evidence grounding, and over-inference.
- Measure bilingual output quality where Chinese and English notes are enabled.
- Make cost and latency visible beside quality scores.
- Keep benchmark fixtures small enough for routine CI and rich enough for release qualification.

## Fixture Types

Each fixture is a versioned directory with source files, expected observations, and evaluator metadata.

```text
benchmark/fixtures/<fixture-id>/
  fixture.yaml
  source/
    SKILL.md
    scripts/
    templates/
    assets/
  expected/
    structure.must.json
    workflow.must.json
    patterns.candidates.json
    review.rubric.yaml
```

Recommended fixture classes:

- `minimal_skill`: one `SKILL.md`, no references; verifies basic anatomy extraction.
- `scripted_skill`: includes scripts or commands; verifies workflow and executable asset detection.
- `template_skill`: includes templates/assets; verifies reusable asset cataloging.
- `nested_references`: `SKILL.md` points to relative docs; verifies evidence traversal boundaries.
- `ambiguous_claims`: contains tempting but unsupported conclusions; verifies over-inference control.
- `bilingual_skill`: includes Chinese and English source content; verifies terminology consistency.
- `large_context_skill`: contains long reference docs; verifies truncation, summarization, and context-limit handling.
- `malformed_output_simulation`: uses mock provider cases to verify retry and error artifact behavior.

## Roles Under Test

Benchmarks should evaluate each harness role independently before testing full pipeline quality.

- `inventory_builder`: discovers skill packages, entry files, assets, and source metadata.
- `structure_analyst`: extracts anatomy, dependencies, configuration surfaces, and evidence links.
- `workflow_analyst`: reconstructs ordered operating procedures, decision points, and stop conditions.
- `pattern_miner`: identifies reusable patterns across skills without promoting single-example guesses.
- `renderer`: writes Obsidian-ready notes with frontmatter, backlinks, and bilingual sections when configured.
- `reviewer`: flags unsupported claims, missing evidence, schema drift, and quality risks.
- `translator`: preserves canonical terms, paths, commands, model names, and schema keys while localizing prose.

Full-pipeline benchmark runs should report both role-level scores and final artifact scores.

## Metrics

### Correctness

- `schema_valid_rate`: percentage of calls whose final output validates against the expected schema.
- `required_fact_recall`: required observations found in generated artifacts.
- `forbidden_claim_rate`: unsupported or contradicted claims per artifact.
- `workflow_order_accuracy`: correctness of ordered workflow steps and branching conditions.
- `asset_detection_rate`: scripts, templates, prompts, and examples correctly classified.

### Evidence Quality

- `evidence_coverage`: claims with at least one source path and excerpt.
- `evidence_precision`: cited evidence actually supports the claim.
- `inference_labeling`: inferred claims marked as inferred with confidence.
- `source_boundary_compliance`: no claims from files outside fixture or configured source scope.

### Output Quality

- `frontmatter_validity`: notes contain required keys and valid YAML.
- `link_integrity`: generated wiki links or relative links resolve inside the output vault.
- `bilingual_consistency`: translated terms preserve canonical English identifiers and intended meaning.
- `readability`: reviewer rubric score for concise, useful human notes.
- `reuse_value`: patterns/assets are specific enough to apply in another skill.

### Operations

- `latency_seconds`: wall-clock time by role and full run.
- `input_tokens`, `output_tokens`, `total_tokens`: recorded when provider returns usage.
- `estimated_cost_usd`: calculated from registry cost tier or explicit pricing table.
- `retry_count`: transport retries and schema-validation retries separately.
- `failure_category`: normalized provider or validation failure reason.

## Scoring

Each fixture defines a rubric with role weights. A default release benchmark should weight evidence and correctness higher than prose quality.

```yaml
weights:
  schema_valid_rate: 0.20
  required_fact_recall: 0.20
  evidence_precision: 0.20
  forbidden_claim_rate: 0.15
  workflow_order_accuracy: 0.10
  output_quality: 0.10
  operations: 0.05
```

Scores should be reported as:

- `pass`: meets all required gates and score threshold.
- `warn`: usable but below preferred threshold or missing non-critical metrics.
- `fail`: violates schema, evidence, forbidden-claim, or source-boundary gates.

## Benchmark Matrix

A matrix declares which providers, models, roles, and fixtures to run. Matrix files should support small smoke runs, nightly regression runs, and release comparisons.

Matrix dimensions:

- `providers`: provider configurations or registry model keys.
- `roles`: subset of harness roles.
- `fixtures`: fixture IDs or glob patterns.
- `languages`: `en`, `zh`, or `bilingual` output modes.
- `budgets`: max calls, max tokens, max cost, and per-call timeout.

## Evaluation Modes

- `deterministic`: mock provider or fixed recorded outputs; used in CI.
- `single_model`: one model runs all roles; useful for baseline comparisons.
- `role_routed`: different models per role; reflects production strategy.
- `cross_review`: one model generates and another reviews; useful for evidence-risk analysis.
- `golden_diff`: compare artifacts against checked-in expected JSON/Markdown snapshots.

## Reporting

Each run writes a benchmark report under `runs/<run-id>/benchmark_report.json` and may render Markdown summaries for Obsidian or release notes.

Required report fields:

- benchmark ID, matrix path, fixture versions, git commit, and timestamp.
- provider/model/role assignments and capability registry version.
- per-role metrics, per-fixture metrics, aggregate scores, and pass/warn/fail status.
- links to generated artifacts and reviewer findings.
- cost, latency, retry, and failure summaries.

## Acceptance Gates

A release candidate should not pass unless:

- All generated JSON artifacts validate against schemas.
- No fixture has source-boundary violations.
- Forbidden claims stay under the configured threshold.
- Reviewer catches intentionally unsupported claims in `ambiguous_claims` fixtures.
- Benchmark report includes enough metadata for another run to reproduce provider, model, fixture, and config choices.
