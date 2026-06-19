# Evidence Spec

Evidence makes Agent Skill Anatomy outputs auditable. Analysts should ground claims in source paths and short excerpts whenever possible.

## Evidence Object

```json
{
  "source_path": "examples/sample-skill/SKILL.md",
  "quote": "Load only the files needed",
  "line_start": 12,
  "line_end": 12,
  "evidence_type": "explicit",
  "notes": null
}
```

## Evidence Types

- `explicit`: The source text directly states the claim.
- `structural`: The claim comes from file layout, filenames, or manifests.
- `inferred`: The claim is a reasonable inference and must not be high confidence.

## Rules

- Keep quotes short, ideally under 25 words.
- Do not fabricate quotes. Use an empty evidence array and lower confidence when evidence is missing.
- Do not use long copied source passages as evidence.
- Inferred workflow steps should use `inferred: true` and `confidence: low|medium`.
- Reviewer should flag high-confidence claims that lack evidence.

## 中文说明

Evidence 是为了让每个分析结论可审计、可回溯。模型可以推断，但必须标记推断来源、置信度和证据强弱。

- `explicit`：原文直接支持。
- `structural`：文件结构、目录、manifest 支持。
- `inferred`：模型推断，不能给 high confidence。

