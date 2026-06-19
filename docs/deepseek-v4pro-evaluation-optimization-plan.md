# DeepSeek v4pro Evaluation Follow-up Optimization Plan

## 1. Background

This plan is based on the real DeepSeek v4pro run:

- Run: `runs/20260618T133033Z`
- Output bundle: `evaluations/anthropic-five-dsv4pro/letuen`
- Quality report: `evaluations/anthropic-five-dsv4pro/quality_issues.json`
- Source: `https://github.com/anthropics/skills`
- Model: `deepseek-v4-pro`

The run completed end-to-end and produced a rich result set:

- 5 skill pages
- 104 Obsidian notes
- 68 anchors
- 59 resource-role rows
- 41 workflow-trace rows
- 69 evidence-audit rows
- 5 reuse assets

However, deterministic quality gates reported:

- 19 issues total
- 5 major issues
- 14 minor issues
- `publishable_by_rules=false`

This means LetUen is already capable of real Skill decomposition, but the model-output contract, quality normalization, and report-facing explanation need another engineering pass before public benchmark use.

## 2. Goal

Upgrade the LetUen pipeline so the same five-skill DeepSeek v4pro benchmark can become:

1. **Quality-passable**: deterministic quality issues should drop to zero major issues and ideally fewer than three minor issues.
2. **Evidence-disciplined**: unsupported claims should be lowered in confidence, marked as inferred, or removed.
3. **Harness-compatible**: model outputs should conform to strict reusable schemas without relying on perfect model obedience.
4. **Reader-friendly**: report/repo output should explain what was decomposed, what is reusable, and what still needs revision.
5. **Repeatable**: benchmark inputs should be fixed so DeepSeek, GPT, Claude, and domestic models can be compared fairly.

## 3. Findings From This Run

### 3.1 Model Strengths

DeepSeek v4pro performed well on high-level decomposition:

- Extracted explicit triggers and inferred trigger families.
- Reconstructed multi-step workflow chains.
- Identified resource roles and selective context-loading strategies.
- Produced validation anchors and risk anchors at useful volume.
- Reviewer correctly rejected under-evidenced publishability in several cases.

The strongest example was `claude-api`, where the model reconstructed:

- provider guard logic,
- language detection,
- subcommand branching,
- surface selection,
- implementation rules,
- verification pitfalls.

### 3.2 Quality Weaknesses

The quality report grouped failures into four issue families.

| Code | Count | Severity | Meaning |
|---|---:|---|---|
| `TARGET_AGENTS_WITHOUT_EVIDENCE` | 5 | major | model inferred target agents with high overall confidence but no direct evidence |
| `TOOL_ITEM_NOT_OBJECT` | 10 | minor | tools were emitted as strings rather than strict objects |
| `EVIDENCE_QUOTE_TOO_LONG` | 3 | minor | quotes exceeded the configured 25-word rule |
| `INFERRED_EVIDENCE_NEEDS_NOTES` | 1 | minor | inferred evidence lacked explanatory notes |

### 3.3 Root Cause Analysis

The failures are not primarily due to DeepSeek v4pro being unable to analyze skills. They come from three system gaps:

1. **Prompt/schema mismatch**
   - `structure-analysis.schema.json` allows loose arrays for `tools`, `inputs`, `outputs`, and `target_agents`.
   - The quality gate expects stricter structures than the schema requires.

2. **No post-generation normalizer**
   - The model can produce semantically useful but structurally loose output.
   - Current pipeline validates schema but does not normalize common model variants before writing artifacts.

3. **Evidence policy is not enforced after generation**
   - The prompt asks for short quotes and confidence discipline.
   - The system does not automatically trim quotes, downgrade unsupported fields, or attach inference notes.

## 4. Optimization Strategy

Use a three-layer defense:

1. **Contract first**: tighten schemas and prompts so models know the exact desired shape.
2. **Normalize second**: add deterministic post-processing for common model-output drift.
3. **Gate third**: keep strict quality checks, but make them actionable and report-visible.

This avoids overfitting to DeepSeek while improving GPT, Claude, Qwen, Moonshot, and other OpenAI-compatible routes.

## 5. Phase 1 — Structured Output Normalization

### 5.1 Add Artifact Normalizer

Create a new module:

- `src/asa/artifact_normalizer.py`

Responsibilities:

- Normalize `structure_analysis.json` after model generation and before writing final artifact.
- Normalize `workflow_analysis.json` evidence fields.
- Return both normalized output and a small normalization report.

Suggested API:

```python
def normalize_structure_analysis(data: dict[str, Any], *, max_quote_words: int = 25) -> tuple[dict[str, Any], list[dict[str, Any]]]: ...

def normalize_workflow_analysis(data: dict[str, Any], *, max_quote_words: int = 25) -> tuple[dict[str, Any], list[dict[str, Any]]]: ...
```

Write sidecar reports:

- `structure_analysis.normalization.json`
- `workflow_analysis.normalization.json`

### 5.2 Normalize `tools`

Current failure:

- `tools` often contains strings like `web_fetch`, `grep`, `Anthropic SDK`.

Target shape:

```json
{
  "name": "web_fetch",
  "type": "external_tool",
  "required": false,
  "purpose": "Fetch live documentation when cached references may be stale.",
  "evidence": []
}
```

Rules:

- string item -> object
- unknown type -> `unknown`
- required defaults to `false`
- evidence defaults to `[]`
- if tool appears in `file_anatomy.scripts`, infer `type=cli` or `filesystem` only when safe

Implementation files:

- `src/asa/artifact_normalizer.py`
- `src/asa/agent_call.py`
- `schemas/structure-analysis.schema.json`
- `tests/test_artifact_normalizer.py`

### 5.3 Normalize Evidence Quotes

Rules:

- Enforce `max_quote_words` after generation.
- Preserve the original quote in sidecar normalization report, not in public artifact.
- If trimming would make quote matching fail, prefer a shorter exact substring found in source.
- If exact quote cannot be found, mark evidence as `inferred` or lower confidence, depending on context.

Implementation files:

- `src/asa/artifact_normalizer.py`
- `src/asa/quality/rules.py`
- `tests/test_artifact_normalizer.py`

### 5.4 Normalize Inferred Evidence Notes

Rules:

- If `evidence_type="inferred"` and `notes` is empty, add a conservative note:
  - `Inferred by model from surrounding structure; not directly stated by source.`
- If an inferred workflow step is high confidence, downgrade to `medium`.

Implementation files:

- `src/asa/artifact_normalizer.py`
- `tests/test_artifact_normalizer.py`

## 6. Phase 2 — Target Agent Evidence Discipline

### 6.1 Split Direct and Inferred Target Agents

Current schema:

```json
"target_agents": ["AI Coding Agent"]
```

Proposed enriched shape:

```json
"target_agents": [
  {
    "name": "AI Coding Agent",
    "confidence": "medium",
    "inferred": true,
    "evidence": [],
    "notes": "Inferred from task framing; source does not explicitly name the agent audience."
  }
]
```

Compatibility path:

- During Phase 1, normalizer accepts both strings and objects.
- During Phase 2, schema is tightened to require objects.
- Report/vault exporters should render both shapes until migration completes.

### 6.2 Downgrade Unsupported Target Agents

Normalizer rule:

- If `target_agents` exists and no direct evidence is found:
  - set each item `inferred=true`
  - set item confidence to `medium` or `low`
  - downgrade `confidence.overall` from `high` to `medium` only if target-agent support is the only high-confidence basis

Quality rule adjustment:

- Keep `TARGET_AGENTS_WITHOUT_EVIDENCE` as major only when:
  - target agent is high confidence, and
  - not marked inferred, and
  - no evidence exists.

Implementation files:

- `schemas/structure-analysis.schema.json`
- `src/asa/artifact_normalizer.py`
- `src/asa/quality/rules.py`
- `src/asa/report_exporter.py`
- `src/asa/vault_exporter.py`
- `tests/test_quality_rules.py`

## 7. Phase 3 — Prompt and Schema Alignment

### 7.1 Prompt Changes

Update:

- `prompts/structure-analyst.md`
- `prompts/workflow-analyst.md`
- `prompts/reviewer.md`

Add explicit instructions:

- Do not use plain strings for `tools`; every tool must be an object.
- Target agents require direct quote evidence; otherwise mark inferred with medium/low confidence.
- Evidence quotes must be exact, short substrings from source files.
- If source does not support a claim, keep it out of main fields and place it in risk/notes as inference.
- Prefer fewer, better-supported claims over exhaustive unsupported claims.

### 7.2 Schema Tightening

Update `schemas/structure-analysis.schema.json`:

- Define `tool` object in `$defs`.
- Define `target_agent` object in `$defs`.
- Keep compatibility for one release if needed:
  - `items: oneOf [string, target_agent]`
- Later remove string support.

Update `schemas/workflow-analysis.schema.json`:

- Require evidence objects to carry notes when `evidence_type=inferred`.
- Consider adding `maxWords` cannot be expressed in current simple validator, so enforce through normalizer/quality rule.

Implementation files:

- `schemas/structure-analysis.schema.json`
- `schemas/workflow-analysis.schema.json`
- `prompts/structure-analyst.md`
- `prompts/workflow-analyst.md`
- `prompts/reviewer.md`
- `tests/test_schema_validation.py`

## 8. Phase 4 — Composition Plan Normalization

### 8.1 Current Problem

The composition plan exists, but summary extraction showed empty `form` and `dispatch_strategy` fields in one path.

Likely cause:

- The planner writes fields under a different nested key than the report/evaluation summary expects.
- Some exports read `plan.composition.form`; others read top-level or older naming.

### 8.2 Target Contract

Normalize `composition_plan.json` to always expose:

```json
{
  "schema_version": 1,
  "request": {},
  "composition": {
    "form": "temporary_composition|forkable_workflow|reference_pack|unknown",
    "dispatch_strategy": "prefer_existing_skill|compose_anchors|manual_review",
    "summary": { "zh": "...", "en": "..." }
  },
  "selected_anchors": [],
  "rejected_anchors": [],
  "warnings": []
}
```

### 8.3 UI Display

Report/repo should show:

- selected anchor count,
- rejected anchor count,
- composition form,
- dispatch strategy,
- top reusable anchors grouped by type.

Implementation files:

- `src/asa/composition_planner.py`
- `src/asa/report_exporter.py`
- `src/asa/vault_exporter.py`
- `tests/test_composition_planner.py`
- `tests/test_export_report.py`

## 9. Phase 5 — Benchmark Repeatability

### 9.1 Fixed Five-Skill Benchmark Source

The mock run and dsv4pro run did not use the same five skills.

Create:

- `evaluations/sources.anthropic-benchmark-five.yaml`
- `evaluations/anatomy.deepseek.pro.anthropic-benchmark-five.yaml`

Lock the five selected skills by local path or include pattern:

1. `algorithmic-art`
2. `frontend-design`
3. `skill-creator`
4. `mcp-builder`
5. `pdf`

Alternative benchmark set from the actual dsv4pro first-five run:

1. `algorithmic-art`
2. `brand-guidelines`
3. `canvas-design`
4. `claude-api`
5. `doc-coauthoring`

Recommendation:

- Use the first set as **Skill Mechanics Benchmark**.
- Use the second set as **Official Anthropic Inventory Benchmark**.

### 9.2 Benchmark Matrix

Add a comparison matrix later:

- `deepseek-v4-pro`
- `deepseek-v4-flash`
- `gpt-5.2` or current OpenAI route
- Claude route
- Qwen route

Metrics:

- quality major issue count,
- minor issue count,
- anchor count,
- workflow step count,
- evidence audit count,
- reviewer publishability,
- latency,
- cost estimate if available,
- human readability score.

Implementation files:

- `benchmark/matrix.example.yaml`
- `docs/model-comparison-spec.md`
- future `src/asa/benchmark_runner.py`

## 10. Phase 6 — Report and Repo Presentation Improvements

### 10.1 Report Should Surface Quality Honestly

For each skill page, show:

- `Publishable` / `Needs revision` status.
- Top three reasons.
- Evidence confidence distribution.
- Unsupported claims count.
- Reusable anchor count.

### 10.2 Repo Should Explain the Skill as a Manual

For user-facing repo view, each skill should answer:

1. What is this skill?
2. When does it trigger?
3. What files/resources does it load?
4. What is the agent workflow?
5. What reusable anchors can I borrow?
6. What risks or failure modes should I respect?
7. What needs human revision before reuse?

Implementation files:

- `src/asa/report_exporter.py`
- `src/asa/vault_exporter.py`
- `src/asa/data_exporter.py`
- `site/styles.css`
- `site/script.js`
- `tests/test_export_report.py`

## 11. Implementation Order

### Sprint A — Quality Pass Foundation

1. Add `artifact_normalizer.py`.
2. Normalize `tools` strings to objects.
3. Normalize inferred evidence notes.
4. Trim evidence quotes deterministically.
5. Wire normalizer into `generate_validated_json` or the specific agent wrappers.
6. Add unit tests for all normalizer behaviors.
7. Re-run dsv4pro benchmark with the same config.

Expected outcome:

- `TOOL_ITEM_NOT_OBJECT`: 0
- `EVIDENCE_QUOTE_TOO_LONG`: 0 or near 0
- `INFERRED_EVIDENCE_NEEDS_NOTES`: 0

### Sprint B — Target Agent Contract

1. Add structured target-agent support.
2. Update prompt instructions.
3. Update exporters to render structured target-agent fields.
4. Update quality rule so unsupported high-confidence claims remain major.
5. Re-run benchmark.

Expected outcome:

- `TARGET_AGENTS_WITHOUT_EVIDENCE`: 0 major issues if model/normalizer marks inferred correctly.

### Sprint C — Composition and UI Summary

1. Normalize composition plan fields.
2. Improve report/repo quality summary cards.
3. Add anchor grouping in report and vault.
4. Re-export previous run to verify visual improvements without re-calling LLM.

Expected outcome:

- Report/repo explains not just what was generated, but what is safe to reuse.

### Sprint D — Repeatable Benchmark

1. Add fixed five-skill benchmark configs.
2. Add benchmark README.
3. Run dsv4pro again.
4. Save outputs under `evaluations/deepseek-v4pro-benchmark-five/`.

Expected outcome:

- Future model comparisons are fair and repeatable.

## 12. Test Plan

Run focused tests after each sprint:

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_quality_rules tests.test_export_report tests.test_anchor_exporter
python -m compileall src scripts -q
```

After normalizer implementation:

```powershell
$env:PYTHONPATH='src'
python -m unittest tests.test_artifact_normalizer
```

Full validation:

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
node --check site/script.js
python -m compileall src scripts -q
```

Benchmark rerun:

```powershell
$env:PYTHONPATH='src'
python -m asa run --config evaluations\anatomy.deepseek.pro.anthropic-benchmark-five.yaml --limit-skills 5
python -m asa quality-run --run runs\<run-id> --output evaluations\deepseek-v4pro-benchmark-five\quality_issues.json
python -m asa export-letuen --run runs\<run-id> --output evaluations\deepseek-v4pro-benchmark-five\letuen --composition-request evaluations\deepseek-v4pro-benchmark-five\composition_request.yaml
```

Acceptance target:

- full tests pass,
- run completes,
- quality major issues = 0,
- minor issues <= 3,
- report/repo/vault/data/anchors generated,
- report clearly marks non-publishable claims instead of hiding them.

## 13. Risks

- Tightening schema too quickly may reduce provider compatibility.
- Automatic quote trimming may break exact source matching if not source-aware.
- Downgrading confidence automatically can hide model weakness if not recorded in normalization reports.
- More normalization can make outputs cleaner but less transparent unless sidecar reports are preserved.

Mitigation:

- Use sidecar normalization reports.
- Keep raw model output optionally under `*.raw.json` in debug mode.
- Add tests around every transformation.
- Keep quality gate strict and visible in the report.

## 14. Recommended Next Action

Start with Sprint A. It has the highest leverage and directly addresses 14 of the 19 observed issues without changing the visual UI or rerouting the product direction.

After Sprint A, re-export the existing run first to confirm deterministic cleanup. Then rerun dsv4pro only if needed.
