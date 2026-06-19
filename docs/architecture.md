# Architecture

Agent Skill Anatomy is organized as a layered pipeline. Each layer owns a narrow responsibility, writes durable artifacts, and passes schema-valid data to the next layer. The current runtime is intentionally small: source collection and JSON validation are deterministic, while model-backed analysis is isolated behind provider adapters.

## Layer Model

```text
Source Layer
  -> Analysis Layer
  -> Quality Layer
  -> Benchmark Layer
  -> Knowledge Layer
```

The layers are logical boundaries, not necessarily separate packages yet. Runtime modules may serve more than one layer during early development, but new work should keep these responsibilities distinct.

## Source Layer

The Source layer acquires and normalizes input material.

- Inputs: GitHub URLs, local paths, source lists, refs, config files, and optional `.env` provider settings.
- Responsibilities: fetch or locate repositories, discover `SKILL.md` packages, collect scripts/references/assets/examples, and record source metadata.
- Current artifacts: `sources.lock.json`, per-source `inventory.json`, aggregate `inventory.json`, and `source_snapshot.json` per skill.
- Current modules: `src/asa/collectors/inventory.py`, `src/asa/config.py`, `src/asa/context.py`, `src/asa/env.py`, `src/asa/paths.py`, `src/asa/jsonio.py`.

This layer should stay deterministic. It should not summarize quality, infer hidden workflows, or execute third-party repository code.

## Analysis Layer

The Analysis layer converts source material into structured, evidence-grounded interpretations.

- Structure Analyst: identifies anatomy, triggers, file layout, tools, context strategy, target agents, and confidence.
- Workflow Analyst: decomposes execution flow, decision points, handoffs, verification steps, and failure modes.
- Pattern Miner: extracts reusable patterns across skills while distinguishing candidates from established patterns.
- Asset Builder: renders structured artifacts into Markdown notes, diagrams, and reusable assets without adding new claims.
- Reviewer: performs semantic review of evidence, inference, coherence, formatting, and publish readiness.

Current modules are `src/asa/agents/*.py`, `src/asa/agent_call.py`, `src/asa/resources.py`, `prompts/`, and `schemas/`. Provider access is routed through `src/asa/providers/base.py`, `src/asa/providers/mock.py`, and `src/asa/providers/openai_provider.py` so the analysis layer remains multi-provider.

## Quality Layer

The Quality layer decides whether artifacts are structurally valid, evidence-grounded, and safe to publish.

- Schema validation checks all persisted JSON against local contracts before reuse or downstream rendering.
- Programmatic quality rules catch deterministic failures such as missing evidence, unverifiable quotes, overconfident inference, and tool/script mismatches.
- LLM review adds semantic judgment but does not replace schema checks or deterministic rules.
- Human calibration reviews selected runs and turns recurring failures into new prompts, schemas, or rules.

Current modules are `src/asa/schemas.py`, `src/asa/validator.py`, `src/asa/quality/rules.py`, `src/asa/quality/report.py`, `src/asa/review_summary.py`, and the review agent. Quality outputs include `review_report.json`, `review_summary.json`, `quality_report.json`, sibling `*.error.json` files, and run state transitions.

## Benchmark Layer

The Benchmark layer is the evaluation workbench for comparing prompts, providers, schemas, and runtime changes. It is partially implemented through data exports, comparison seeds, quality summaries, and provider/model metadata.

- Inputs: golden fixtures, source snapshots, expected properties, provider/model metadata, and run configurations.
- Measures: schema pass rate, evidence coverage, quote verification, workflow completeness, pattern precision, bilingual quality, cost, latency, and reproducibility.
- Outputs: benchmark manifests, per-case scores, provider comparison reports, and calibration notes.

Today, benchmark foundations exist in mock runs, smoke GitHub collection, `plan-run`, schema validation, quality reports, `scripts/compare_runs.py`, `export-data`, and model comparison seed JSONL. The long-term goal is a first-class benchmark lab that can replay the same cases across OpenAI-compatible providers and Chinese model providers.

## Knowledge Layer

The Knowledge layer compiles validated artifacts into durable learning assets.

- Outputs: Obsidian source notes, skill anatomy notes, workflow pattern notes, MOCs, Mermaid diagrams, templates, checklists, and comparison views.
- Principles: generated notes must preserve source paths, confidence, review status, and evidence references; reusable claims must trace back to artifacts.
- Current destinations: `vault/00 Maps/`, `vault/01 Sources/`, `vault/02 Skills/`, `vault/03 Workflows/`, `vault/04 Patterns/`, `vault/05 Quality/`, `vault/06 Data/`, `dist/<run>/report/`, and `dist/<run>/data/`.
- Current modules: render helpers in `src/asa/agents/asset_builder.py` and orchestration in `src/asa/runtime.py`.

Future compiler work should add richer graph interaction, reusable asset packs, and cross-run comparison notes without making the vault the source of truth.

## Current Runtime Flow

```text
asa run
  -> load RuntimeConfig and .env
  -> build provider: mock or openai
  -> lock configured sources
  -> collect per-source inventories
  -> build aggregate inventory
  -> for each selected skill:
       source_snapshot
       structure_analysis
       workflow_analysis
       review_report
       skill note
  -> mine cross-skill patterns
  -> render source notes, pattern notes, and MOCs
  -> write render manifest and run state
```

## Runtime Modules

- `src/asa/cli.py`: command surface for `run`, `resume`, `collect`, `validate`, `review-run`, `quality-run`, `smoke-github`, `plan-run`, `export-report`, `export-vault`, `export-data`, and `export-all`.
- `src/asa/runtime.py`: end-to-end orchestration, run directory creation, state updates, provider construction, and rendering calls.
- `src/asa/state.py`: durable run status and stage tracking.
- `src/asa/planner.py`: collector-only scope and cost planning before real model calls.
- `src/asa/providers/`: provider interface plus mock and OpenAI adapters.
- `src/asa/agents/`: bounded agent stages and current Markdown renderers.
- `src/asa/quality/`: deterministic quality report generation.

## Design Constraints

- Keep source acquisition, model analysis, quality checks, benchmarks, and knowledge rendering independently testable.
- Prefer schemas and evidence contracts over prose-only prompt instructions.
- Treat provider-specific behavior as metadata for comparison, not hidden runtime magic.
- Never require a paid model call for basic onboarding, CI, or open-source contribution.
- Keep generated knowledge reproducible from artifacts so Obsidian remains an output layer, not the canonical database.
