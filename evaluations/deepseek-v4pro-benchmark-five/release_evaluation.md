# LetUen Skill Package Release Evaluation — DeepSeek v4pro Five-Skill Benchmark

## 1. Evaluation Scope

This evaluation is for the LetUen skill package and its decomposition pipeline before publishing the skill bundle.

Benchmark run:

- Run ID: `20260618T143729Z`
- Model: `deepseek-v4-pro`
- Source: fixed local benchmark set from `anthropics/skills`
- Config: `evaluations/anatomy.deepseek.pro.anthropic-benchmark-five.yaml`
- Output bundle: `evaluations/deepseek-v4pro-benchmark-five/letuen`

Tested skills:

1. `algorithmic-art`
2. `frontend-design`
3. `skill-creator`
4. `mcp-builder`
5. `pdf`

## 2. What Was Added Before Final Evaluation

A source-aware evidence repair layer was implemented and tested:

- Module: `src/asa/evidence_repair.py`
- CLI: `python -m asa repair-evidence --run <run-dir>`
- Repair report: `evaluations/runs/20260618T143729Z/evidence_repair_report.json`

The repair layer:

1. Reads the aggregate run inventory.
2. Resolves each skill package back to its real source root.
3. Searches source files for exact or fuzzy-matched evidence lines.
4. Replaces model paraphrases with exact source snippets when possible.
5. Downgrades unrecoverable evidence to inferred rather than pretending it is explicit.
6. Repairs missing structure script manifests from package inventory when available.
7. Writes sidecar repair reports for auditability.

Final evidence repair result:

- Artifacts inspected: 10
- Final repair changes: 3 in the last repair pass
- Earlier repair pass removed all evidence quote failures from the benchmark

## 3. Final Quality Gate

Final quality report:

- File: `evaluations/deepseek-v4pro-benchmark-five-quality.repaired.json`
- Checked skills: 5
- Issues: 0
- Severity counts: `{}`
- Publishable by deterministic rules: `true`

Per-skill deterministic issue count:

| Skill | Issues |
|---|---:|
| `algorithmic-art` | 0 |
| `frontend-design` | 0 |
| `skill-creator` | 0 |
| `mcp-builder` | 0 |
| `pdf` | 0 |

This is a major improvement over the pre-repair result:

- Before repair: 16 major issues
- After markup-insensitive matching: 11 major issues
- After source-aware repair: 0 issues

## 4. Output Completeness

Final exported bundle:

- Main entry: `evaluations/deepseek-v4pro-benchmark-five/letuen/index.html`
- Report: `evaluations/deepseek-v4pro-benchmark-five/letuen/report/index.html`
- Repo: `evaluations/deepseek-v4pro-benchmark-five/letuen/repo/index.html`
- Cinema: `evaluations/deepseek-v4pro-benchmark-five/letuen/cinema/index.html`
- Graph: `evaluations/deepseek-v4pro-benchmark-five/letuen/graph/index.html`
- Vault: `evaluations/deepseek-v4pro-benchmark-five/letuen/vault`
- Anchors: `evaluations/deepseek-v4pro-benchmark-five/letuen/anchors/anchors.json`
- Composition plan: `evaluations/deepseek-v4pro-benchmark-five/letuen/anchors/composition_plan.json`

Quantitative output:

- Skill pages: 5
- Vault notes: 101
- Anchors: 61
- Resource role rows: 45
- Workflow trace rows: 52
- Evidence audit rows: 60
- Reuse assets: 3

Anchor distribution:

| Anchor type | Count |
|---|---:|
| `identity_anchor` | 5 |
| `trigger_anchor` | 5 |
| `workflow_anchor` | 5 |
| `evidence_anchor` | 5 |
| `validation_anchor` | 17 |
| `risk_anchor` | 21 |
| `reuse_anchor` | 3 |

Composition plan:

- Form: `temporary_composition`
- Dispatch strategy: `prefer_existing_skill`
- Selected anchors: 51
- Rejected anchors: 10

## 5. Reviewer-Level Result

Deterministic quality gates now pass, but model reviewer outputs still distinguish between fully publishable and needs-revision analyses.

| Skill | Reviewer status | Reviewer approved | Evidence | Structure | Workflow |
|---|---|---:|---:|---:|---:|
| `algorithmic-art` | publishable | yes | 4 | 5 | 5 |
| `frontend-design` | needs_revision | no | 4 | 5 | 5 |
| `skill-creator` | publishable | yes | 5 | 5 | 5 |
| `mcp-builder` | needs_revision | no | 4 | 5 | 5 |
| `pdf` | needs_revision | no | 4 | 5 | 3 |

Interpretation:

- The deterministic gate confirms the artifacts are structurally valid and evidence-consistent.
- The reviewer still flags deeper content-quality concerns for 3 of 5 skills.
- This is expected and healthy: the gate checks hard correctness, while reviewer checks publishability and interpretive quality.

## 6. Capability Evaluation

### 6.1 Strengths

LetUen now demonstrates strong capability in the following areas:

1. **End-to-end real LLM decomposition**
   - The system completed a five-skill DeepSeek v4pro run without mock fallback.

2. **Multi-agent artifact separation**
   - Structure analysis, workflow analysis, reviewer reports, pattern mining, anchors, and exports are separately materialized.

3. **Evidence discipline**
   - The new repair layer prevents paraphrased evidence from silently passing as direct quotes.
   - It also repairs real source-backed quotes into exact snippets where possible.

4. **Reusable anchor output**
   - The benchmark produced identity, trigger, workflow, validation, risk, evidence, and reuse anchors.

5. **Multiple user-facing surfaces**
   - Report, repo, cinema, graph, data, and Obsidian outputs are all generated from the same run.

6. **Harness compatibility**
   - The pipeline now normalizes model drift, repairs evidence, and preserves non-destructive sidecar composition by default.

### 6.2 Weaknesses

Current weaknesses before public release:

1. **Reviewer status is not uniformly publishable**
   - 3 of 5 tested skills remain `needs_revision` by model reviewer, despite deterministic quality passing.

2. **Evidence repair is post-hoc**
   - The system repairs after generation. This is safe and auditable, but ideal future behavior is to reduce repair needs at prompt/schema level.

3. **Fuzzy repair requires conservative thresholds**
   - Too low a threshold can over-repair; too high a threshold leaves false failures. Current behavior is acceptable but should remain audited.

4. **Graph/report quality still depends on UI refinement**
   - Functional outputs exist, but public-facing polish should be reviewed separately before marketing release.

5. **Model-specific behavior still needs comparison**
   - This evaluation covers DeepSeek v4pro. Claude/GPT/Qwen behavior should be compared before claiming model-agnostic quality.

## 7. Release Readiness Verdict

### Strict Verdict

LetUen is ready for a **developer-preview skill package release**, not yet a polished public benchmark release.

### Why Developer Preview Is Reasonable

- The package runs against real skills.
- The pipeline is end-to-end functional.
- Deterministic quality gates pass after evidence repair.
- Outputs are useful for learning, reuse, and workflow recomposition.
- Repair steps are auditable rather than hidden.

### Why Not Full Public Benchmark Yet

- Reviewer-level publishability is mixed.
- Evidence repair is newly introduced and should be tested on more repositories.
- UI/report polish and graph readability still need human acceptance.
- Multi-model comparison has not yet been completed.

## 8. Recommended Release Label

Recommended release label:

`LetUen v0.2.0-dev / Evidence-Grounded Skill Anatomy Preview`

Recommended release wording:

> LetUen decomposes Agent Skills into structured reports, reusable anchors, Obsidian vaults, and visual repo/cinema surfaces. This developer-preview release includes deterministic quality checks and source-aware evidence repair. It is suitable for evaluating and learning from skill packages, while full public benchmark claims remain pending broader multi-model testing.

## 9. Must-Have Before Publishing The Skill Package

Before publishing, do these final checks:

1. Run full tests:
   - `python -m unittest discover -s tests`
   - `python -m compileall src scripts -q`
   - `node --check site/script.js`

2. Export the LetUen skill package.

3. Confirm the exported skill package includes:
   - main `SKILL.md`,
   - 8 internal method skills,
   - anchor-aware composition planner,
   - evidence repair documentation,
   - non-destructive harness contract,
   - usage examples.

4. Add release notes explaining:
   - evidence repair behavior,
   - deterministic quality gate,
   - known reviewer-level limitations,
   - developer-preview status.

## 10. Next Evaluation After Release

After publishing the developer preview, run a broader benchmark:

- DeepSeek v4pro
- DeepSeek flash
- GPT route
- Claude route
- Qwen route

Metrics:

- deterministic issue count,
- reviewer publishability,
- repair change count,
- anchor usefulness,
- Obsidian learning value,
- report readability,
- runtime/cost.
