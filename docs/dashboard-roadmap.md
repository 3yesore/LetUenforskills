# Dashboard Roadmap

This roadmap defines UI work after the public landing page. The project should move from static explanation to artifact browsing, then to local research workflows.

## Stage 1: Static Report Browser

Purpose: turn a completed run into a browsable static report.

Input artifacts:

- `runs/<run-id>/inventory.json`
- `runs/<run-id>/skills/*/structure_analysis.json`
- `runs/<run-id>/skills/*/workflow_analysis.json`
- `runs/<run-id>/skills/*/review_report.json`
- `runs/<run-id>/quality_report.json`
- `runs/<run-id>/review_summary.json`
- `runs/<run-id>/patterns/patterns.json`
- `runs/<run-id>/render/render_manifest.json`

Views:

- Run Overview
- Sources
- Skills
- Skill Detail
- Workflow Steps
- Evidence Table
- Quality Issues
- Reviewer Scores
- Patterns

Implemented command:

```powershell
python -m asa export-report --run runs/<run-id> --output site/report
```

Current implementation:

- `asa export-report` generates static HTML with no client-side framework.
- `index.html` provides run overview, skills, quality, review summary, and patterns.
- `skills/<skill-id>.html` provides skill detail, workflow steps, review notes, and artifact links.
- `artifacts/` contains copied canonical JSON artifacts for traceability.
- The report can be served locally or deployed with Cloudflare Pages as static files.

Exit criteria:

- A user can inspect a run without reading raw JSON. ✅
- Every page links back to canonical JSON artifacts. ✅
- Quality failures are visible and not hidden. ✅

## Stage 2: Local Research Dashboard

Purpose: compare runs, models, prompts, and benchmark results locally.

Input directories:

- `runs/`
- `benchmark/results/`
- `models/registry.yaml`
- `vault/`

Views:

- Run Selector
- Run Diff
- Quality Trend
- Provider/Model Comparison
- Benchmark Matrix
- Pattern Coverage
- Evidence Coverage Heatmap
- Reviewer Strictness View

Implementation options:

- Vite + React when interactivity is needed.
- Read local JSON artifacts through a lightweight local server.
- Keep all data local by default.

Possible location:

```text
apps/dashboard/
```

Exit criteria:

- Maintainers can compare two runs in under one minute.
- Prompt/schema changes can be evaluated against prior runs.
- Model regressions are visible from benchmark summaries.

## Stage 3: Interactive Workbench

Purpose: operate the harness from a local UI.

Potential capabilities:

- Edit source configs.
- Run `plan-run`.
- Start or resume analysis.
- Review quality issues.
- Approve or reject artifacts.
- Export Obsidian vault or static report.
- Compare provider routing strategies.

This stage should wait until CLI workflows and artifact schemas stabilize.

## UI Data Contract

The dashboard should not call model providers directly in early versions. It should consume existing artifacts written by CLI commands.

Canonical data sources:

- inventory artifacts for source and skill lists
- analysis artifacts for structure/workflow detail
- quality reports for deterministic issues
- review summaries for LLM reviewer conclusions
- benchmark reports for provider comparison

## Design Constraints

- Artifact-first: JSON remains the source of truth.
- Local-first: no hosted backend required.
- Evidence-visible: claims should show source paths and quotes.
- Quality-visible: failed checks should be prominent.
- Bilingual-ready: UI labels should support Chinese and English.



## Landing And Report Linkage

The landing page and static report should feel like one product surface:

- `site/index.html` links to `site/report/` when a report has been generated.
- `site/report/index.html` links back to the landing page.
- Report styling should reuse the same dark research-tool language, title gradients, bento cards, and artifact-first tone.
- Generated report pages remain static and do not require a frontend build step.


For local linked demos, run:

```powershell
python -m asa export-all --run runs/<run-id> --output site
```

This creates `site/report/` and `site/vault/` so the report can link directly to Obsidian Markdown learning notes while being served from the same local static site.


## Bilingual UI

The landing page and generated report pages include a lightweight language toggle:

- Default language is Chinese.
- The `EN` button switches visible UI copy to English.
- The selected language is stored in `localStorage` under `asa-language`.
- Generated report pages use the same toggle pattern and include `report.js` in `site/report/assets/`.
