<p align="center">
  <img src="docs/assets/letuen-banner.svg" alt="LetUen — Agent Skill Anatomy" width="100%" />
</p>

# LetUen / Agent Skill Anatomy

<p align="center">
  <strong>中文</strong> · <a href="README.md">English</a>
</p>

<p align="center">
  <a href="https://github.com/3yesore/LetUenforskills/actions/workflows/ci.yml"><img src="https://github.com/3yesore/LetUenforskills/actions/workflows/ci.yml/badge.svg" alt="CI" /></a>
  <a href="https://github.com/3yesore/LetUenforskills/releases"><img src="https://img.shields.io/github/v/release/3yesore/LetUenforskills?include_prereleases" alt="Release" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="MIT License" /></a>
  <img src="https://img.shields.io/badge/output-Report%20%7C%20Obsidian%20%7C%20Graph-70dfcc" alt="Outputs" />
</p>

LetUen 是一个多 Agent 研究工具，用于把 Agent Skills 与 Agent 工作流拆解成可读说明书、可复用 anchors、Obsidian 知识库、图谱数据和可发布的 skill 包。

它面向两类需求：一是读懂一个 skill 到底如何组成、如何触发、如何调用资源；二是把有价值的能力片段抽出来，安全地拼接进自己的工作流，而不破坏原有 skills 结构。

## 为什么需要 LetUen

多数 skill 仓库只展示最终的 `SKILL.md`、脚本和资源，但不解释背后的设计逻辑。LetUen 会把一个 skill 仓库拆成结构化 anatomy：

- **它是什么**：身份、触发意图、边界、适合的用户请求形态。
- **它如何工作**：工作流阶段、工具使用、脚本、references、assets 和运行假设。
- **它为什么可信**：证据扎根、确定性质量门禁、reviewer 汇总和 evidence repair。
- **它如何复用**：anchors、composition plan、Obsidian 笔记、可复用模板和非破坏式集成建议。

## 核心产物

| 产物界面 | 能提供什么 | 状态 |
| --- | --- | --- |
| **Report** | 面向人阅读的 skill 拆解说明书。 | 可用 |
| **Cinema / Repo UI** | 本地静态展示页，用于呈现拆解结果。 | Demo 可用 |
| **Obsidian Vault** | 中英双语笔记、MOC、Mermaid 图、证据笔记和复用资产。 | 可用 |
| **Data / Graph** | JSONL、CSV、Mermaid 和图谱数据。 | 可用 |
| **Anchor Pack** | `skills/asa-*` 方法层 skills 与 anchor composition 契约。 | 开发预览 |
| **Quality Gates** | 确定性检查、reviewer 汇总、source-aware evidence repair。 | 可用 |

## 仓库定位

当前仓库是完整 LetUen 项目仓库，包含：

- Python harness 与 provider
- 静态 UI 展示页
- report / vault / data / graph 导出器
- 内置方法层 skills
- 测试与样例产物
- 已打包的开发预览版 skill anchor pack

后续可以从 `package-letuen-skill` 产物单独发布一个更轻量的 skill-only 仓库。目前保留完整仓库，是为了让 harness、UI、文档和 skill pack 同步演进。

## 快速开始

先运行 mock 流程，不需要模型 API key。

```powershell
cp .env.example .env
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.example.yaml
python -m asa export-letuen --run runs\<run-id> --output dist\letuen-demo
```

启动本地视觉展示页：

```powershell
npm install
npm run demo:export
npm run demo:serve
```

打开 `http://localhost:4173/`。仓库设置里启用 GitHub Pages，并选择 **GitHub Actions** 作为来源后，`Deploy GitHub Pages` workflow 会发布在线展示页。

## 真实模型调用

默认配置使用 `mock`。真实多 Agent 调用时，复制对应 provider 配置，并在 `.env` 或 shell 中设置对应 key。

| Provider route | Config file | API key env | Base URL |
| --- | --- | --- | --- |
| OpenAI · gpt-5.2 | `anatomy.openai.example.yaml` | `OPENAI_API_KEY` | `https://api.openai.com/v1` |
| Claude · Opus 4.5 | `anatomy.claude.example.yaml` | `ANTHROPIC_API_KEY` | `https://api.anthropic.com/v1` |
| DeepSeek · V4 Pro | `anatomy.deepseek.example.yaml` | `DEEPSEEK_API_KEY` | `https://api.deepseek.com/v1` |
| Qwen · Qwen3.7 Max | `anatomy.qwen.example.yaml` | `DASHSCOPE_API_KEY` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |
| Moonshot · moonshot-v1-32k | `anatomy.moonshot.example.yaml` | `MOONSHOT_API_KEY` | `https://api.moonshot.cn/v1` |

建议第一次真实运行控制范围：

```powershell
cp anatomy.openai.example.yaml anatomy.config.yaml
cp sources.github.example.yaml sources.yaml
notepad .env
$env:PYTHONPATH='src'
python -m asa plan-run --config anatomy.config.yaml --limit-skills 1
python -m asa run --config anatomy.config.yaml --limit-skills 1
python -m asa quality-run --run runs\<run-id> --output runs\<run-id>\quality_report.json
python -m asa export-letuen --run runs\<run-id> --output dist\letuen-real
```

在 provider 路由、成本、schema 校验和 artifact 质量稳定前，建议保留 `--limit-skills 1`。

## 分析流程

```text
GitHub URL / Local Path
  -> Collector
  -> Structure Analyst
  -> Workflow Analyst
  -> Pattern Miner
  -> Asset Builder
  -> Reviewer
  -> Quality Gates
  -> Report / Vault / Data / Anchors
```

## 本地模型 Bridge

静态 UI 可以调用本地 bridge 来测试模型连接，也可以驱动首页 GitHub URL 拆解入口。

```powershell
$env:PYTHONPATH='src'
python scripts/local_bridge.py
```

然后打开 `http://localhost:4173/settings/models/`。bridge 不持久化 key；CLI 真实运行建议把 key 存在 `.env` 对应环境变量中。

## Skill Anchor Pack

当前开发预览版 method pack 已发布到 GitHub Release，也保留在 `releases/`：

- `releases/letuen-skill-anchor-pack-v0.2.0-dev.zip`
- `releases/letuen-skill-anchor-pack-v0.2.0-dev.tar.gz`
- `releases/SHA256SUMS.txt`

本地重打包：

```powershell
$env:PYTHONPATH='src'
python -m asa package-letuen-skill --output releases --version v0.2.0-dev
```

该包包含一个协调器 `SKILL.md`、9 个 `skills/asa-*` 方法层 skills、anchor schemas、非破坏式调用策略和 sample anchor composition assets。

## 常用命令

```powershell
$env:PYTHONPATH='src'
python -m asa collect --source examples/sample-skill --output runs/manual-collect/inventory.json
python -m asa run --config anatomy.config.example.yaml
python -m asa validate --run runs/<run-id>
python -m asa review-run --run runs/<run-id> --output runs/<run-id>/review_summary.json
python -m asa repair-evidence --run runs/<run-id>
python -m asa quality-run --run runs/<run-id> --output runs/<run-id>/quality_report.json
python -m asa export-report --run runs/<run-id> --output site/report
python -m asa export-vault --run runs/<run-id> --output vault
python -m asa export-data --run runs/<run-id> --output site/data
python -m asa export-anchors --run runs/<run-id> --output dist/anchors.json
python -m asa export-letuen --run runs/<run-id> --output dist/<run-id>
python -m asa smoke-github --sources sources.smoke.github.yaml --output runs/github-smoke
python -m asa package-letuen-skill --output releases --version v0.2.0-dev
```

## GitHub Pages 展示页

仓库内置静态站点在 `site/`。启用 GitHub Pages 且选择 **GitHub Actions** 作为来源后，`Deploy GitHub Pages` workflow 会发布本地 showcase UI。

启用后的预期地址：

```text
https://3yesore.github.io/LetUenforskills/
```

## 仓库结构

```text
src/                  Python harness、providers、exporters、quality gates
site/                 静态 UI：首页、cinema、repo、data/settings surfaces
skills/               LetUen 内置方法层 skills 与 anchor-aware workflow skills
docs/                 设计文档、harness 契约、UI/output strategy
examples/             sample skill、sample vault、anchor composition examples
runs/demo-multi-skill 用于 export/demo scripts 的提交版 demo run
releases/             开发预览版 skill anchor pack archives
tests/                runtime、exporters、quality、packaging 单元测试
```

## 文档地图

- `docs/fork-ready-guide.md`：clone/fork 使用、CI、sample vault workflow。
- `docs/harness-spec.md`：runtime state machine 与 quality gates。
- `docs/agent-protocol.md`：各 agent 责任和边界。
- `docs/evidence-spec.md`：evidence object 契约和 confidence 规则。
- `docs/provider-spec.md`：model provider interface、retry、OpenAI-compatible adapter。
- `docs/letuen-usage-guide.md`：report、vault、data、anchors、composition plans 的端到端命令。
- `docs/letuen-skill-anchor-pack-design.md`：基于 anchor 的 skill 拆解与重组方法包。
- `docs/graph-data-surface-spec.md`：data table、graph nodes/edges、manifest 与 UI 要求。
- `docs/ui-strategy.md`：本地研究 dashboard 与未来公开网站方向。

## 参与贡献

可使用 issue templates 提交可复现 bug 或边界清晰的功能建议。PR 建议按 `.github/pull_request_template.md` 中的验证命令检查。

安全敏感问题请按 `SECURITY.md` 处理，不要直接发公开 issue。

## 发布状态

当前开发预览版：`v0.2.0-dev`。

- CI 已在 `main` 上启用。
- Release asset 是 method skill pack，不是完整 Python harness。
- 完整仓库仍然是 harness + UI + skill pack 的开发源。

## License

MIT。见 `LICENSE`。
