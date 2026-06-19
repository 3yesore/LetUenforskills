# Obsidian Output Spec

## Vault Layout

```text
vault/
  00 Maps/
    Skill Anatomy MOC.md
    Workflow Pattern MOC.md
    Source Repos MOC.md
  01 Sources/
  02 Skills/
  03 Patterns/
  04 Reusable Assets/
  05 Comparisons/
  99 System/
    inventory/
    analysis-json/
    review-reports/
```

## Skill Note Frontmatter

```yaml
---
type: skill-analysis
source_repo:
source_path:
source_commit:
skill_type:
target_agents: []
patterns: []
confidence: unknown
status: analyzed
tags:
  - asa/skill
---
```

## Bilingual Style

- Use English canonical terms with Chinese explanation in bilingual mode.
- Keep frontmatter keys in English.
- Do not translate repository names, file paths, code identifiers, or commands.
- Prefer section titles like `Summary 摘要` and `Reusable Patterns 可复用模式`.

## Render Manifest

Each run writes `runs/<run-id>/render/render_manifest.json` with note paths and note types.

```json
{
  "generated_notes": [
    { "path": "00 Maps/Skill Anatomy MOC.md", "note_type": "moc" },
    { "path": "02 Skills/example.md", "note_type": "skill" }
  ],
  "generated_note_count": 2,
  "patterns_count": 1,
  "generated_at": "2026-06-07T00:00:00Z"
}
```
