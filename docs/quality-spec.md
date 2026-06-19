# Quality Spec

Agent Skill Anatomy uses layered quality checks. LLM reviewers are useful, but they are not the only source of truth.

## Layers

1. Schema validation: JSON artifacts must match local schemas.
2. Programmatic quality rules: deterministic checks for obvious quality failures.
3. LLM reviewer: semantic review of evidence, inference, workflow coherence, and publishability.
4. Human spot check: calibration against real examples and golden fixtures.

## Current Programmatic Rules

`asa quality-run` currently checks structure and workflow artifacts for:

- `HIGH_CONFIDENCE_WITHOUT_EVIDENCE`
- `INFERRED_HIGH_CONFIDENCE`
- `EVIDENCE_SOURCE_MISSING`
- `EVIDENCE_SOURCE_NOT_FOUND`
- `EVIDENCE_QUOTE_TOO_LONG`
- `EVIDENCE_QUOTE_NOT_FOUND`
- `INFERRED_EVIDENCE_NEEDS_NOTES`
- `TARGET_AGENTS_WITHOUT_EVIDENCE`
- `SCRIPT_TOOL_WITHOUT_SCRIPT_MANIFEST`
- `REQUIRED_TOOL_WITHOUT_EVIDENCE`

## CLI

```powershell
$env:PYTHONPATH='src'
python -m asa quality-run --run runs/<run-id> --output runs/<run-id>/quality_report.json
```

`quality-run` returns exit code `2` when major/blocker issues make the run non-publishable by deterministic rules.

## 中文说明

质量检查不能完全交给 LLM。当前项目采用：schema 校验、程序化规则、LLM reviewer、人工抽样四层质量体系。

程序化规则主要拦截明显问题，例如 high confidence 但没有 evidence、inferred 却 high confidence、source_path 不存在、quote 过长、quote 不存在于源文件、target_agents 缺证据、工具和 scripts manifest 不匹配等。

## Quote Verification

When `source_root` is available, quality checks verify that each evidence `quote` appears in the referenced `source_path`. Matching normalizes whitespace and case, but does not do semantic fuzzy matching.

当 `source_root` 可用时，质量检查会验证 evidence 的 `quote` 是否真的出现在对应 `source_path` 中。匹配会归一化空白和大小写，但不会做语义模糊匹配。
