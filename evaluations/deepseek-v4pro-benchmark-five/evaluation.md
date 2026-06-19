# DeepSeek v4pro Benchmark Five — Detailed Test Result

## Run Metadata
- Run ID: `20260618T143729Z`
- Model: `deepseek-v4-pro`
- Config: `evaluations/anatomy.deepseek.pro.anthropic-benchmark-five.yaml`
- Source mode: fixed local benchmark sources
- Source repository: `https://github.com/anthropics/skills`

## Tested Skills
1. `algorithmic-art`
2. `frontend-design`
3. `skill-creator`
4. `mcp-builder`
5. `pdf`

## Output Bundle
- Main entry: `evaluations/deepseek-v4pro-benchmark-five/letuen/index.html`
- Report: `evaluations/deepseek-v4pro-benchmark-five/letuen/report/index.html`
- Repo: `evaluations/deepseek-v4pro-benchmark-five/letuen/repo/index.html`
- Cinema: `evaluations/deepseek-v4pro-benchmark-five/letuen/cinema/index.html`
- Graph: `evaluations/deepseek-v4pro-benchmark-five/letuen/graph/index.html`
- Vault: `evaluations/deepseek-v4pro-benchmark-five/letuen/vault`
- Anchors: `evaluations/deepseek-v4pro-benchmark-five/letuen/anchors/anchors.json`
- Composition: `evaluations/deepseek-v4pro-benchmark-five/letuen/anchors/composition_plan.json`
- Quality report: `evaluations/deepseek-v4pro-benchmark-five-quality.final.json`

## Quantitative Result
- Skill pages: 5
- Vault notes: 101
- Anchors: 61
- Data rows:
  - skills: 5
  - resource roles: 45
  - workflow trace: 52
  - evidence audit: 60
  - reuse assets: 3
- Composition plan:
  - selected anchors: 51
  - rejected anchors: 10
  - form: `temporary_composition`
  - dispatch strategy: `prefer_existing_skill`

## Review Result By Skill
| Skill | Skill type | Reviewer status | Reviewer publishable |
|---|---|---|---:|
| `algorithmic-art` | workflow | publishable | yes |
| `frontend-design` | meta | needs_revision | no |
| `skill-creator` | meta | publishable | yes |
| `mcp-builder` | workflow | needs_revision | no |
| `pdf` | tool | needs_revision | no |

## Deterministic Quality Gate
Initial quality gate after full run:
- Issues: 16
- Major: 16
- Publishable by rules: false

After improving markdown/markup-insensitive evidence matching:
- Issues: 11
- Major: 11
- Publishable by rules: false

Current remaining issue families:
- `EVIDENCE_QUOTE_NOT_FOUND`: 10
- `SCRIPT_TOOL_WITHOUT_SCRIPT_MANIFEST`: 1

## Interpretation
This benchmark confirms that the pipeline now produces rich, complete, multi-surface outputs for five real skills. The output is materially useful for learning, reuse, report browsing, Obsidian vault navigation, and anchor composition.

However, the deterministic quality gate still fails the full five-skill run. The remaining failures are mostly not broad decomposition failures. They are concentrated in evidence exactness:

1. Some model evidence quotes are paraphrases or compact summaries of real source passages.
2. Some quotes omit Markdown markers, table formatting, or link syntax that exist in the source.
3. Some `skill-creator` workflow evidence appears semantically plausible but not exact enough for strict publication.
4. One `skill-creator` CLI tool claim is treated as required without a script manifest, which should be reviewed or downgraded.

## Strict Verdict
- End-to-end pipeline: pass.
- Export completeness: pass.
- Obsidian/repo/report/cinema generation: pass.
- Anchor generation and composition: pass.
- Reviewer usefulness: pass.
- Deterministic publishability: fail for the full five-skill benchmark.
- Public benchmark readiness without post-review: not yet.

## Quality Assessment
DeepSeek v4pro performs well at structural decomposition and workflow reconstruction. It is strong enough for LetUen’s core use case, but it still needs deterministic evidence repair before public-grade publication.

The system improvements from Sprint A-D are validated by the one-skill run, where quality issues dropped to zero. The five-skill run shows the next bottleneck: evidence repair must become source-aware, not just markup-tolerant.

## Recommended Next Fix
Add a source-aware evidence repair pass:

1. For each evidence quote, search the referenced source file.
2. If exact match fails, run fuzzy matching against nearby source lines.
3. Replace paraphrased quotes with exact short source substrings.
4. If no sufficiently similar source line exists, downgrade evidence to inferred and lower confidence.
5. Record every repair in `*.normalization.json`.

Acceptance target for the next run:
- `EVIDENCE_QUOTE_NOT_FOUND = 0`
- `SCRIPT_TOOL_WITHOUT_SCRIPT_MANIFEST = 0` or explicitly justified as a real issue
- Full five-skill benchmark publishable by deterministic rules, or failed only on genuinely unsupported model claims.
