# Agent Protocol

Each agent receives a bounded task and returns a schema-valid artifact. Agents may not silently expand their role.

## Common Call Envelope

```yaml
agent_call:
  run_id:
  agent_name:
  agent_version:
  task_id:
  input_refs: []
  input_payload: {}
  constraints: {}
  output_schema:
  language: bilingual
  timestamp:
```

## Common Result Envelope

```yaml
agent_result:
  run_id:
  agent_name:
  agent_version:
  task_id:
  status: success | partial | failed
  output: {}
  evidence: []
  warnings: []
  errors: []
  confidence: high | medium | low | unknown
  token_usage: {}
  created_at:
```

## Agents

### Collector

- Responsibility: discover repositories, skill packages, `SKILL.md`, scripts, references, assets, examples, README, and license files.
- Output: `inventory.json`.
- Must not: summarize quality, infer workflow, execute repository scripts.

### Structure Analyst

- Responsibility: analyze package structure, frontmatter, trigger wording, file anatomy, context strategy, and tool boundaries.
- Output: `structure_analysis.json`.
- Must not: write final notes or mine cross-skill patterns.

### Workflow Analyst

- Responsibility: decompose execution steps, decision points, verification points, failure modes, context loading, and model/script/tool responsibilities.
- Output: `workflow_analysis.json`.
- Must not: invent workflow steps without `inferred: true` and confidence.

### Pattern Miner

- Responsibility: compare multiple skills and extract reusable patterns.
- Output: `patterns.json`.
- Must not: mark a pattern as established from a single example.

### Asset Builder

- Responsibility: render JSON artifacts into Obsidian notes, Mermaid diagrams, templates, and checklists.
- Output: Markdown files and `render_manifest.json`.
- Must not: introduce new facts or raise confidence levels.

### Translator

- Responsibility: enforce `zh`, `en`, or `bilingual` style using the project glossary.
- Output: translated or bilingual notes.
- Must not: translate paths, code symbols, repo names, or evidence semantics.

### Reviewer

- Responsibility: check evidence, schema validity, over-inference, bilingual quality, Obsidian formatting, and publishability.
- Output: `review_report.json`.
- Must not: add new factual claims without marking them as reviewer notes.

