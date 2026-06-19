# Roadmap

Agent Skill Anatomy is an open-source research and tooling project for turning agent skills, prompts, and workflow packages into evidence-grounded, reusable knowledge. The primary product is the toolchain plus the research method behind it; tutorials and knowledge publishing are important secondary outputs that prove the method and help adoption.

## Product Direction

- Build a provider-neutral analysis harness that can inspect real skill repositories, preserve evidence, and emit replayable artifacts.
- Treat research calibration as a first-class deliverable: prompts, schemas, quality rules, benchmark fixtures, and evaluation notes should improve together.
- Support multiple model providers, including OpenAI-compatible APIs and Chinese model ecosystems, without binding core logic to any vendor.
- Generate Obsidian-ready, visual, reusable outputs: bilingual notes, MOCs, Mermaid diagrams, pattern libraries, templates, and checklists.
- Keep the project fork-ready and clone-ready for open-source users: sample configs, mock runs, smoke tests, and clear contribution paths.

## Priorities

### Primary: Tooling and Research

The main value is a reproducible system for analyzing agent skills at scale. The harness should make source acquisition, structured analysis, quality gates, benchmark runs, and knowledge compilation reliable enough that contributors can compare changes across prompts, models, and schemas.

### Secondary: Knowledge and Tutorials

The generated vault, tutorials, and design essays should explain what the system learns from real skills. They should remain downstream of verified artifacts rather than becoming hand-written summaries that drift away from evidence.

## Phases

### 1. Foundation

- Stabilize repository structure, CLI entry points, config files, schemas, prompts, and sample data.
- Preserve every run under `runs/<run-id>/` with source locks, resolved config, artifacts, state, and review reports.
- Keep mock provider support strong enough for CI, demos, and offline contributor onboarding.

### 2. Real-Run Calibration

- Run small, real-model analyses with `--limit-skills` and compare outputs against human expectations.
- Tune prompts, schemas, retry behavior, and quality rules based on observed hallucinations, weak evidence, and missing workflow detail.
- Build golden fixtures from representative agent skills so regressions are visible before broader runs.

### 3. Multi-Provider Runtime

- Introduce built-in decomposition meta-skills as a provider-neutral method layer. See `docs/meta-skills-design.md`.
- Generalize provider adapters around schema-valid JSON generation, retry, token/cost metadata, and consistent error reporting.
- Add OpenAI-compatible provider configuration for other hosted APIs and Chinese models such as Qwen, DeepSeek, GLM, Moonshot, and Baichuan where feasible.
- Track provider differences in benchmark metadata instead of hiding them behind one generic score.

### 4. Benchmark Lab

- Create repeatable benchmark suites for source discovery, structure analysis, workflow decomposition, pattern mining, evidence quality, and note render quality.
- Compare prompts, schemas, model providers, context budgets, and language modes on the same fixture set.
- Publish compact benchmark reports that explain tradeoffs, not just leaderboards.

### 5. Knowledge Compiler

- Promote validated run artifacts into a curated Obsidian vault with stable note IDs, backlinks, MOCs, diagrams, reusable templates, and pattern indexes.
- Add higher-level comparison views across providers, source projects, skill types, workflow patterns, and failure modes.
- Keep compiler outputs reproducible from JSON artifacts so the vault can be regenerated and reviewed.

### 6. Open-Source Release

- Prepare contributor docs, issue templates, example runs, sample vaults, and a minimal governance model.
- Clearly separate generated artifacts, cache directories, local secrets, and source-controlled examples.
- Publish a roadmap of good first issues across providers, benchmarks, renderers, quality rules, and knowledge templates.

## Current Operating Defaults

The roadmap now uses these defaults for the next implementation phase:

- First-class provider support requires schema-valid JSON or reliable JSON retry behavior, visible model metadata, configurable base URL/model id, and safe secret handling.
- Publishability is gated by schema validation, deterministic quality checks, evidence coverage, and reviewer status rather than a single model score.
- Generated vault/report/data outputs should be reproducible on demand; only small examples and fixtures should be committed for open-source onboarding.
- The most important reusable visual outputs are the skill anatomy manual, workflow trace, evidence graph, model comparison matrix, and Obsidian pattern notes.

Detailed specs now live in:

- `docs/report-manual-spec.md`
- `docs/llm-skill-integration-design.md`
- `docs/model-comparison-spec.md`
- `docs/graph-data-surface-spec.md`
- `docs/acceptance-checklist.md`
