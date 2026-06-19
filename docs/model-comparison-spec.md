# Internal Model Comparison Spec / 内部模型对比规范

## 1. Purpose

Multi-model comparison is an internal development and calibration feature, not a user-facing product entry or marketing leaderboard. It measures how different models decompose the same skill under the same evidence constraints.

The goal is to learn which model is better at which stage and how model choice changes the final report, graph, and reusable assets.

## 2. Controlled Comparison Principle

A valid comparison changes one major variable at a time.

Fixed variables:

- source repo and commit
- selected skill package
- deterministic artifacts
- meta-skill version
- schema version
- language policy
- quality rules

Variable:

- provider/model route

Optional experimental variables:

- with/without meta-skills
- full evidence bundle vs compressed evidence bundle
- Chinese-first vs English-first prompts

## 3. Required Runs

For a meaningful first comparison:

1. DeepSeek reasoning/pro route
2. DeepSeek fast/flash route
3. Claude current strong route
4. Qwen or another China-compatible route

Model names change over time, so configs should store model ids as editable presets rather than hard-coded UI claims. The UI can show recommended presets, but the config file remains the source of truth.

## 4. Metrics

### 4.1 Structural Metrics

- schema pass rate
- retry count
- missing required fields
- artifact completeness
- stage latency
- token/cost estimate when available

### 4.2 Evidence Metrics

- evidence citation count
- invalid evidence id count
- missing source path count
- unsupported claim count
- high-confidence inferred claim count
- quote verification failures

### 4.3 Decomposition Metrics

- identity specificity
- activation boundary clarity
- resource role coverage
- workflow step count and quality
- failure mode coverage
- tool/script risk coverage

### 4.4 Reader Metrics

- beginner readability
- expert usefulness
- reuse actionability
- bilingual quality
- repetition rate
- report section completeness

### 4.5 Reuse Metrics

- reusable asset count
- template quality
- adaptation constraints
- risk warnings
- cross-skill pattern usefulness

## 5. Scorecard Shape

Recommended comparison artifact:

```json
{
  "source": "anthropics/skills",
  "skill": "algorithmic-art",
  "comparison_id": "2026-06-xx-model-comparison",
  "runs": [
    {
      "run_id": "...",
      "provider": "deepseek",
      "model": "...",
      "schema_pass_rate": 1.0,
      "unsupported_claims": 0,
      "workflow_steps": 9,
      "reuse_assets": 3,
      "notes": []
    }
  ],
  "agreement_zones": [],
  "disagreement_zones": [],
  "recommended_use": {}
}
```

## 6. Disagreement Taxonomy

Disagreements should be classified, not only counted.

- **identity disagreement**: models disagree on skill purpose or target user
- **trigger disagreement**: models disagree on when the skill should run
- **workflow disagreement**: step order, missing step, or invented step
- **resource disagreement**: different interpretation of script/reference/asset roles
- **risk disagreement**: tool or security risk seen by one model but not another
- **reuse disagreement**: different reusable patterns extracted
- **evidence disagreement**: same claim supported by different or weak evidence
- **language disagreement**: Chinese/English explanation changes meaning

## 7. Human Review Loop

The comparison should produce review prompts for humans:

- Which model produced the most useful workflow trace?
- Which model over-inferred beyond evidence?
- Which model found reusable assets others missed?
- Which claims need deterministic rule support?
- Which prompt/meta-skill should be revised?

Human calibration notes should become benchmark fixtures or prompt/schema changes.

## 8. UI Presentation

Development comparison artifacts should avoid overwhelming reviewers.

Recommended surfaces:

- compact model score strip at report top
- evidence coverage comparison table
- disagreement cards with source links
- graph layer showing model-specific nodes/edges
- exportable benchmark JSON/CSV

Do not hide raw model outputs; link them in appendix/artifacts.

## 9. Operational Rules

- Never persist user-provided API keys in generated reports or fixtures.
- Run `asa plan-run` before expensive comparisons.
- Use `--limit-skills 1` for first calibration.
- Store configs without secrets.
- Keep provider-specific failures visible rather than normalizing them away.

## 10. Acceptance Checklist

A model comparison is acceptable when:

- all compared runs use the same deterministic source artifacts
- all outputs pass schemas or record explicit failure artifacts
- deterministic quality metrics are computed for every run
- disagreement cases are classified
- report readers can see which model produced which claim
- no secret appears in artifacts, logs, report, vault, or data exports
