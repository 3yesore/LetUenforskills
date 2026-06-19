# UI Strategy

Agent Skill Anatomy should expose its research outputs through progressive UI layers. The UI should not replace the CLI or artifacts; it should make verified artifacts easier to understand, compare, and share.

## Goals

- Explain the project clearly to new users and contributors.
- Show evidence-grounded analysis outputs without requiring users to inspect raw JSON first.
- Make runs, quality reports, review reports, pattern notes, and benchmark results easier to browse.
- Preserve reproducibility: every UI view should link back to source artifacts.
- Support open-source adoption through a public landing page and sample outputs.

## Non-Goals

- Do not build a complex hosted SaaS first.
- Do not require a backend for the first public website.
- Do not make the UI the source of truth; JSON artifacts remain canonical.
- Do not hide quality warnings to make outputs look better.

## UI Layers

```text
Layer 1: Public Landing Page
Layer 2: Static Report Browser
Layer 3: Local Research Dashboard
Layer 4: Future Interactive Workbench
```

## Layer 1: Public Landing Page

Purpose: explain the project and drive users to GitHub, docs, and sample outputs.

Audience:

- AI agent tool builders
- skill authors
- researchers
- open-source contributors
- users who want to learn skill/workflow design

Recommended implementation:

- Static HTML/CSS in `site/` for the first version.
- Deploy with Cloudflare Pages using the free `*.pages.dev` domain.
- Avoid build dependencies until the content direction stabilizes.

Core sections:

1. Hero
   - Project name.
   - One-line value proposition.
   - Links to GitHub, docs, sample vault, and quick start.
2. Problem
   - Agent skills are hard to compare, audit, and learn from.
3. Solution
   - Multi-agent analysis harness.
   - Schema-first artifacts.
   - Evidence-grounded quality checks.
4. Pipeline
   - Collector -> Structure Analyst -> Workflow Analyst -> Pattern Miner -> Reviewer -> Knowledge Outputs.
5. Quality System
   - Schema validation.
   - Evidence verification.
   - Programmatic rules.
   - LLM reviewer.
   - Human calibration.
6. Outputs
   - Obsidian vault.
   - Mermaid diagrams.
   - Pattern library.
   - Review reports.
   - Benchmark reports.
7. CLI Demo
   - `asa plan-run`
   - `asa run`
   - `asa validate`
   - `asa quality-run`
   - `asa review-run`
8. Roadmap
   - Real-run calibration.
   - Multi-provider support.
   - Benchmark lab.
   - Knowledge compiler.
   - Web dashboard.

Success criteria:

- A new visitor understands the project in under one minute.
- A developer can find the quick start in one click.
- A researcher can find benchmark and quality docs quickly.
- The page can be deployed without API keys or build services.

## Layer 2: Static Report Browser

Purpose: browse generated artifacts as a static website.

Inputs:

- `runs/<run-id>/inventory.json`
- `runs/<run-id>/render/render_manifest.json`
- `runs/<run-id>/review_summary.json`
- `runs/<run-id>/quality_report.json`
- `runs/<run-id>/patterns/patterns.json`

Views:

- Run overview
- Source list
- Skill list
- Skill detail
- Workflow graph
- Evidence table
- Quality issue table
- Reviewer score table
- Pattern list

Recommended implementation:

- Generate static HTML from run artifacts.
- Keep it deployable to Cloudflare Pages.
- Add links from every UI view back to JSON artifact paths.

Possible command:

```powershell
python -m asa export-report --run runs/<run-id> --output site/report
```

Success criteria:

- Users can inspect a run without opening raw JSON manually.
- Quality issues remain visible and searchable.
- Static report can be shared as an artifact or hosted page.

## Layer 3: Local Research Dashboard

Purpose: help project maintainers compare runs, providers, prompts, and benchmark results.

Audience:

- maintainers
- researchers
- prompt/schema designers
- provider evaluators

Views:

- Run selector
- Artifact diff
- Quality trend
- Reviewer status trend
- Provider/model calibration for development only
- Benchmark matrix
- Pattern coverage map
- Evidence coverage heatmap

Recommended implementation:

- Start as a local-only app.
- Use static JSON files from `runs/`, `benchmark/results/`, and `vault/`.
- Consider Vite + React when interactivity becomes necessary.

Possible location:

```text
apps/dashboard/
```

Success criteria:

- Maintainers can compare two runs quickly.
- Provider/model regressions are visible.
- Prompt/schema changes can be evaluated against benchmark fixtures.

## Layer 4: Future Interactive Workbench

Purpose: provide an end-to-end local UI for running analysis, reviewing artifacts, editing notes, and exporting outputs.

Potential features:

- Configure sources.
- Select provider/model routing.
- Run `plan-run`, `run`, `resume`, `quality-run`, and `review-run` from UI.
- Approve or reject artifacts.
- Edit generated notes before publishing.
- Export Obsidian vault or static website.

This layer should come after CLI, report browser, and benchmark workflows stabilize.

## Design Principles

- Evidence-first: show claims with source paths and quotes.
- Quality-visible: do not hide warnings or reviewer failures.
- Artifact-linked: every UI card should link to canonical JSON.
- Static-first: prefer static pages until dynamic behavior is justified.
- Bilingual-ready: support Chinese and English labels from the start.
- Reusable-output-oriented: UI should expose templates, checklists, and pattern assets.

## Recommended Next UI Step

Build `site/` as a static public landing page, then deploy it to Cloudflare Pages with the free `*.pages.dev` domain. The first version should be content-first and dependency-free.

