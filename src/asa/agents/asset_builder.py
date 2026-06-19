from __future__ import annotations

from pathlib import Path

from asa.jsonio import write_text


def render_skill_note(vault_path: Path, package: dict, structure: dict, workflow: dict, review: dict | None = None) -> Path:
    note_path = vault_path / "02 Skills" / f"{package['id']}.md"
    mermaid = workflow.get("mermaid", {}).get("flowchart", "flowchart TD\n  A[No workflow]")
    summary_zh = structure.get("summary", {}).get("zh", "")
    summary_en = structure.get("summary", {}).get("en", "")
    workflow_summary_zh = workflow.get("workflow_summary", {}).get("zh", "")
    workflow_summary_en = workflow.get("workflow_summary", {}).get("en", "")
    review_status = review.get("status") if review else "not_reviewed"
    content = f"""---
type: skill-analysis
source_repo: {structure.get('source', {}).get('repo')}
source_path: {package.get('skill_md_path')}
source_commit: {structure.get('source', {}).get('commit')}
skill_type: {structure.get('skill_type', {}).get('primary')}
target_agents: {structure.get('target_agents', [])}
patterns: []
confidence: {structure.get('confidence', {}).get('overall')}
status: {review_status}
tags:
  - asa/skill
---

# {package['name']}

## Summary 摘要

- ZH: {summary_zh}
- EN: {summary_en}

## Anatomy 结构解剖

- Skill file: `{package.get('skill_md_path')}`
- Root path: `{package.get('root_path')}`
- Scripts: {len(package.get('scripts', []))}
- References: {len(package.get('references', []))}
- Assets: {len(package.get('assets', []))}

## Workflow 工作流拆解

- ZH: {workflow_summary_zh}
- EN: {workflow_summary_en}

## Mermaid Flow 流程图

```mermaid
{mermaid}
```

## Review 审查

- Status: `{review_status}`

## Evidence 原始证据

Mock mode does not include evidence. Real analyst agents must populate evidence fields.
"""
    write_text(note_path, content)
    return note_path


def render_source_note(vault_path: Path, inventory: dict) -> Path:
    source = inventory["source"]
    note_path = vault_path / "01 Sources" / f"{source['name']}.md"
    skill_links = "\n".join(
        f"- [[{package['id']}|{package['name']}]] — `{package['skill_md_path']}`"
        for package in inventory.get("skill_packages", [])
    ) or "- No skill packages found."
    content = f"""---
type: source-repo
source_name: {source.get('name')}
source_type: {source.get('type')}
source_url: {source.get('url')}
source_ref: {source.get('ref')}
source_commit: {source.get('resolved_commit')}
tags:
  - asa/source
---

# {source.get('name')}

## Summary 摘要

- Type: `{source.get('type')}`
- URL: {source.get('url')}
- Commit: `{source.get('resolved_commit')}`
- Files scanned: {inventory.get('repository', {}).get('total_files_scanned')}
- Skill packages: {len(inventory.get('skill_packages', []))}

## Skills 技能包

{skill_links}
"""
    write_text(note_path, content)
    return note_path


def render_pattern_notes(vault_path: Path, patterns: dict) -> list[Path]:
    paths: list[Path] = []
    for pattern in patterns.get("patterns", []):
        note_name = pattern["canonical_name"].replace("/", "-")
        note_path = vault_path / "03 Patterns" / f"{note_name}.md"
        examples = "\n".join(
            f"- [[{example.get('skill_id')}]] — `{example.get('source_path')}`"
            for example in pattern.get("examples", [])
        ) or "- No examples recorded."
        content = f"""---
type: pattern
canonical_name: {pattern.get('canonical_name')}
zh_name: {pattern.get('zh_name')}
category: {pattern.get('category')}
status: {pattern.get('status')}
confidence: {pattern.get('confidence')}
tags:
  - asa/pattern
  - asa/pattern/{pattern.get('category')}
---

# {pattern.get('canonical_name')} {pattern.get('zh_name')}

## Definition 定义

- ZH: {pattern.get('definition', {}).get('zh', '')}
- EN: {pattern.get('definition', {}).get('en', '')}

## Problem 问题

- ZH: {pattern.get('problem', {}).get('zh', '')}
- EN: {pattern.get('problem', {}).get('en', '')}

## Solution 方案

- ZH: {pattern.get('solution', {}).get('zh', '')}
- EN: {pattern.get('solution', {}).get('en', '')}

## When To Use 适用场景

- ZH: {pattern.get('when_to_use', {}).get('zh', '')}
- EN: {pattern.get('when_to_use', {}).get('en', '')}

## Examples 示例

{examples}

## Reusable Template 可复用模板

- ZH: {pattern.get('reusable_template', {}).get('zh', '')}
- EN: {pattern.get('reusable_template', {}).get('en', '')}
"""
        write_text(note_path, content)
        paths.append(note_path)
    return paths


def render_mocs(vault_path: Path, source_inventories: list[dict], packages: list[dict], patterns: dict) -> list[Path]:
    maps_dir = vault_path / "00 Maps"
    source_lines = "\n".join(f"- [[{source['name']}]]" for source in source_inventories) or "- No sources yet."
    skill_lines = "\n".join(f"- [[{package['id']}|{package['name']}]]" for package in packages) or "- No skills yet."
    pattern_lines = "\n".join(
        f"- [[{pattern['canonical_name']}|{pattern['canonical_name']} {pattern['zh_name']}]]"
        for pattern in patterns.get("patterns", [])
    ) or "- No patterns yet."
    files = {
        "Source Repos MOC.md": f"# Source Repos MOC\n\n{source_lines}\n",
        "Skill Anatomy MOC.md": f"# Skill Anatomy MOC\n\n{skill_lines}\n",
        "Workflow Pattern MOC.md": f"# Workflow Pattern MOC\n\n{pattern_lines}\n",
    }
    paths: list[Path] = []
    for name, content in files.items():
        path = maps_dir / name
        write_text(path, content)
        paths.append(path)
    return paths
