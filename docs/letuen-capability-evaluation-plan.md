# LetUen Skill Capability Evaluation Plan

This document defines how to review and evaluate the practical capability of the LetUen Skill Anchor Pack after v0.2.0-dev.

目标：评测 LetUen 这组内置拆解 skills 是否真的能帮助用户“拆得完全、看得明白、借得安全、拼得合理”。

## 1. Evaluation Questions

The evaluation should answer six questions:

1. **Decomposition completeness**: Did LetUen identify the skill identity, trigger, boundary, resources, workflow, evidence, outputs, and reuse points?
2. **Anchor usefulness**: Are the extracted anchors small enough to borrow and meaningful enough to reuse?
3. **Composition quality**: Does the composition plan select anchors that fit the user goal and reject irrelevant anchors?
4. **Non-destructive behavior**: Does LetUen preserve existing user skills and avoid accidental workflow solidification?
5. **Learning value**: Can both beginners and skill designers understand the result from report and Obsidian?
6. **Model robustness**: Do different LLM providers produce stable enough decomposition when guided by the same method skills?

## 2. Test Set

Use at least four categories of skill repos:

| Category | Purpose | Suggested Source |
|---|---|---|
| Small single-skill repo | Basic extraction and report readability | local `examples/sample-skill` |
| Real research skill | Evidence/resource/workflow richness | GitHub skill repo with `SKILL.md` + references |
| Tool/script skill | Resource role and side-effect boundary | skill with `scripts/` |
| Multi-skill registry | Trigger conflicts and composition selection | repo with many skills |

Each evaluated source should record:

```yaml
source_name:
source_url_or_path:
commit_or_ref:
skill_count:
model_provider:
model_name:
run_id:
evaluator:
notes:
```

## 3. Evaluation Flow

For each source, first scaffold the evaluation folder:

```powershell
$env:PYTHONPATH='src'
python -m asa init-evaluation `
  --name <source-name> `
  --source <source-url-or-path> `
  --output evaluations `
  --model <model-route>
```

Then run analysis and export:

```powershell
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.yaml --limit-skills 3
python -m asa export-letuen `
  --run runs\<run-id> `
  --output evaluations\<source-name>\letuen `
  --composition-request evaluations\<source-name>\composition_request.yaml
```

Then inspect:

- `report/index.html`
- `vault/00 Maps/Agent Skill Anatomy MOC.md`
- `vault/00 Maps/Anchor Index.md`
- `vault/07 Anchors/*.md`
- `anchors/anchors.json`
- `anchors/composition_plan.json`
- `data/graph-data.json`
- `letuen_manifest.json`

## 4. Scoring Rubric

Score each dimension from 0 to 5.

### 4.1 Decomposition Completeness

| Score | Meaning |
|---:|---|
| 0 | Mostly missing or unusable |
| 1 | Only generic summary |
| 2 | Identity and rough workflow extracted |
| 3 | Trigger/resource/workflow/evidence mostly present |
| 4 | Complete anatomy with minor gaps |
| 5 | Complete, evidence-grounded, and easy to verify |

### 4.2 Anchor Usefulness

| Score | Meaning |
|---:|---|
| 0 | No useful anchors |
| 1 | Anchors are too large or vague |
| 2 | Some anchors useful but noisy |
| 3 | Anchors mostly borrowable |
| 4 | Anchors are well-sized and evidence-backed |
| 5 | Anchors can be directly reused across tasks |

### 4.3 Composition Quality

| Score | Meaning |
|---:|---|
| 0 | Selection fails or unsafe |
| 1 | Selects irrelevant anchors |
| 2 | Selects useful anchors but misses risks |
| 3 | Reasonable selection and rejection |
| 4 | Clear fit, risk, dispatch, and solidification state |
| 5 | Plan is immediately usable and safely adaptable |

### 4.4 Report Readability

| Score | Meaning |
|---:|---|
| 0 | Hard to read |
| 1 | Mostly raw artifacts |
| 2 | Understandable only to project authors |
| 3 | Beginners can follow the main idea |
| 4 | Beginners and experts both have clear paths |
| 5 | Feels like a polished skill decomposition manual |

### 4.5 Obsidian Learning Value

| Score | Meaning |
|---:|---|
| 0 | Vault unusable |
| 1 | Notes exist but disconnected |
| 2 | MOC works but graph is weak |
| 3 | Skill/workflow/anchor notes are navigable |
| 4 | Native links support real study and reuse |
| 5 | Vault is a high-quality reusable learning knowledge base |

### 4.6 Non-Destructive Safety

| Score | Meaning |
|---:|---|
| 0 | Mutates or overwrites user skills unexpectedly |
| 1 | Ambiguous side effects |
| 2 | Mostly safe but unclear dispatch policy |
| 3 | Sidecar outputs and dispatch policy present |
| 4 | Trigger conflicts and solidification clearly handled |
| 5 | Safe-by-default behavior is obvious and verifiable |

## 5. Required Review Notes

For each run, write:

```markdown
# LetUen Evaluation: <source-name>

## Summary
- Source:
- Model:
- Run:
- Overall score:

## Scores
| Dimension | Score | Notes |
|---|---:|---|
| Decomposition completeness | | |
| Anchor usefulness | | |
| Composition quality | | |
| Report readability | | |
| Obsidian learning value | | |
| Non-destructive safety | | |

## Best Findings

## Missing Or Weak Areas

## Unsafe Or Overstated Claims

## Recommended Improvements

## Keep / Change / Drop Decision
```

## 6. Model Comparison Protocol

Multi-model comparison is only for development testing. It should not become a user-facing model selection page yet.

For the same source and same commit, run at least two providers/configs:

```text
OpenAI / GPT route
DeepSeek / V4 Pro route
Claude route
Qwen or Kimi route when available
```

Compare:

- anchor count by type;
- unsupported claims;
- workflow completeness;
- reuse anchor quality;
- bilingual quality;
- Obsidian note usefulness;
- composition plan quality.

Use `asa-model-comparison-judge` to summarize:

- `anchor_consensus`
- `anchor_disagreement`
- `best_model_per_anchor_type`

## 7. Pass Criteria For v0.2.0-dev

A source passes if:

- average score is at least 3.5 / 5;
- non-destructive safety is at least 4 / 5;
- report readability is at least 3 / 5;
- at least one workflow anchor and one validation/evidence/risk anchor are useful;
- composition plan does not suggest modifying existing skills unless explicitly requested.

## 8. Failure Criteria

A source fails if:

- major unsupported claims appear in the report;
- composition plan selects anchors that conflict with the stated goal;
- trigger conflicts are ignored;
- Obsidian vault cannot be opened or navigated;
- the result encourages overwriting user skills by default.

## 9. Next Improvements After Evaluation

Likely improvements after real review:

- richer deterministic anchor exporter;
- stricter anchor confidence scoring;
- better composition compatibility matrix;
- report cards for rejected anchors and risk anchors;
- Obsidian templates for anchor reuse recipes;
- model-specific calibration prompts.
