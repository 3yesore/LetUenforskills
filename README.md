# Agent Skill Anatomy

Agent Skill Anatomy is a multi-agent analysis harness for deconstructing AI agent skills and workflows into reusable knowledge assets.

Agent Skill Anatomy 是一个多 Agent 分析框架，用于把 AI Agent Skills 与工作流拆解成可学习、可追溯、可复用的知识资产。

## Goal 目标

The mid-term goal is a fork-ready and clone-ready project: configure API keys and GitHub sources, run the harness, and generate a bilingual Obsidian vault.

中期目标是做到 fork 即用、clone 即用：配置模型 API key 和 GitHub 源，运行 harness，即可生成中英双语 Obsidian 知识库。

## Core Outputs 核心产物

- Structured JSON artifacts for each analysis stage.
- Evidence-grounded bilingual Obsidian notes.
- Reusable skill design patterns, checklists, templates, and Mermaid workflow diagrams.
- Review reports that flag unsupported claims, weak evidence, and over-inference.

## Docs 文档

- `docs/fork-ready-guide.md`: clone/fork usage, CI, sample vault workflow.
- `docs/harness-spec.md`: runtime state machine and quality gates.
- `docs/agent-protocol.md`: agent responsibilities and boundaries.
- `docs/evidence-spec.md`: evidence object contract and confidence rules.
- `docs/provider-spec.md`: model provider interface, retry, and OpenAI adapter.
- `docs/roadmap.md`: long-term phases and open-source direction.
- `docs/architecture.md`: layered system architecture.
- `docs/skill-decomposition-design.md`: evidence-first decomposition taxonomy, deterministic artifacts, LLM agent chain, and feedback forms.
- `docs/user-facing-output-design.md`: final user-visible surfaces, report sections, skill pages, graph, vault, and review cards.
- `docs/report-manual-spec.md`: report-as-manual IA for beginners, experts, evidence, and reuse.
- `docs/llm-skill-integration-design.md`: design for injecting internal meta-skills into LLM-backed analysis stages.
- `docs/letuen-usage-guide.md`: end-to-end LetUen commands for report, vault, data, anchors, and composition plans.
- `docs/release-v0.2.0-dev-checklist.md`: dev release acceptance checklist, package contents, and remaining risks.
- `docs/letuen-capability-evaluation-plan.md`: rubric for reviewing real LetUen skill capability.
- `docs/letuen-skill-anchor-pack-design.md`: LetUen anchor-based skill decomposition and recomposition method pack.
- `docs/letuen-lightweight-profile.md`: lightweight L1/L2/L3 profile for keeping LetUen thin and optional.
- `docs/letuen-anchor-schema.md`: Skill Anchor, composition request, selection, matrix, and plan contracts.
- `docs/letuen-harness-integration-spec.md`: harness rules for safe anchor composition inside user projects.
- `docs/letuen-non-destructive-invocation-policy.md`: trigger conflict, dispatch, and sidecar-first invocation policy.
- `docs/model-comparison-spec.md`: internal development/testing protocol for controlled model calibration, scoring, and disagreement analysis.
- `docs/graph-data-surface-spec.md`: data table contracts, graph nodes/edges, manifest, and UI expectations.
- `docs/acceptance-checklist.md`: handoff checklist for docs, runtime, UI, graph/data/vault, and validation.
- `docs/provider-strategy.md`: multi-provider and Chinese model support strategy.
- `docs/benchmark-spec.md`: benchmark lab fixtures, roles, metrics, and reports.
- `docs/output-strategy.md`: Obsidian, visualization, reusable assets, and future website outputs.
- `docs/ui-strategy.md`: staged UI plan from landing page to local research dashboard.
- `docs/landing-page-spec.md`: first public website information architecture.
- `docs/dashboard-roadmap.md`: static report browser and local dashboard roadmap.
- `docs/quality-spec.md`: deterministic quality layers and current rule set.
- `CONTRIBUTING.md`: contribution workflow.

## Harness Flow 分析流程

```text
GitHub URL / Local Path
  -> Collector
  -> Structure Analyst
  -> Workflow Analyst
  -> Pattern Miner
  -> Asset Builder
  -> Translator
  -> Reviewer
  -> Obsidian Vault
```

## Repository Layout 仓库结构

```text
docs/                 Design specs and implementation notes
prompts/              Role prompts for each agent
schemas/              JSON Schema contracts for artifacts
scripts/              Local utility scripts
templates/obsidian/   Obsidian note templates
taxonomy/             Skill types, workflow patterns, glossary
examples/             Example configs and outputs
runs/                 Generated run artifacts, usually ignored later
vault/                Generated Obsidian vault, optionally committed
```

## Quick Start 草案

```powershell
cp .env.example .env
cp anatomy.config.example.yaml anatomy.config.yaml
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.example.yaml
```


## LetUen Anchor Workflow

For the current anchor-oriented workflow, use `export-letuen` after a run:

```powershell
$env:PYTHONPATH='src'
python -m asa export-letuen `
  --run runs\demo-multi-skill `
  --output tmp\letuen-demo `
  --composition-request examples\anchor-composition\sample-skill\composition_request.temporary.yaml
```

This writes `report/`, `vault/`, `data/`, `anchors/anchors.json`, optional `anchors/composition_plan.json`, and `letuen_manifest.json`. See `docs/letuen-usage-guide.md` for the full flow.

Use `sources.github.example.yaml` as a starting point for GitHub URL analysis.

GitHub sources first use shallow `git clone --filter blob:none`. If clone fails, the collector falls back to GitHub zip archives and records `acquisition_method` in `inventory.json`.

Use `asa smoke-github` for collector-only remote checks. It does not run LLM agents.

## Real Model Calls 真实模型调用

The default example config uses `mock` so the harness runs without API keys. For real multi-agent calls, choose one mapped config from the UI/model registry and add the matching API key env var to `.env`.

默认示例配置使用 `mock`，因此无需 API key 即可跑通。若要启用真实多 Agent 模型调用，请从 UI/model registry 选择一个已映射配置，并在 `.env` 中填写对应 API key 环境变量。


Mapped model routes used by the local UI are recorded in `models/ui-presets.yaml`:

UI 中的模型选择不是纯展示，真实映射记录在 `models/ui-presets.yaml`：

| UI route | Config file | API key env | Base URL |
| --- | --- | --- | --- |
| `OpenAI · gpt-5.2` | `anatomy.openai.example.yaml` | `OPENAI_API_KEY` | `https://api.openai.com/v1` |
| `Claude · Opus 4.5` | `anatomy.claude.example.yaml` | `ANTHROPIC_API_KEY` | `https://api.anthropic.com/v1` |
| `DeepSeek · V4 Pro` | `anatomy.deepseek.example.yaml` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com/v1` |
| `Qwen · Qwen3.7 Max` | `anatomy.qwen.example.yaml` | `DASHSCOPE_API_KEY` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| `Moonshot · moonshot-v1-32k` | `anatomy.moonshot.example.yaml` | `MOONSHOT_API_KEY` | `https://api.moonshot.cn/v1` |
```powershell
cp anatomy.openai.example.yaml anatomy.config.yaml
cp sources.github.example.yaml sources.yaml
notepad .env
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.yaml
```

The OpenAI provider uses the Responses API with JSON Schema output. Each analyst/reviewer stage is a separate model call and writes schema-validated artifacts under `runs/<run-id>/`.

OpenAI provider 使用 Responses API 的 JSON Schema 输出。每个 analyst/reviewer 阶段都是独立模型调用，并会在 `runs/<run-id>/` 下写入通过 schema 校验的 artifacts。


### Local Model Bridge 本地模型测试 Bridge

The settings page calls a local-only bridge for real connection tests. Start it before clicking `测试连接 / Test connection`:

模型配置页通过本地 bridge 做真实连接测试。点击 `测试连接 / Test connection` 前先启动：

```powershell
$env:PYTHONPATH='src'
python scripts/local_bridge.py
```

Then open `http://localhost:4173/settings/models/`, paste a newly generated API key in the temporary key field, and test the selected provider. The bridge does not persist keys; for real runs, store keys in `.env` using the mapped env var such as `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, `DASHSCOPE_API_KEY`, or `OPENAI_API_KEY`.

然后打开 `http://localhost:4173/settings/models/`，在临时 Key 输入框粘贴新生成的 API key，再测试所选 provider。bridge 不持久化密钥；真实运行时请把 key 写入 `.env`，例如 `DEEPSEEK_API_KEY`、`ANTHROPIC_API_KEY`、`DASHSCOPE_API_KEY` 或 `OPENAI_API_KEY`。

The same bridge also powers the home-page GitHub URL entry for local real runs:

同一个 bridge 也负责首页 GitHub URL 拆解入口的本地真实运行：

```text
POST /api/analyze/plan
POST /api/analyze/run
```

`/api/analyze/run` writes temporary source/config files, runs `python -m asa run --limit-skills 1`, then refreshes `site/report`, `site/data`, `site/graph`, `site/vault`, and the Demo manifest. If the bridge is not running, the home page falls back to the visual Demo animation.

`/api/analyze/run` 会写入临时 source/config，执行 `python -m asa run --limit-skills 1`，然后刷新 `site/report`、`site/data`、`site/graph`、`site/vault` 与 Demo manifest。如果 bridge 未启动，首页会回退到视觉 Demo 动画。
## Multi-Skill Demo 多 Skill Demo

Use the bundled `runs/demo-multi-skill` fixture to preview the Demo/repo page with real `Repo / Skill` switching and a visible Skill selector. See `docs/demo-fixtures.md` for fixture structure and replacement guidance.

使用内置 `runs/demo-multi-skill` 样例，可以直接预览 Demo/repo 页里的 `Repo / Skill` 切换和多 Skill 选择器。fixture 结构和替换真实 run 的说明见 `docs/demo-fixtures.md`。

```powershell
$env:PYTHONPATH='src'
python scripts/export_demo.py
python -m http.server 4173 -d site
```

Then open:

```text
http://localhost:4173/cinema/  # visible label: Demo
```

If Node is available, the same export can be run with:

```powershell
npm run demo:export
npm run demo:serve
```
## CLI Commands 命令

```powershell
$env:PYTHONPATH='src'
python -m asa collect --source examples/sample-skill --output runs/manual-collect/inventory.json
python -m asa run --config anatomy.config.example.yaml
python -m asa validate --run runs/<run-id>
python -m asa review-run --run runs/<run-id> --output runs/<run-id>/review_summary.json
python -m asa quality-run --run runs/<run-id> --output runs/<run-id>/quality_report.json
python -m asa export-report --run runs/<run-id> --output site/report
python -m asa export-vault --run runs/<run-id> --output vault
python -m asa export-all --run runs/<run-id> --output dist/<run-id>
python -m asa export-all --run runs/<run-id> --output site  # linked local web demo
python -m asa smoke-github --sources sources.smoke.github.yaml --output runs/github-smoke
python -m asa plan-run --config anatomy.openai.example.yaml --limit-skills 1 --output runs/plan-openai.json
python -m asa run --config anatomy.openai.example.yaml --limit-skills 1
```

## Current Vault Output 当前知识库输出

The runtime currently renders:

- `vault/00 Maps/`: source, skill, and workflow pattern MOCs.
- `vault/01 Sources/`: one source note per analyzed repository or local source.
- `vault/02 Skills/`: one bilingual skill anatomy note per skill package.
- `vault/03 Patterns/`: reusable pattern notes from pattern mining artifacts.

当前 runtime 会生成：

- `vault/00 Maps/`：source、skill、workflow pattern 的 MOC 页面。
- `vault/01 Sources/`：每个源仓库/本地源一份 source note。
- `vault/02 Skills/`：每个 skill package 一份中英双语 anatomy note。
- `vault/03 Patterns/`：从 pattern mining artifact 渲染出的模式笔记。

A committed sample output is available under `examples/sample-vault/`.

仓库内置了一份示例输出：`examples/sample-vault/`。

## Evidence-First Analysis 证据优先分析

Agent Skill Anatomy treats evidence as a first-class artifact. Analyst agents should attach source paths, short quotes, evidence types, and confidence levels to important claims. Inferred claims are allowed, but they must be marked as inferred and should not use high confidence.

Agent Skill Anatomy 将 evidence 视为一等产物。分析 Agent 应为重要结论附上 source path、短 quote、evidence type 和 confidence。允许推断，但必须显式标记 inferred，且不应使用 high confidence。

See `docs/evidence-spec.md` for the evidence contract.

## Schema Validation Retry

Each LLM-backed agent call validates output before writing artifacts. If the output fails schema validation, the harness retries once with the validation error and previous invalid output. Artifacts are persisted only after successful validation.

每个真实模型 Agent 调用都会先校验输出，再写入 artifact。如果输出不符合 schema，harness 会带着校验错误和上一次无效输出重试一次。只有通过校验的结果才会持久化。

For first real-model runs, use `--limit-skills 1` to cap cost and inspect artifact quality before scaling up.

首次真实模型调用建议使用 `--limit-skills 1`，先控制成本并检查 artifact 质量，再扩大分析范围。

Use `asa plan-run` before real calls to list selected skills and estimate agent calls without invoking model agents.

真实调用前可先用 `asa plan-run` 查看将分析的 skills 和预计 agent calls，不会调用模型 Agent。

After a run completes, use `asa review-run` to summarize reviewer statuses, scores, unsupported claims, missing evidence, and approval state.

运行完成后，可用 `asa review-run` 汇总 reviewer 状态、分数、unsupported claims、missing evidence 和发布批准状态。

Use `asa quality-run` for deterministic checks such as high confidence without evidence, inferred high-confidence claims, missing source paths, and long quotes.

可用 `asa quality-run` 进行程序化质量检查，例如 high confidence 缺 evidence、推断却 high confidence、source path 不存在、quote 过长等。

Use `asa export-report` to turn a completed run into a static browsable report with overview, skill detail pages, quality issues, reviewer summaries, patterns, and copied canonical JSON artifacts.

可用 `asa export-report` 将一次完成的 run 导出为静态可浏览报告，包括总览、技能详情页、质量问题、reviewer 汇总、patterns，以及可追溯的原始 JSON artifacts。

Use `asa export-vault` to rebuild an Obsidian-ready Markdown vault from any completed run. Use `asa export-all` to emit report and vault outputs together under one distribution directory.

可用 `asa export-vault` 从任意完成的 run 重建 Obsidian Markdown 知识库。可用 `asa export-all` 将 report 与 vault 一起输出到统一分发目录。

## Resume Runs 恢复运行

```powershell
$env:PYTHONPATH='src'
python -m asa resume --run runs/<run-id>
```

Resume mode reuses existing valid artifacts and regenerates missing or invalid stage outputs. If schema validation still fails after retry, the harness writes a sibling `*.error.json` artifact for debugging.

恢复模式会复用已有且通过 schema 校验的 artifact，并重新生成缺失或无效的阶段输出。如果重试后仍不合 schema，harness 会写入相邻的 `*.error.json` 便于排查。

The current repository contains the early design foundation and a lightweight inventory collector. LLM-backed multi-agent stages are specified in `docs/agent-protocol.md` and will be implemented against the schemas in `schemas/`.

当前仓库已包含可运行的多 Agent 拆解链路、DeepSeek/OpenAI-compatible provider、Report/Vault/Data/Graph 导出，以及内置 meta-skills 方法层。`docs/agent-protocol.md` 和 `schemas/` 仍是阶段契约与 artifact 约束来源。






