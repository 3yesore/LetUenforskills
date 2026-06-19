# LetUen / Agent Skill Anatomy

[![CI](https://github.com/3yesore/LetUenforskills/actions/workflows/ci.yml/badge.svg)](https://github.com/3yesore/LetUenforskills/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/3yesore/LetUenforskills?include_prereleases)](https://github.com/3yesore/LetUenforskills/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

LetUen is a multi-agent research harness for deconstructing Agent Skills and workflows into readable reports, reusable anchors, Obsidian notes, and structured data assets.

LetUen 是一个多 Agent 研究工具，用于把 Agent Skills 与工作流拆解成可读报告、可复用锚点、Obsidian 知识库和结构化数据资产。

## What It Produces 产出

- **Readable report / 拆解说明书**: explains what a skill is, how it is composed, how it triggers, and how it can be reused.
- **Cinema + Repo surfaces / 展示页面**: local static UI for presenting decomposition results with the same visual language as the report.
- **Obsidian vault / 知识库**: bilingual notes, MOCs, Mermaid maps, evidence notes, patterns, and reusable assets.
- **Anchor pack / 可组合 Skill 包**: `skills/asa-*` method skills plus anchor composition contracts for non-destructive reuse.
- **Quality gates / 质量门禁**: deterministic checks, reviewer summaries, evidence repair, and source-grounded artifacts.

## Repository Scope 仓库定位

This repository currently contains the full LetUen project: Python harness, static UI, documentation, sample outputs, tests, and the packaged internal skill anchor pack. A separate skill-only repository can be published later from `package-letuen-skill` artifacts.

当前仓库是完整 LetUen 项目仓库：包含 Python 拆解链路、静态 UI、文档、样例产物、测试，以及已打包的内置 skill anchor pack。后续可以再从 `package-letuen-skill` 产物拆出 skill-only 仓库。

## Quick Start 快速开始

```powershell
cp .env.example .env
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.example.yaml
python -m asa export-letuen --run runs\<run-id> --output dist\letuen-demo
```

For a local visual demo:

```powershell
npm install
npm run demo:export
npm run demo:serve
```

Open `http://localhost:4173/`.

## Real Model Calls 真实模型调用

The default example config uses `mock` so the harness runs without API keys. For real multi-agent calls, copy one provider config and set the matching environment variable in `.env` or your shell.

默认示例配置使用 `mock`，无需 API key 即可运行。真实多 Agent 调用时，复制对应 provider 配置，并在 `.env` 或 shell 中设置对应环境变量。

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
python -m asa plan-run --config anatomy.config.yaml --limit-skills 1
python -m asa run --config anatomy.config.yaml --limit-skills 1
```

## Harness Flow 分析流程

```text
GitHub URL / Local Path
  -> Collector
  -> Structure Analyst
  -> Workflow Analyst
  -> Pattern Miner
  -> Asset Builder
  -> Reviewer
  -> Report / Vault / Data / Anchors
```

## Repository Layout 仓库结构

```text
src/                  Python harness, providers, exporters, quality gates
site/                 Static local UI: home, cinema, repo, data/settings surfaces
skills/               LetUen internal method skills and anchor-aware workflow skills
docs/                 Design specs, harness contracts, UI/output strategy
examples/             Sample skill, sample vault, anchor composition examples
runs/demo-multi-skill Committed demo run used by local export/demo scripts
releases/             Developer-preview skill anchor pack archives
tests/                Unit tests for runtime, exporters, quality, packaging
```

## Skill Anchor Pack 技能包

The current developer-preview skill pack is available in the GitHub Release and under `releases/`:

- `releases/letuen-skill-anchor-pack-v0.2.0-dev.zip`
- `releases/letuen-skill-anchor-pack-v0.2.0-dev.tar.gz`
- `releases/SHA256SUMS.txt`

Rebuild it locally with:

```powershell
$env:PYTHONPATH='src'
python -m asa package-letuen-skill --output releases --version v0.2.0-dev
```

## Local Model Bridge 本地模型测试 Bridge

The settings page calls a local-only bridge for connection tests and home-page GitHub URL analysis. Start it before clicking `测试连接 / Test connection` or running the local UI analysis flow:

```powershell
$env:PYTHONPATH='src'
python scripts/local_bridge.py
```

Then open `http://localhost:4173/settings/models/`. The bridge does not persist keys; for real CLI runs, store keys in `.env` using the mapped env var such as `DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY`, `DASHSCOPE_API_KEY`, or `OPENAI_API_KEY`.

## Docs 文档

- `docs/fork-ready-guide.md`: clone/fork usage, CI, sample vault workflow.
- `docs/harness-spec.md`: runtime state machine and quality gates.
- `docs/agent-protocol.md`: agent responsibilities and boundaries.
- `docs/evidence-spec.md`: evidence object contract and confidence rules.
- `docs/provider-spec.md`: model provider interface, retry, and OpenAI-compatible adapter.
- `docs/letuen-usage-guide.md`: end-to-end LetUen commands for report, vault, data, anchors, and composition plans.
- `docs/letuen-skill-anchor-pack-design.md`: LetUen anchor-based skill decomposition and recomposition method pack.
- `docs/graph-data-surface-spec.md`: data table contracts, graph nodes/edges, manifest, and UI expectations.
- `docs/ui-strategy.md`: local research dashboard and public website direction.

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






