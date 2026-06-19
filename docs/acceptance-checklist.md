# Project Acceptance Checklist / 项目验收清单

## Purpose

This checklist defines what should be reviewed before handing a build to the user for visual and functional acceptance.

It is intentionally practical: each item should be verifiable from local files, generated output, or the browser.

## Documentation Completion

- README links to the core design documents.
- Architecture, decomposition, output, UI, provider, and benchmark docs agree on artifact names.
- The manual/report spec explains what a user should see first.
- The internal model comparison protocol explains controlled development runs and scoring.
- The LLM skill runtime design explains how internal meta-skills guide model calls.
- The graph/data spec explains export tables, graph nodes, and UI behavior.
- Open questions are either explicitly deferred or converted into working defaults.

## Runtime Readiness

- `asa run` works with mock config without API keys.
- real provider configs do not contain secrets.
- `asa plan-run` can estimate scope before paid calls.
- `asa resume` can regenerate missing/invalid artifacts.
- `asa export-all` emits report, vault, and data directories.
- schema validation and deterministic quality checks run before presentation.

## Report / Repo Surface

- default language is Chinese.
- EN/中 toggle affects titles, descriptions, and navigation copy.
- the report begins as a skill manual, not an abstract project demo.
- navigation buttons are visually aligned with the top bar and do not hide anchors.
- Demo, Repo, Report, Artifacts, Vault/Data/Graph links are clear and non-redundant.
- typography and glass/motion style are consistent across home, cinema, repo, and report.

## Demo Surface

- first run can route to Demo automatically.
- later runs can choose Demo or Repo/Report directly.
- Demo uses real run stages when available.
- final card arrangement has enough size and readable spacing.
- motion is restrained and does not block content comprehension.
- reduced motion mode remains readable.

## Data / Graph / Vault Surface

- `data_manifest.json` reflects exported files and row counts.
- graph UI uses real `graph-data.json` when available.
- Obsidian notes expose method layer, workflow trace, evidence audit, and reuse assets.
- data rows preserve run id, skill id, confidence, and evidence references.
- report/vault/data/graph can be regenerated from the same run artifacts.

## Multi-Model Readiness

- provider/model/base URL presets are editable.
- temporary key testing does not persist secrets.
- model route used for a run is visible in metadata and report.
- comparison only uses runs with the same source/evidence bundle.
- disagreement cases preserve evidence status and severity.

## Validation Commands

Run before claiming a handoff is ready:

```powershell
$env:PYTHONPATH='src'
python -m compileall src scripts -q
python -m unittest discover -s tests
node --check site/script.js
python -m asa export-all --run runs/20260613T183941Z --output dist/deepseek-v4-pro-manual
```

Optional documentation scan: search `docs/` and `README.md` for stale planning markers, placeholder wording, or unresolved open-question headings before handoff.

## Handoff Notes

When handing off to the user, include:

- changed document list
- validation commands and results
- generated output path
- known remaining product work
- whether any real model call was executed

Never include API keys in handoff text, logs, configs, or generated artifacts.


