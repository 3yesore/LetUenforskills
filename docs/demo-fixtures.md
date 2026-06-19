# Demo Fixtures / 演示数据

This project keeps a small, committed demo run so contributors can preview the cinematic repo page without calling an LLM or GitHub.

本项目保留一个可提交的 demo run，方便贡献者无需调用 LLM 或 GitHub，也能直接预览 cinematic repo 页。

## Bundled Demo Run

Default fixture:

```text
runs/demo-multi-skill/
```

It contains two skill packages:

| Skill | Status | Purpose |
| --- | --- | --- |
| `research-skill` | `approved` | Richer demo skill with triggers, tools, workflow steps, reusable candidates, and outputs. |
| `sample-skill` | `needs_revision` | Minimal/mock skill that demonstrates sparse extraction and review issues. |

它包含两个 skill：

| Skill | 状态 | 用途 |
| --- | --- | --- |
| `research-skill` | `approved` | 较完整的演示 skill，包含触发条件、工具、工作流步骤、复用候选和输出。 |
| `sample-skill` | `needs_revision` | 极简/mock skill，用于展示信息稀疏和 review issue。 |

## Quick Preview

```powershell
$env:PYTHONPATH='src'
python scripts/export_demo.py
python -m http.server 4173 -d site
```

Open:

```text
http://localhost:4173/cinema/
```

Node shortcut:

```powershell
npm run demo:export
npm run demo:serve
```

## What It Exercises

The fixture is designed to exercise these UI paths:

- `Repo / Skill` view switching.
- Multi-skill selector in `Skill` view.
- Six-card skill anatomy: `Trigger / Boundary / Tools / Workflow / Evidence / Reuse`.
- Run Dossier with trust strip and output links.
- Web report with two skill detail pages.

该 fixture 用于覆盖以下 UI 路径：

- `Repo / Skill` 视图切换。
- `Skill` 视图中的多 skill 选择器。
- 六卡 skill 解剖：`Trigger / Boundary / Tools / Workflow / Evidence / Reuse`。
- 带可信状态条和输出入口的 Run Dossier。
- 包含两个 skill 详情页的 Web report。

## Demo vs Real Run Labels

The cinematic Run Dossier marks this fixture as `demo fixture`. This label is intentional: it prevents users from mistaking the bundled demo for a real model analysis.

cinematic 的 Run Dossier 会把该 fixture 标记为 `demo fixture`。这是刻意设计的：避免用户把内置演示误认为真实模型分析。

Run labels are generated as follows:

- `demo fixture`: run directory name starts with `demo-`.
- `mock run`: provider is `mock` but the run is not a bundled demo.
- `real run`: non-mock provider exported from canonical artifacts.
## File Map

```text
runs/demo-multi-skill/
  run.json
  inventory.json
  quality_report.json
  review_summary.json
  patterns/patterns.json
  sources/<source>/inventory.json
  skills/<skill-id>/structure_analysis.json
  skills/<skill-id>/workflow_analysis.json
  skills/<skill-id>/review_report.json
  skills/<skill-id>/source_snapshot.json
```

Key files:

- `inventory.json`: aggregate source and skill package inventory.
- `skills/*/structure_analysis.json`: identity, triggers, context strategy, tools, risks.
- `skills/*/workflow_analysis.json`: workflow steps, decisions, failures, reusable candidates.
- `skills/*/review_report.json`: publish status, review issues, scores.
- `review_summary.json`: run-level review totals used by trust and report sections.
- `patterns/patterns.json`: reusable pattern candidates.

## Replacing The Demo With A Real Run

To preview a real run in the same UI:

```powershell
$env:PYTHONPATH='src'
python -m asa export-report --run runs/<real-run-id> --output site/report
python -m http.server 4173 -d site
```

The exporter writes both:

- `site/report/` for the web report.
- `site/cinema/cinema-data.json` for the cinematic repo page.

If the real run contains multiple skills, the cinematic page will show the Skill selector automatically.

如果真实 run 包含多个 skills，cinematic 页面会自动显示 Skill 选择器。

## Adding Another Fixture

Recommended rules:

1. Keep fixture artifacts small and deterministic.
2. Avoid secrets, API keys, downloaded repos, or large files.
3. Include at least two skills if the fixture is meant to test skill switching.
4. Make one skill rich and one skill sparse so the UI can show contrast.
5. Update `scripts/export_demo.py` only if the default demo run changes.

建议规则：

1. fixture artifact 保持小而确定。
2. 不要包含密钥、API key、下载的大仓库或大文件。
3. 如果用于测试 skill 切换，至少包含两个 skills。
4. 最好一个 skill 信息较完整，一个 skill 信息较稀疏，方便 UI 展示差异。
5. 只有默认 demo run 改变时，才需要更新 `scripts/export_demo.py`。

