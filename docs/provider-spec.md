# Provider Spec

Providers adapt model APIs to the harness. Agents call providers through one method: `generate_json`.

## Interface

```python
provider.generate_json(
    system_prompt=prompt,
    user_payload=payload,
    schema=schema,
    model="gpt-5.2",
    temperature=0,
)
```

## Implemented Providers

- `mock`: deterministic local output for CI, demos, and runtime debugging.
- `openai`: OpenAI Responses API adapter using JSON Schema output.

## Rules

- Providers return parsed JSON, not Markdown.
- Agents validate provider output against local schemas.
- Real providers must not silently repair schema failures; runtime or agents should surface validation errors.
- `.env` is loaded from the config directory before provider initialization.
- Provider prompts should include the evidence contract so model outputs remain auditable.

## Schema Validation Retry

Agent calls use `generate_validated_json` from `src/asa/agent_call.py`.

Flow:

1. Call provider with prompt, payload, model, and JSON Schema.
2. Validate parsed JSON against the local schema.
3. If validation fails, retry once with:
   - `previous_invalid_output`
   - `previous_validation_error`
   - `retry_instruction`
4. Persist the artifact only after validation succeeds.
5. Surface a schema validation error after the final failed attempt.
6. Write a sibling `*.error.json` artifact for the failed output path.

This keeps real model calls resilient without silently accepting malformed artifacts.

## Cost-Control Smoke Runs

Use `--limit-skills 1` for the first real OpenAI run. This executes the full multi-agent flow for a single discovered skill package while preserving the same artifact structure.

Before running real calls, use:

```powershell
python -m asa plan-run --config anatomy.openai.example.yaml --limit-skills 1
```

The planner collects sources and estimates agent calls without invoking model agents.
