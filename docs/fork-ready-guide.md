# Fork-Ready Guide

This guide describes the target fork/clone workflow for Agent Skill Anatomy.

## Clone and Run Locally

```powershell
git clone <repo-url>
cd agent-skill-anatomy
cp .env.example .env
cp anatomy.config.example.yaml anatomy.config.yaml
cp sources.example.yaml sources.yaml
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.yaml
```

## Validate a Run

```powershell
$env:PYTHONPATH='src'
python -m asa validate --run runs/<run-id>
```

## Review a Run

```powershell
$env:PYTHONPATH='src'
python -m asa review-run --run runs/<run-id> --output runs/<run-id>/review_summary.json
```

The review summary aggregates reviewer statuses, average scores, unsupported claims, missing evidence, over-inference counts, and publish approval state.

## Quality Check a Run

```powershell
$env:PYTHONPATH='src'
python -m asa quality-run --run runs/<run-id> --output runs/<run-id>/quality_report.json
```

This runs deterministic quality rules before or after LLM reviewer inspection.

## Resume a Run

```powershell
$env:PYTHONPATH='src'
python -m asa resume --run runs/<run-id>
```

Resume mode reuses schema-valid artifacts and regenerates missing or invalid stage outputs.

## Use GitHub Sources

```powershell
cp sources.github.example.yaml sources.yaml
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.yaml
```

If GitHub clone fails due to network issues, rerun the same command. The collector cleans partial clone directories before retrying.

The collector first tries a shallow `git clone --filter blob:none`. If clone fails, it falls back to GitHub zip archives such as `https://github.com/<owner>/<repo>/archive/HEAD.zip` or `archive/<ref>.zip`.

Inventory records the source acquisition method as one of:

- `git_clone`
- `github_archive`
- `local`

## GitHub Collector Smoke

Use collector-only smoke checks when you want to verify GitHub URL access without running LLM agents.

```powershell
$env:PYTHONPATH='src'
python -m asa smoke-github --sources sources.smoke.github.yaml --output runs/github-smoke
```

The manual GitHub Actions workflow `.github/workflows/github-smoke.yml` runs the same check and uploads the generated inventories.

## Use Real OpenAI Calls

```powershell
cp anatomy.openai.example.yaml anatomy.config.yaml
notepad .env
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.yaml
```

Set `OPENAI_API_KEY` in `.env` before running the OpenAI provider.

For the first real run, limit analysis to one skill package:

```powershell
$env:PYTHONPATH='src'
python -m asa plan-run --config anatomy.config.yaml --limit-skills 1 --output runs/plan-openai.json
python -m asa run --config anatomy.config.yaml --limit-skills 1
```

This keeps cost and output review manageable.

`plan-run` runs collectors only. It estimates model calls but does not call LLM agents.

## CI

The default CI workflow runs:

- unit tests
- Python compile checks
- mock harness run
- artifact validation for the latest run

The sample vault workflow builds `vault/` and uploads it as a GitHub Actions artifact.
