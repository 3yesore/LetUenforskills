# LetUen Usage Guide

LetUen is the anchor-oriented layer inside Agent Skill Anatomy. It helps users decompose a skill into reusable anchors, inspect the result in web/Obsidian/data surfaces, and optionally plan a lightweight composition without modifying existing user skills.

LetUen 是 Agent Skill Anatomy 内部的锚点化拆解层。它把 skill 拆成可学习、可借用、可组合的 anchors，并把结果输出到网页版报告、Obsidian、数据文件和可选组合计划。默认不修改用户已有 skills。

## 1. Mental Model

```text
source repo / local skill
  -> asa run
  -> run artifacts
  -> asa export-letuen
  -> report + vault + data + anchors + optional composition plan
```

The important distinction is:

- `run` analyzes a source skill repository.
- `export-anchors` turns run artifacts into reusable anchor cards.
- `plan-composition` selects compatible anchors for a user goal.
- `export-letuen` bundles report, vault, data, anchors, and optional composition plan in one output directory.

## 2. Fast Path

Use the bundled demo run first:

```powershell
$env:PYTHONPATH='src'
python -m asa export-letuen `
  --run runs\demo-multi-skill `
  --output tmp\letuen-demo `
  --composition-request examples\anchor-composition\sample-skill\composition_request.temporary.yaml
```

Open:

- `tmp/letuen-demo/report/index.html`
- `tmp/letuen-demo/vault/Open in Obsidian.html`
- `tmp/letuen-demo/anchors/anchors.json`
- `tmp/letuen-demo/anchors/composition_plan.json`
- `tmp/letuen-demo/letuen_manifest.json`

## 3. Full Source Analysis

For a real source, configure `anatomy.config.yaml` and run:

```powershell
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.yaml --limit-skills 3
```

Then export the complete LetUen bundle:

```powershell
python -m asa export-letuen `
  --run runs\<run-id> `
  --output dist\letuen-<run-id>
```

If you want a composition plan, provide a request:

```powershell
python -m asa export-letuen `
  --run runs\<run-id> `
  --output dist\letuen-<run-id> `
  --composition-request examples\anchor-composition\sample-skill\composition_request.temporary.yaml
```

## 4. Output Layout

```text
letuen-output/
  report/
    index.html
    skills/*.html
  vault/
    00 Maps/Agent Skill Anatomy MOC.md
    00 Maps/Anchor Index.md
    07 Anchors/*.md
    07 Anchors/Composition Plan.md
    Open in Obsidian.html
  data/
    data_manifest.json
    graph-data.json
    *.jsonl / *.csv
  anchors/
    anchors.json
    composition_plan.json        # only when --composition-request is provided
  letuen_manifest.json
```

## 5. What Users See

### Web Report

The report is the primary readable surface. It explains:

- what the skill is;
- how it is composed;
- how workflow steps connect;
- which evidence supports claims;
- which anchors can be borrowed;
- what the composition plan selects or rejects.

### Obsidian Vault

The vault is the learning and reuse surface. It includes native links so Obsidian Graph View can show relationships without custom graph clutter:

```text
MOC -> Skill Index -> Skill Notes
MOC -> Anchor Index -> Anchor Notes -> Composition Plan
MOC -> Workflow Index -> Workflow Notes
MOC -> Reuse Asset Index -> Pattern Notes
```

### Data

The data output supports research and future visualization:

- `graph-data.json`
- `skills.jsonl`
- `workflow_trace.jsonl`
- `evidence_audit.jsonl`
- `reuse_assets.jsonl`

### Anchors

`anchors/anchors.json` is the machine-readable reuse layer. Typical anchor types include:

- `identity_anchor`
- `trigger_anchor`
- `workflow_anchor`
- `validation_anchor`
- `risk_anchor`
- `evidence_anchor`
- `reuse_anchor`

## 6. Composition Requests

A composition request tells LetUen what kind of reuse the user wants. It prevents the harness from assuming every reuse should become a full workflow or new skill.

Example:

```yaml
schema_version: 1
goal:
  type: temporary_composition
  description: Borrow workflow and validation anchors for a one-off task.
constraints:
  avoid_full_workflow: true
  preserve_existing_skill_structure: true
  allowed_side_effects:
    - none
selected_anchor_types:
  - workflow_anchor
  - validation_anchor
selected_source_skills: []
excluded_source_skills: []
preferred_outputs:
  - markdown
  - json
```

Use `temporary_composition` when you only want to borrow behavior for one task. Use `new_skill_spec` or `full_workflow_blueprint` only when you explicitly want persistent artifacts.

## 7. Separate Commands

If you do not want the all-in-one bundle, run the steps separately.

Export anchors only:

```powershell
python -m asa export-anchors --run runs\<run-id> --output tmp\anchors.json
```

Plan composition only:

```powershell
python -m asa plan-composition `
  --anchors tmp\anchors.json `
  --request path\to\composition_request.yaml `
  --output tmp\composition_plan.json
```

Export standard surfaces only:

```powershell
python -m asa export-all --run runs\<run-id> --output site
```

## 8. Non-Destructive Defaults

LetUen defaults are intentionally conservative:

- existing user skills remain primary;
- trigger conflicts produce dispatch policy instead of overwrites;
- composition outputs are sidecar files;
- `solidification.requested` is false unless the request explicitly asks for `full_workflow_blueprint` or `new_skill_spec`;
- Obsidian uses native links and Graph View instead of custom graph clutter.

## 9. Evaluation Scaffold

To prepare a real capability review, create an evaluation folder:

```powershell
python -m asa init-evaluation `
  --name sample-real-skill `
  --source https://github.com/example/skill-repo `
  --output evaluations `
  --model deepseek-v4pro
```

This creates `composition_request.yaml`, `source.yaml`, and `evaluation.md` for scoring the result.

## 10. Validation

Recommended local checks:

```powershell
node --check site/script.js
$env:PYTHONPATH='src'
python -m unittest discover -s tests
python -m compileall src scripts -q
```

A successful current run should report all tests passing and should be able to execute:

```powershell
python -m asa export-letuen --run runs\demo-multi-skill --output tmp\letuen-demo
```

## 11. When To Use Which Surface

| Need | Surface |
|---|---|
| Quickly understand the skill | `report/index.html` |
| Learn and connect concepts | `vault/` in Obsidian |
| Reuse parts in another workflow | `anchors/anchors.json` |
| Plan safe recombination | `anchors/composition_plan.json` |
| Build visual/data experiments | `data/graph-data.json` and JSONL/CSV |
| Inspect source of truth | `report/artifacts/` |
