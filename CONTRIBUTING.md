# Contributing

Agent Skill Anatomy is schema-first and evidence-first. Contributions should preserve those two constraints.

## Development Setup

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
python -m compileall src scripts -q
python -m asa run --config anatomy.config.example.yaml
```

## Adding a Schema Field

- Update the relevant `schemas/*.json` file.
- Update prompts if the field should be produced by a model.
- Update mock provider output if the field is required.
- Add or update `examples/schema-valid/*`.
- Run `python -m asa validate --run runs/<run-id>` after a mock run.

## Adding an Agent

- Add a prompt under `prompts/`.
- Add a runner under `src/asa/agents/`.
- Use `generate_or_reuse_validated_json` for provider calls.
- Persist artifacts only after schema validation.
- Add tests for retry, resume, or rendering behavior when possible.

## Evidence Rules

- Use short quotes only.
- Attach `source_path` whenever possible.
- Mark inferred claims explicitly.
- Do not use high confidence for unsupported inferences.

See `docs/evidence-spec.md` for details.

