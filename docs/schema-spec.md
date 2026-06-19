# Schema Spec

The harness uses JSON artifacts as contracts between agents. Markdown is rendered from artifacts, not generated directly as the source of truth.

## Artifact Types

- `inventory.json`: source and skill package discovery.
- `structure_analysis.json`: structural anatomy of one skill package.
- `workflow_analysis.json`: execution workflow for one skill package.
- `patterns.json`: reusable pattern candidates and established patterns.
- `review_report.json`: quality gate output.

## Evidence Fields

Evidence should use short excerpts and precise source paths.

```yaml
evidence:
  - source_path: skills/pdf/SKILL.md
    quote: short excerpt only
    line_start: 12
    line_end: 14
    evidence_type: explicit | inferred | structural
```

See `docs/evidence-spec.md` for the canonical evidence rules and `examples/schema-valid/evidence.json` for a minimal example.

## Confidence Values

- `high`: explicitly supported by source text or direct file structure.
- `medium`: reasonably inferred from nearby context.
- `low`: plausible but weakly supported; must be marked inferred.
- `unknown`: not enough information.
