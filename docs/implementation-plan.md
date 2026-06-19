# Implementation Plan

This plan turns the design discussion into a fork-ready multi-agent skill analysis harness.

## Phase 1: Foundation

- Create project-level documentation in `README.md` and `docs/`.
- Define artifact schemas in `schemas/`.
- Add `anatomy.config.example.yaml`, `sources.example.yaml`, and `.env.example`.
- Add a non-LLM collector script at `scripts/collect_inventory.py`.
- Add initial prompts under `prompts/` for future LLM stages.

## Phase 2: Harness Runtime

- Implement config loading from `anatomy.config.yaml`.
- Implement provider-neutral model call abstraction under `src/providers/`.
- Implement per-agent runners under `src/agents/`.
- Persist every run under `runs/<run-id>/`.
- Validate each artifact against JSON Schema before moving to the next stage.

## Phase 3: Obsidian Renderer

- Render source notes, skill notes, pattern notes, comparison notes, and MOCs.
- Support `zh`, `en`, and `bilingual` language modes.
- Preserve evidence, confidence, and inferred flags in generated notes.
- Generate Mermaid flowcharts from `workflow_analysis.json`.

## Phase 4: Fork-Ready Operation

- Add a single `asa run` command.
- Add GitHub Actions for scheduled source updates.
- Add sample vault output from real public repositories.
- Add contribution docs for new sources, patterns, schemas, and templates.

## Initial Verification Commands

```powershell
python scripts/collect_inventory.py --source . --output runs/local/inventory.json
python -m json.tool runs/local/inventory.json > $null
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.example.yaml
python -m asa validate --run runs/<run-id>
python -m asa smoke-github --sources sources.smoke.github.yaml --output runs/github-smoke
```
