from __future__ import annotations

import json
import re
import shutil
import zipfile
from pathlib import Path
from typing import Any

from .jsonio import read_json, write_json, write_text
from .quality.report import quality_report_for_run
from .review_summary import summarize_run_reviews


LEGACY_VAULT_DIRS = ["03 Patterns"]

VAULT_DIRS = [
    "00 Maps",
    "01 Sources",
    "02 Skills",
    "03 Workflows",
    "04 Patterns",
    "05 Quality",
    "06 Data",
    "07 Anchors",
    "_templates",
]


def export_vault(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    output_dir = output_dir.resolve()
    _prepare_vault_dirs(output_dir)

    inventory = _read_optional_json(run_dir / "inventory.json", {})
    quality = _read_optional_json(run_dir / "quality_report.json", None) or quality_report_for_run(run_dir)
    review_summary = _read_optional_json(run_dir / "review_summary.json", None) or summarize_run_reviews(run_dir)
    patterns = _read_optional_json(run_dir / "patterns" / "patterns.json", {"patterns": []})
    anchors_doc = _read_optional_json(output_dir.parent / "anchors" / "anchors.json", {"anchors": []})
    composition_plan = _read_optional_json(output_dir.parent / "anchors" / "composition_plan.json", {})
    skills = _collect_skills(run_dir, inventory, quality, review_summary)
    for skill in skills:
        skill["patterns"] = patterns

    written: list[Path] = []
    written.extend(_write_maps(output_dir, run_dir, skills, patterns, quality, review_summary))
    written.extend(_write_vault_indexes(output_dir, run_dir, skills, patterns, quality, review_summary, anchors_doc, composition_plan))
    written.append(_write_obsidian_canvas(output_dir, run_dir, skills, patterns, quality))
    written.extend(_write_sources(output_dir, inventory, skills))
    for skill in skills:
        written.append(_write_skill_note(output_dir, run_dir, skill))
        written.append(_write_workflow_note(output_dir, run_dir, skill))
    written.extend(_write_pattern_notes(output_dir, patterns))
    written.extend(_write_anchor_notes(output_dir, anchors_doc, composition_plan))
    written.append(_write_quality_note(output_dir, quality))
    written.append(_write_review_note(output_dir, review_summary))
    written.append(_write_model_compare_seed(output_dir, run_dir, skills, patterns, quality, review_summary))
    written.append(_write_templates(output_dir))
    written.extend(_write_obsidian_app_config(output_dir))
    written.extend(_write_obsidian_launch_files(output_dir, run_dir))
    zip_path = _write_vault_zip(output_dir, run_dir)
    written.append(zip_path)

    manifest = {
        "schema_version": 1,
        "run_dir": str(run_dir),
        "output_dir": str(output_dir),
        "skill_count": len(skills),
        "pattern_count": len(patterns.get("patterns", [])),
        "anchor_count": len(anchors_doc.get("anchors", []) if isinstance(anchors_doc, dict) else []),
        "notes": [path.relative_to(output_dir).as_posix() for path in written],
        "entry_note": "00 Maps/Agent Skill Anatomy MOC.md",
        "open_html": "Open in Obsidian.html",
        "open_url": "Open Agent Skill Anatomy Vault.url",
        "download_zip": f"Agent-Skill-Anatomy-Vault-{run_dir.name}.zip",
    }
    write_json(output_dir / "06 Data" / "vault_manifest.json", manifest)
    return manifest




def _write_obsidian_app_config(output_dir: Path) -> list[Path]:
    config_dir = output_dir / ".obsidian"
    config_dir.mkdir(parents=True, exist_ok=True)
    app_json = config_dir / "app.json"
    appearance_json = config_dir / "appearance.json"
    core_plugins_json = config_dir / "core-plugins.json"
    graph_json = config_dir / "graph.json"
    write_json(app_json, {"showLineNumber": True, "readableLineLength": False, "newFileLocation": "folder", "newFileFolderPath": "06 Data"})
    write_json(appearance_json, {"theme": "obsidian", "accentColor": "#e8ff7a", "cssTheme": ""})
    write_json(core_plugins_json, ["file-explorer", "global-search", "graph", "backlink", "canvas", "outgoing-link", "tag-pane", "page-preview", "templates"])
    write_json(graph_json, {"collapse-filter": False, "search": "", "showTags": True, "showAttachments": True, "hideUnresolved": False, "showOrphans": True})
    return [app_json, appearance_json, core_plugins_json, graph_json]

def _write_obsidian_launch_files(output_dir: Path, run_dir: Path) -> list[Path]:
    entry_note = "00 Maps/Agent Skill Anatomy MOC.md"
    entry_path = (output_dir / entry_note).resolve()
    vault_path = output_dir.resolve()
    zip_name = f"Agent-Skill-Anatomy-Vault-{run_dir.name}.zip"
    entry_uri = f"obsidian://open?path={_uri_component(str(entry_path))}"
    vault_uri = f"obsidian://open?path={_uri_component(str(vault_path))}"
    open_html = output_dir / "Open in Obsidian.html"
    open_url = output_dir / "Open Agent Skill Anatomy Vault.url"
    readme = output_dir / "README - Open in Obsidian.md"
    entry_path_json = json.dumps(str(entry_path), ensure_ascii=False)
    vault_path_json = json.dumps(str(vault_path), ensure_ascii=False)
    html = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Agent Skill Anatomy Vault</title>
  <style>
    :root {{ color-scheme: dark; font-family: Inter, "Microsoft YaHei", system-ui, sans-serif; background: #080b0c; color: #f3efe4; }}
    body {{ min-height: 100vh; margin: 0; display: grid; place-items: center; background: radial-gradient(circle at 20% 0%, rgba(232,255,122,.16), transparent 32rem), radial-gradient(circle at 86% 16%, rgba(124,230,211,.16), transparent 30rem), #080b0c; }}
    main {{ width: min(880px, calc(100vw - 32px)); padding: 34px; border: 1px solid rgba(244,239,228,.14); border-radius: 28px; background: linear-gradient(145deg, rgba(244,239,228,.08), rgba(244,239,228,.025)); box-shadow: 0 40px 120px rgba(0,0,0,.45); }}
    p {{ color: rgba(244,239,228,.68); line-height: 1.72; }}
    a, button {{ display: inline-flex; margin: 12px 10px 0 0; padding: 12px 16px; border: 1px solid rgba(232,255,122,.24); border-radius: 999px; color: #e8ff7a; background: rgba(232,255,122,.055); text-decoration: none; font-weight: 760; cursor: pointer; }}
    a.primary {{ color: #10130d; background: #e8ff7a; }}
    code {{ color: #7ce6d3; }}
    .cards {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12px; margin: 22px 0; }}
    .card {{ padding: 16px; border: 1px solid rgba(244,239,228,.12); border-radius: 18px; background: rgba(0,0,0,.18); }}
    .card strong {{ display: block; margin-bottom: 8px; }}
    .status {{ margin-top: 16px; color: rgba(124,230,211,.82); font-size: .92rem; }}
    @media (max-width: 760px) {{ .cards {{ grid-template-columns: 1fr; }} }}
  </style>
</head>
<body>
  <main>
    <p>Agent Skill Anatomy / Obsidian Vault</p>
    <h1>下载或打开 Obsidian 学习库</h1>
    <p>这里是一份完整 Markdown vault：包含 MOC、Skill 笔记、Workflow、质量索引、Canvas和数据 manifest。普通用户下载 zip 即可使用；本地开发模式可一键注册并跳转到 Obsidian。</p>
    <div class="cards">
      <div class="card"><strong>1 所有人可用</strong><p>下载 ZIP 后解压，用 Obsidian 选择 <code>Open folder as vault</code>。</p></div>
      <div class="card"><strong>2 直接跳转 Obsidian</strong><p>本地 bridge 会先注册 vault，再跳转到 MOC 笔记。</p></div>
      <div class="card"><strong>3 自带关系图谱</strong><p>打开 Obsidian 后使用内置 Graph View 查看 Skill、Workflow、Evidence 的链接关系。</p></div>
    </div>
    <a class="primary" href="{zip_name}" download>Download Vault ZIP</a>
    <button type="button" data-open-bridge="obsidian">Open in Obsidian</button>
    <button type="button" data-open-bridge="folder">Open Local Folder</button>
    <a href="00%20Maps/Agent%20Skill%20Anatomy%20MOC.md">Read MOC Markdown</a>
    <a href="{vault_uri}">Fallback Vault URI</a>
    <a href="{entry_uri}">Fallback MOC URI</a>
    <p class="status" data-status>Ready. Click Open in Obsidian to register this vault and jump to the MOC note.</p>
  </main>
  <script>
    const entryPath = {entry_path_json};
    const vaultPath = {vault_path_json};
    const statusEl = document.querySelector('[data-status]');
    async function openViaBridge(path, mode = 'folder') {{
      try {{
        const response = await fetch('http://127.0.0.1:8765/api/obsidian/open', {{
          method: 'POST',
          headers: {{ 'Content-Type': 'application/json' }},
          body: JSON.stringify({{ path, mode }})
        }});
        const result = await response.json().catch(() => ({{}}));
        if (!response.ok || result.ok === false) throw new Error(result.message || `HTTP ${{response.status}}`);
        if (statusEl) statusEl.textContent = result.message || 'Open request sent to Obsidian.';
        return true;
      }} catch (error) {{
        if (statusEl) statusEl.textContent = `Local bridge unavailable: ${{error.message}}. Download the zip or open the folder manually.`;
        return false;
      }}
    }}
    document.querySelector('[data-open-bridge="obsidian"]')?.addEventListener('click', () => openViaBridge(vaultPath, 'obsidian'));
    document.querySelector('[data-open-bridge="folder"]')?.addEventListener('click', () => openViaBridge(vaultPath, 'folder'));
  </script>
</body>
</html>
"""
    readme_text = f"""---
type: asa-vault-readme
run_id: {run_dir.name}
tags:
  - asa/vault
---

# Open Agent Skill Anatomy Vault

This folder is a complete Obsidian-ready vault generated from run `{run_dir.name}`.

## Recommended Entry

- [[00 Maps/Agent Skill Anatomy MOC]]
- [[00 Maps/Skill Anatomy Canvas.canvas]]

## Best User Flow

1. Download `Agent-Skill-Anatomy-Vault-{run_dir.name}.zip`.
2. Extract it.
3. In Obsidian, choose **Open folder as vault**.
4. Start from [[00 Maps/Agent Skill Anatomy MOC]].

## Local Developer Shortcut

If your system supports Obsidian URI links, use:

```text
{vault_uri}
```

To open the MOC file directly after the folder is registered as a vault, use:

```text
{entry_uri}
```

Windows users can also double-click `Open Agent Skill Anatomy Vault.url`.
"""
    write_text(open_html, html)
    write_text(open_url, "[InternetShortcut]\n" + f"URL={vault_uri}" + "\n")
    write_text(readme, readme_text)
    return [open_html, open_url, readme]


def _write_vault_zip(output_dir: Path, run_dir: Path) -> Path:
    zip_path = output_dir / f"Agent-Skill-Anatomy-Vault-{run_dir.name}.zip"
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(output_dir.rglob("*")):
            if path == zip_path or not path.is_file() or _skip_vault_zip_file(path, output_dir):
                continue
            archive.write(path, path.relative_to(output_dir.parent))
    return zip_path
def _skip_vault_zip_file(path: Path, output_dir: Path) -> bool:
    try:
        relative = path.relative_to(output_dir).as_posix()
    except ValueError:
        return False
    blocked = {
        ".obsidian/workspace.json",
        ".obsidian/workspace-mobile.json",
        ".obsidian/hotkeys.json",
    }
    return relative in blocked or relative.startswith(".obsidian/plugins/") or relative.startswith(".trash/")

def _uri_component(value: str) -> str:
    from urllib.parse import quote
    return quote(value.replace("\\", "/"), safe="")


def _prepare_vault_dirs(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for directory in [*VAULT_DIRS, *LEGACY_VAULT_DIRS]:
        path = output_dir / directory
        if path.exists():
            shutil.rmtree(path)
    for directory in VAULT_DIRS:
        (output_dir / directory).mkdir(parents=True, exist_ok=True)


def _collect_skills(run_dir: Path, inventory: dict[str, Any], quality: dict[str, Any], review_summary: dict[str, Any]) -> list[dict[str, Any]]:
    packages = {item.get("id"): item for item in inventory.get("skill_packages", [])}
    review_by_skill = {item.get("skill_id"): item for item in review_summary.get("skills", [])}
    quality_counts = {item.get("skill_id"): item.get("issue_count", 0) for item in quality.get("skills", [])}
    skills_dir = run_dir / "skills"
    skills: list[dict[str, Any]] = []
    for skill_dir in sorted(path for path in skills_dir.glob("*") if path.is_dir()) if skills_dir.exists() else []:
        skill_id = skill_dir.name
        package = packages.get(skill_id, {})
        structure = _read_optional_json(skill_dir / "structure_analysis.json", {})
        workflow = _read_optional_json(skill_dir / "workflow_analysis.json", {})
        review = _read_optional_json(skill_dir / "review_report.json", {})
        skills.append(
            {
                "id": skill_id,
                "name": package.get("name") or structure.get("skill_id") or skill_id,
                "package": package,
                "structure": structure,
                "workflow": workflow,
                "review": review,
                "review_summary": review_by_skill.get(skill_id, {}),
                "quality_issue_count": quality_counts.get(skill_id, 0),
                "artifact_dir": str(skill_dir.relative_to(run_dir)),
            }
        )
    return skills


def _write_maps(output_dir: Path, run_dir: Path, skills: list[dict[str, Any]], patterns: dict[str, Any], quality: dict[str, Any], review_summary: dict[str, Any]) -> list[Path]:
    skills_list = "\n".join(f"- [[{_skill_note_name(skill)}|{skill['name']}]] — [[{_workflow_note_name(skill)}|workflow]]" for skill in skills) or "- No skills exported."
    patterns_list = "\n".join(f"- [[{_pattern_note_name(pattern)}|{pattern.get('canonical_name') or pattern.get('id')}]]" for pattern in patterns.get("patterns", [])) or "- No patterns exported."
    quality_state = "publishable" if quality.get("publishable_by_rules") else "needs-review"
    moc = output_dir / "00 Maps" / "Agent Skill Anatomy MOC.md"
    content = f"""---
type: asa-map
run_id: {run_dir.name}
tags:
  - asa/map
---

# Agent Skill Anatomy MOC

## Run Overview

- Run: `{run_dir}`
- Skills: {len(skills)}
- Patterns: {len(patterns.get('patterns', []))}
- Quality issues: {quality.get('issue_count', 0)}
- Rule gate: `{quality_state}`
- Reviewed skills: {review_summary.get('reviewed_skill_count', 0)}

## Start Here

- [[Skill Anatomy Canvas.canvas|Skill Anatomy Canvas]] — Obsidian Canvas 空间版
- [[Skill Index]]
- [[Workflow Index]]
- [[Pattern Index]]
- [[Evidence And Quality Index]]
- [[Reuse Asset Index]]
- [[Anchor Index]]
- [[Knowledge Graph]]
- [[Skill Anatomy Canvas.canvas|Skill Anatomy Canvas]]
- [[README - Open in Obsidian|Open in Obsidian]]

## Learning Path

1. Open [[Skill Index]] and choose one skill.
2. Read the skill note for identity, trigger, boundary, resources, and outputs.
3. Open the paired workflow note to understand how the skill actually runs.
4. Use [[Evidence And Quality Index]] to verify which claims are grounded.

## Reuse Path

1. Start from [[Reuse Asset Index]] or [[Anchor Index]].
2. Follow each candidate back to its source skill and workflow.
3. Copy only the anchor, checklist, or pattern that still fits your target harness.

## Review Path

1. Use [[Quality Report]] for deterministic issues.
2. Use [[Review Summary]] for model reviewer concerns.
3. Use [[Knowledge Graph]] when relationships are easier to inspect visually.

## Everyone Can Use This

- **普通用户**：下载 ZIP，解压后在 Obsidian 中选择 `Open folder as vault`。
- **本地增强**：如果本地 bridge 正在运行，`Open in Obsidian` 会注册 vault 并直接跳到 MOC。
- **无 Obsidian**：直接阅读 Markdown、Canvas JSON 和 `06 Data` 数据文件。

## Skills

{skills_list}

## Patterns

{patterns_list}

## Quality And Review

- [[Quality Report]]
- [[Review Summary]]

## Data

- [[vault_manifest.json]]
"""
    write_text(moc, content)
    return [moc]




def _write_vault_indexes(output_dir: Path, run_dir: Path, skills: list[dict[str, Any]], patterns: dict[str, Any], quality: dict[str, Any], review_summary: dict[str, Any], anchors_doc: dict[str, Any], composition_plan: dict[str, Any]) -> list[Path]:
    skill_rows = "\n".join(_skill_index_row(skill) for skill in skills) or "- No skills exported."
    workflow_rows = "\n".join(f"- [[{_workflow_note_name(skill)}|{skill['name']} workflow]] ← [[{_skill_note_name(skill)}|skill]]" for skill in skills) or "- No workflows exported."
    pattern_rows = "\n".join(f"- [[{_pattern_note_name(pattern)}|{pattern.get('canonical_name') or pattern.get('id')}]] — `{pattern.get('category', 'pattern')}`" for pattern in patterns.get("patterns", [])) or "- No patterns exported."
    reuse_rows = "\n".join(_reuse_index_rows(skill) for skill in skills) or "- No reuse assets extracted yet."
    anchors = anchors_doc.get("anchors", []) if isinstance(anchors_doc, dict) else []
    anchor_rows = "\n".join(_anchor_index_row(anchor) for anchor in anchors if isinstance(anchor, dict)) or "- No anchors exported yet."
    composition_line = _composition_index_line(composition_plan)
    graph_edges = "\n".join(_knowledge_graph_edges(skill) for skill in skills) or "  MOC[Agent Skill Anatomy MOC]"
    files = {
        "Skill Index.md": f"""---
type: asa-index
run_id: {run_dir.name}
tags:
  - asa/index
  - asa/skill
---

# Skill Index

## How To Read

1. Open the skill note first to understand identity, triggers, boundaries, and outputs.
2. Follow its workflow link to inspect the action path and resources.
3. Return to Evidence And Quality Index before reusing an anchor or pattern.

{skill_rows}
""",
        "Workflow Index.md": f"""---
type: asa-index
run_id: {run_dir.name}
tags:
  - asa/index
  - asa/workflow
---

# Workflow Index

## How To Read

- Start from the skill note, then use workflow notes to inspect step order, required resources, and fallback risks.
- Treat workflow notes as the bridge between a readable report and a reusable implementation plan.

{workflow_rows}
""",
        "Pattern Index.md": f"""---
type: asa-index
run_id: {run_dir.name}
tags:
  - asa/index
  - asa/pattern
---

# Pattern Index

{pattern_rows}
""",
        "Evidence And Quality Index.md": f"""---
type: asa-index
run_id: {run_dir.name}
tags:
  - asa/index
  - asa/evidence
  - asa/quality
---

# Evidence And Quality Index

- [[Quality Report]]
- [[Review Summary]]
- Rule gate: `{'publishable' if quality.get('publishable_by_rules') else 'needs-review'}`
- Deterministic issues: {quality.get('issue_count', 0)}
- Reviewed skills: {review_summary.get('reviewed_skill_count', 0)}

## Skill Quality

{skill_rows}
""",
        "Reuse Asset Index.md": f"""---
type: asa-index
run_id: {run_dir.name}
tags:
  - asa/index
  - asa/reuse
---

# Reuse Asset Index

## Reuse Path

1. Pick a reuse candidate.
2. Check the original skill note and workflow note.
3. Verify evidence and boundary notes before copying it into another workflow.

{reuse_rows}
""",
        "Anchor Index.md": f"""---
type: asa-index
run_id: {run_dir.name}
tags:
  - asa/index
  - asa/anchor
---

# Anchor Index

{anchor_rows}

## Composition Plan

{composition_line}
""",        "Knowledge Graph.md": f"""---
type: asa-map
run_id: {run_dir.name}
tags:
  - asa/map
  - asa/graph
---

# Knowledge Graph

```mermaid
flowchart LR
{graph_edges}
```

## Navigation

- [[Agent Skill Anatomy MOC]]
- [[Skill Index]]
- [[Workflow Index]]
- [[Pattern Index]]
- [[Evidence And Quality Index]]
- [[Reuse Asset Index]]
- [[Anchor Index]]
""",
    }
    paths = []
    for name, content in files.items():
        path = output_dir / "00 Maps" / name
        write_text(path, content)
        paths.append(path)
    return paths



def _write_anchor_notes(output_dir: Path, anchors_doc: dict[str, Any], composition_plan: dict[str, Any]) -> list[Path]:
    anchors = anchors_doc.get("anchors", []) if isinstance(anchors_doc, dict) else []
    paths: list[Path] = []
    for anchor in anchors:
        if not isinstance(anchor, dict):
            continue
        path = output_dir / "07 Anchors" / f"{_anchor_note_name(anchor)}.md"
        write_text(path, _anchor_note_content(anchor))
        paths.append(path)
    if composition_plan:
        path = output_dir / "07 Anchors" / "Composition Plan.md"
        write_text(path, _composition_note_content(composition_plan))
        paths.append(path)
    return paths


def _anchor_index_row(anchor: dict[str, Any]) -> str:
    name = _text_value(anchor.get("name", {})) or anchor.get("id", "anchor")
    anchor_type = anchor.get("anchor_type", "unknown")
    source_skill_id = anchor.get("source_skill_id", "unknown")
    return f"- [[{_anchor_note_name(anchor)}|{name}]] — type=`{anchor_type}` source=`{source_skill_id}`"


def _composition_index_line(plan: dict[str, Any]) -> str:
    if not plan:
        return "- No composition plan generated yet."
    selected = plan.get("selected_anchors", []) if isinstance(plan.get("selected_anchors"), list) else []
    policy = plan.get("dispatch_policy", {}).get("policy", "prefer_existing_skill") if isinstance(plan.get("dispatch_policy"), dict) else "prefer_existing_skill"
    return f"- [[Composition Plan]] — form=`{plan.get('composition_form', 'unknown')}` selected=`{len(selected)}` dispatch=`{policy}`"


def _anchor_note_content(anchor: dict[str, Any]) -> str:
    name = _text_value(anchor.get("name", {})) or anchor.get("id", "anchor")
    summary = _text_value(anchor.get("summary", {})) or "No summary."
    anchor_type = anchor.get("anchor_type", "unknown")
    source_skill_id = anchor.get("source_skill_id", "unknown")
    confidence = anchor.get("confidence") or _anchor_confidence(anchor)
    risk = anchor.get("risk", {}) if isinstance(anchor.get("risk"), dict) else {}
    risk_score = risk.get("score", "unknown")
    reuse_modes = anchor.get("reuse_modes", []) if isinstance(anchor.get("reuse_modes"), list) else []
    evidence = anchor.get("source_evidence", []) or anchor.get("evidence", []) or []
    evidence_lines = "\n".join(_anchor_evidence_line(item) for item in evidence if isinstance(item, dict)) or "- No evidence attached."
    reuse_lines = _list_block(reuse_modes, "No reuse modes recorded.")
    return f"""---
type: asa-anchor
anchor_id: {anchor.get('id', 'anchor')}
anchor_type: {anchor_type}
source_skill_id: {source_skill_id}
tags:
  - asa/anchor
  - asa/anchor/{_slug(anchor_type)}
---

# {name}

> {summary}

## Anchor Metadata

- **Type**: `{anchor_type}`
- **Source skill**: `{source_skill_id}`
- **Confidence**: `{confidence}`
- **Risk**: `{risk_score}`

## Reuse Modes

{reuse_lines}

## Evidence

{evidence_lines}

## Links

- [[Anchor Index]]
- [[Agent Skill Anatomy MOC]]
"""


def _composition_note_content(plan: dict[str, Any]) -> str:
    selected = plan.get("selected_anchors", []) if isinstance(plan.get("selected_anchors"), list) else []
    rejected = plan.get("rejected_anchors", []) if isinstance(plan.get("rejected_anchors"), list) else []
    dispatch = plan.get("dispatch_policy", {}) if isinstance(plan.get("dispatch_policy"), dict) else {}
    solidification = plan.get("solidification", {}) if isinstance(plan.get("solidification"), dict) else {}
    selected_lines = "\n".join(f"- `{item.get('anchor_id', 'anchor')}` — {item.get('reason', '')}" for item in selected if isinstance(item, dict)) or "- No anchors selected."
    rejected_lines = "\n".join(f"- `{item.get('anchor_id', 'anchor')}` — {item.get('reason', '')}" for item in rejected if isinstance(item, dict)) or "- No anchors rejected."
    return f"""---
type: asa-composition-plan
composition_form: {plan.get('composition_form', 'unknown')}
tags:
  - asa/anchor
  - asa/composition
---

# Composition Plan

{_text_value(plan.get('summary', {})) or 'No summary.'}

## Policy

- **Form**: `{plan.get('composition_form', 'unknown')}`
- **Dispatch**: `{dispatch.get('policy', 'prefer_existing_skill')}`
- **Solidification requested**: `{str(solidification.get('requested', False)).lower()}`

## Selected Anchors

{selected_lines}

## Rejected Anchors

{rejected_lines}

## Links

- [[Anchor Index]]
- [[Agent Skill Anatomy MOC]]
"""


def _anchor_evidence_line(item: dict[str, Any]) -> str:
    path = item.get("path", "unknown")
    quote = item.get("quote", "")
    confidence = item.get("confidence", "unknown")
    return f"- `{path}` — {quote} (`confidence={confidence}`)"


def _anchor_confidence(anchor: dict[str, Any]) -> str:
    evidence = anchor.get("source_evidence") or anchor.get("evidence") or []
    for item in evidence:
        if isinstance(item, dict) and item.get("confidence"):
            return str(item.get("confidence"))
    return "unknown"


def _anchor_note_name(anchor: dict[str, Any]) -> str:
    anchor_type = anchor.get("anchor_type", "anchor")
    name = _text_value(anchor.get("name", {})) or anchor.get("id", "anchor")
    return f"{_slug(anchor_type)} - {_slug(name)}"

def _skill_index_row(skill: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    review = skill.get("review", {})
    skill_type = structure.get("skill_type", {}).get("primary", "unknown")
    confidence = structure.get("confidence", {}).get("overall", "unknown")
    return f"- [[{_skill_note_name(skill)}|{skill['name']}]] — type=`{skill_type}` confidence=`{confidence}` review=`{review.get('status', 'unknown')}` workflow=[[{_workflow_note_name(skill)}|open]]"


def _reuse_index_rows(skill: dict[str, Any]) -> str:
    review = skill.get("review", {})
    assets = review.get("reuse_assets", []) or []
    if not assets:
        return f"- [[{_skill_note_name(skill)}|{skill['name']}]] — no explicit reuse assets extracted"
    rows = []
    for asset in assets:
        if isinstance(asset, dict):
            name = asset.get("name") or asset.get("asset") or "reuse asset"
            rows.append(f"- [[{_skill_note_name(skill)}|{skill['name']}]] — {name}")
        else:
            rows.append(f"- [[{_skill_note_name(skill)}|{skill['name']}]] — {asset}")
    return "\n".join(rows)


def _knowledge_graph_edges(skill: dict[str, Any]) -> str:
    skill_node = _slug(skill.get("name") or skill.get("id") or "skill").replace("-", "_")
    skill_label = str(skill.get("name") or skill.get("id") or "skill").replace('"', "'")
    return "\n".join([
        f"  MOC[Agent Skill Anatomy MOC] --> {skill_node}[{skill_label}]",
        f"  {skill_node} --> {skill_node}_workflow[Workflow]",
        f"  {skill_node} --> {skill_node}_quality[Quality]",
        f"  {skill_node} --> {skill_node}_reuse[Reuse Assets]",
        f"  {skill_node}_workflow --> Report[Web Report]",
        f"  {skill_node}_reuse --> Vault[Obsidian Vault]",
    ])
def _write_obsidian_canvas(output_dir: Path, run_dir: Path, skills: list[dict[str, Any]], patterns: dict[str, Any], quality: dict[str, Any]) -> Path:
    import json
    nodes = []
    edges = []
    nodes.append({"id": "moc", "type": "file", "file": "00 Maps/Agent Skill Anatomy MOC.md", "x": 0, "y": 0, "width": 360, "height": 220})
    nodes.append({"id": "quality", "type": "file", "file": "05 Quality/Quality Report.md", "x": 860, "y": 0, "width": 340, "height": 180})
    nodes.append({"id": "reuse", "type": "file", "file": "00 Maps/Reuse Asset Index.md", "x": 860, "y": 240, "width": 340, "height": 180})
    nodes.append({"id": "graph", "type": "file", "file": "00 Maps/Knowledge Graph.md", "x": 0, "y": 300, "width": 360, "height": 180})
    edges.extend([
        {"id": "moc-graph", "fromNode": "moc", "fromSide": "bottom", "toNode": "graph", "toSide": "top"},
        {"id": "moc-quality", "fromNode": "moc", "fromSide": "right", "toNode": "quality", "toSide": "left"},
        {"id": "quality-reuse", "fromNode": "quality", "fromSide": "bottom", "toNode": "reuse", "toSide": "top"},
    ])
    for index, skill in enumerate(skills):
        skill_id = f"skill-{index}"
        workflow_id = f"workflow-{index}"
        y = index * 250
        nodes.append({"id": skill_id, "type": "file", "file": f"02 Skills/{_skill_note_name(skill)}.md", "x": 430, "y": y, "width": 360, "height": 210})
        nodes.append({"id": workflow_id, "type": "file", "file": f"03 Workflows/{_workflow_note_name(skill)}.md", "x": 430, "y": y + 250, "width": 360, "height": 190})
        edges.append({"id": f"moc-{skill_id}", "fromNode": "moc", "fromSide": "right", "toNode": skill_id, "toSide": "left"})
        edges.append({"id": f"{skill_id}-{workflow_id}", "fromNode": skill_id, "fromSide": "bottom", "toNode": workflow_id, "toSide": "top"})
        edges.append({"id": f"{skill_id}-quality", "fromNode": skill_id, "fromSide": "right", "toNode": "quality", "toSide": "left"})
        edges.append({"id": f"{skill_id}-reuse", "fromNode": skill_id, "fromSide": "right", "toNode": "reuse", "toSide": "left"})
    path = output_dir / "00 Maps" / "Skill Anatomy Canvas.canvas"
    write_text(path, json.dumps({"nodes": nodes, "edges": edges}, ensure_ascii=False, indent=2))
    return path


def _write_sources(output_dir: Path, inventory: dict[str, Any], skills: list[dict[str, Any]]) -> list[Path]:
    by_source: dict[str, list[dict[str, Any]]] = {}
    for skill in skills:
        source = skill.get("package", {}).get("source_name") or "unknown-source"
        by_source.setdefault(source, []).append(skill)
    paths = []
    for source, source_skills in sorted(by_source.items()):
        path = output_dir / "01 Sources" / f"{_slug(source)}.md"
        skill_links = "\n".join(f"- [[{_skill_note_name(skill)}|{skill['name']}]]" for skill in source_skills)
        content = f"""---
type: asa-source
source_name: {source}
tags:
  - asa/source
---

# {source}

## Learning Path

1. Open [[Skill Index]] and choose one skill.
2. Read the skill note for identity, trigger, boundary, resources, and outputs.
3. Open the paired workflow note to understand how the skill actually runs.
4. Use [[Evidence And Quality Index]] to verify which claims are grounded.

## Reuse Path

1. Start from [[Reuse Asset Index]] or [[Anchor Index]].
2. Follow each candidate back to its source skill and workflow.
3. Copy only the anchor, checklist, or pattern that still fits your target harness.

## Review Path

1. Use [[Quality Report]] for deterministic issues.
2. Use [[Review Summary]] for model reviewer concerns.
3. Use [[Knowledge Graph]] when relationships are easier to inspect visually.

## Skills

{skill_links}

## Inventory

- Source inventories: {len(inventory.get('source_inventories', []))}
- Total skills in run: {len(inventory.get('skill_packages', []))}
"""
        write_text(path, content)
        paths.append(path)
    return paths


def _write_skill_note(output_dir: Path, run_dir: Path, skill: dict[str, Any]) -> Path:
    structure = skill["structure"]
    workflow = skill["workflow"]
    review = skill["review"]
    summary = structure.get("summary", {})
    package = skill.get("package", {})
    target_agents = structure.get("target_agents", [])
    path = output_dir / "02 Skills" / f"{_skill_note_name(skill)}.md"
    content = f"""---
type: asa-skill
run_id: {run_dir.name}
skill_id: {skill['id']}
skill_name: {skill['name']}
source_path: {package.get('skill_md_path') or structure.get('source', {}).get('skill_md_path')}
review_status: {review.get('status', 'unknown')}
quality_issues: {skill.get('quality_issue_count', 0)}
tags:
  - asa/skill
  - asa/anatomy-manual
---

# {skill['name']}

## Learning Brief

{_skill_learning_brief(skill)}

## Summary

- ZH: {summary.get('zh') or ''}
- EN: {summary.get('en') or ''}

## Visual Map

```mermaid
{_skill_mermaid_map(skill)}
```

## Obsidian Queries

```dataview
LIST FROM #asa/workflow OR #asa/quality OR #asa/reuse
WHERE contains(file.outlinks, this.file.link)
```

## Anatomy

- Skill ID: `{skill['id']}`
- Skill file: `{package.get('skill_md_path') or structure.get('source', {}).get('skill_md_path') or 'unknown'}`
- Target agents: {_join_preview(target_agents, 'unknown')}
- Skill type: `{structure.get('skill_type', {}).get('primary', 'unknown')}`
- Confidence: `{structure.get('confidence', {}).get('overall', 'unknown')}`

## 10-Layer Anatomy Manual

{_skill_manual_sections(skill)}

## Method Layer

{_skill_method_layer(skill)}

## Composition Matrix

{_skill_composition_table(skill)}

## Evidence Audit

{_skill_evidence_audit(skill)}

## Reuse Assets

{_skill_reuse_assets(skill)}

## Reuse Kit

{_skill_reuse_kit(skill)}

## Links

- [[Agent Skill Anatomy MOC]]
- [[Skill Index]]
- [[Workflow Index]]
- [[Pattern Index]]
- [[Evidence And Quality Index]]
- [[Reuse Asset Index]]
- [[Anchor Index]]
- [[Knowledge Graph]]
- [[Skill Anatomy Canvas.canvas|Skill Anatomy Canvas]]
- [[{_workflow_note_name(skill)}|Workflow]]
- [[Quality Report]]
- [[Review Summary]]

## Canonical Artifacts

- `{skill['artifact_dir']}/structure_analysis.json`
- `{skill['artifact_dir']}/workflow_analysis.json`
- `{skill['artifact_dir']}/review_report.json`
"""
    write_text(path, content)
    return path


def _write_workflow_note(output_dir: Path, run_dir: Path, skill: dict[str, Any]) -> Path:
    workflow = skill["workflow"]
    summary = workflow.get("workflow_summary", {})
    steps = workflow.get("workflow_steps", [])
    trace = workflow.get("workflow_trace", {}) or {}
    mermaid = workflow.get("mermaid", {}).get("flowchart") or "flowchart TD\n  A[No workflow]"
    step_lines = "\n".join(_workflow_step_line(step) for step in steps) or "- No workflow steps."
    trace_pipeline = _workflow_trace_pipeline(trace)
    trace_steps = _workflow_trace_steps(trace)
    failure_modes = _list_block(trace.get("failure_modes", []) or workflow.get("failure_modes", []) or [], "- No failure modes recorded.")
    path = output_dir / "03 Workflows" / f"{_workflow_note_name(skill)}.md"
    content = f"""---
type: asa-workflow
run_id: {run_dir.name}
skill_id: {skill['id']}
tags:
  - asa/workflow
---

# {skill['name']} Workflow

## Summary

- ZH: {summary.get('zh') or ''}
- EN: {summary.get('en') or ''}

## Steps

{step_lines}

## Trace Pipeline

{trace_pipeline}

## Trace Steps

{trace_steps}

## Failure Modes

{failure_modes}

## Diagram

```mermaid
{mermaid}
```

## Related

- [[{_skill_note_name(skill)}|{skill['name']}]]
"""
    write_text(path, content)
    return path


def _write_pattern_notes(output_dir: Path, patterns: dict[str, Any]) -> list[Path]:
    paths = []
    for pattern in patterns.get("patterns", []):
        path = output_dir / "04 Patterns" / f"{_pattern_note_name(pattern)}.md"
        examples = "\n".join(f"- [[{example.get('skill_id')}]] — `{example.get('source_path')}`" for example in pattern.get("examples", [])) or "- No examples recorded."
        content = f"""---
type: asa-pattern
pattern_id: {pattern.get('id')}
category: {pattern.get('category')}
status: {pattern.get('status')}
confidence: {pattern.get('confidence')}
tags:
  - asa/pattern
---

# {pattern.get('canonical_name') or pattern.get('id')}

## Definition

- ZH: {pattern.get('definition', {}).get('zh', '')}
- EN: {pattern.get('definition', {}).get('en', '')}

## Problem

- ZH: {pattern.get('problem', {}).get('zh', '')}
- EN: {pattern.get('problem', {}).get('en', '')}

## Solution

- ZH: {pattern.get('solution', {}).get('zh', '')}
- EN: {pattern.get('solution', {}).get('en', '')}

## Examples

{examples}
"""
        write_text(path, content)
        paths.append(path)
    return paths


def _write_quality_note(output_dir: Path, quality: dict[str, Any]) -> Path:
    path = output_dir / "05 Quality" / "Quality Report.md"
    issue_lines = "\n".join(f"- `{issue.get('severity')}` `{issue.get('code')}` {issue.get('skill_id', '')}: {issue.get('message', '')}" for issue in quality.get("issues", [])) or "- No deterministic quality issues."
    content = f"""---
type: asa-quality-report
tags:
  - asa/quality
---

# Quality Report

- Checked skills: {quality.get('checked_skill_count', 0)}
- Issues: {quality.get('issue_count', 0)}
- Publishable by rules: `{quality.get('publishable_by_rules')}`

## Severity Counts

```json
{quality.get('severity_counts', {})}
```

## Issues

{issue_lines}
"""
    write_text(path, content)
    return path


def _write_review_note(output_dir: Path, review_summary: dict[str, Any]) -> Path:
    path = output_dir / "05 Quality" / "Review Summary.md"
    skill_lines = "\n".join(f"- `{skill.get('status')}` [[{skill.get('skill_id')}]] approved={skill.get('approved_for_publish')} issues={skill.get('issue_count', 0)}" for skill in review_summary.get("skills", [])) or "- No reviewer outputs."
    content = f"""---
type: asa-review-summary
tags:
  - asa/review
---

# Review Summary

- Reviewed skills: {review_summary.get('reviewed_skill_count', 0)}

## Status Counts

```json
{review_summary.get('status_counts', {})}
```

## Skills

{skill_lines}
"""
    write_text(path, content)
    return path


def _write_model_compare_seed(output_dir: Path, run_dir: Path, skills: list[dict[str, Any]], patterns: dict[str, Any], quality: dict[str, Any], review_summary: dict[str, Any]) -> Path:
    path = output_dir / "06 Data" / "model_compare_seed.jsonl"
    lines = []
    for skill in skills:
        structure = skill.get("structure", {})
        workflow = skill.get("workflow", {})
        review = skill.get("review", {})
        row = {
            "run_id": run_dir.name,
            "skill_id": skill.get("id"),
            "skill_name": skill.get("name"),
            "summary_zh": _text_value(structure.get("summary", {})),
            "skill_type": structure.get("skill_type", {}).get("primary", "unknown"),
            "workflow_steps": len(workflow.get("workflow_steps", []) or []),
            "review_status": review.get("status", "unknown"),
            "review_issues": len(review.get("issues", []) or []),
            "quality_issues": skill.get("quality_issue_count", 0),
            "patterns": len(patterns.get("patterns", []) or []),
            "evidence_score": (review.get("scores", {}) or {}).get("evidence_score"),
            "structure_score": (review.get("scores", {}) or {}).get("structure_score"),
            "workflow_score": (review.get("scores", {}) or {}).get("workflow_score"),
            "pattern_score": (review.get("scores", {}) or {}).get("pattern_score"),
            "bilingual_score": (review.get("scores", {}) or {}).get("bilingual_score"),
            "obsidian_score": (review.get("scores", {}) or {}).get("obsidian_score"),
        }
        import json
        lines.append(json.dumps(row, ensure_ascii=False))
    write_text(path, "\n".join(lines) + ("\n" if lines else ""))
    return path

def _write_templates(output_dir: Path) -> Path:
    path = output_dir / "_templates" / "Skill Note Template.md"
    content = """---
type: asa-template
tags:
  - asa/template
---

# {{skill_name}}

## Summary

## Anatomy

## Workflow

## Evidence

## Reusable Assets
"""
    write_text(path, content)
    return path


def _skill_method_layer(skill: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    workflow = skill.get("workflow", {})
    review = skill.get("review", {})
    identity = structure.get("identity", {}) or {}
    activation = structure.get("activation", {}) or {}
    resource_roles = structure.get("resource_roles", []) or []
    workflow_trace = workflow.get("workflow_trace", {}) or {}
    evidence_audit = review.get("evidence_audit", {}) or {}
    rows = [
        ("Identity", _text_value(identity.get("one_line", {})) or _text_value(structure.get("summary", {}))),
        ("Activation", _list_inline(activation.get("explicit_triggers", []) or structure.get("trigger_conditions", {}).get("explicit", []) or [], "未发现显式触发")),
        ("Resources", _list_inline([item.get("path") for item in resource_roles if isinstance(item, dict)], skill.get("package", {}).get("skill_md_path") or "SKILL.md")),
        ("Trace", _list_inline(workflow_trace.get("pipeline", []) or [], "未提取 trace pipeline")),
        ("Evidence", evidence_audit.get("rationale") or review.get("status", "unknown")),
    ]
    lines = ["| Layer | Summary |", "|---|---|"]
    lines.extend(f"| {layer} | {summary or '—'} |" for layer, summary in rows)
    if resource_roles:
        lines.append("\n### Resource Roles")
        lines.append("\n| Path | Role | Stage | Read | Reuse |")
        lines.append("|---|---|---|---|---|")
        for item in resource_roles:
            if isinstance(item, dict):
                lines.append(f"| `{item.get('path', 'file')}` | {item.get('role', '—')} | {item.get('stage', '—')} | `{item.get('read_policy', 'unknown')}` | `{item.get('reuse_value', 'unknown')}` |")
    return "\n".join(lines)


def _skill_evidence_audit(skill: dict[str, Any]) -> str:
    review = skill.get("review", {})
    audit = review.get("evidence_audit", {}) or {}
    if not audit:
        return f"- Status: `{review.get('status', 'unknown')}`\n- No structured evidence audit exported."
    sections = [
        ("Supported Claims", audit.get("supported_claims", [])),
        ("Inferred Claims", audit.get("inferred_claims", [])),
        ("Unsupported Claims", audit.get("unsupported_claims", [])),
        ("Missing Evidence", audit.get("missing_evidence", [])),
        ("Conflicts", audit.get("conflicts", [])),
    ]
    lines = [f"- Publishability: `{audit.get('publishable') or review.get('status', 'unknown')}`", f"- Rationale: {audit.get('rationale') or review.get('approved_for_publish', {}).get('rationale', '')}"]
    for title, values in sections:
        lines.append(f"\n### {title}")
        lines.append(_list_block(values, "- None"))
    return "\n".join(lines)


def _skill_reuse_assets(skill: dict[str, Any]) -> str:
    patterns = skill.get("patterns", {}) or {}
    reuse_assets = patterns.get("reuse_assets", {}) or {}
    specs = [
        ("Reusable Patterns", reuse_assets.get("patterns", [])),
        ("Templates", reuse_assets.get("templates", [])),
        ("Checklists", reuse_assets.get("checklists", [])),
        ("Anti-Patterns", reuse_assets.get("anti_patterns", [])),
        ("Extension Ideas", reuse_assets.get("extension_ideas", [])),
    ]
    lines = []
    for title, values in specs:
        lines.append(f"### {title}")
        lines.append(_list_block(values, "- None"))
        lines.append("")
    return "\n".join(lines).strip()


def _skill_manual_sections(skill: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    workflow = skill.get("workflow", {})
    review = skill.get("review", {})
    package = skill.get("package", {})
    steps = workflow.get("workflow_steps", []) or []
    related = package.get("related_files", []) or []
    sections = [
        ("01 身份层", f"这是一个 `{structure.get('skill_type', {}).get('primary', 'unknown')}` 型 skill。{_text_value(structure.get('summary', {}))}"),
        ("02 触发层", _list_inline([*(structure.get('trigger_conditions', {}).get('explicit', []) or []), *(structure.get('trigger_conditions', {}).get('inferred', []) or [])], "未提取触发条件")),
        ("03 输入层", _list_inline(structure.get("inputs", []) or [], "未提取输入")),
        ("04 资源层", _list_inline([_path_value(item) for item in related], "未提取相关资源")),
        ("05 上下文层", _text_value(structure.get("context_strategy", {}).get("description")) or _text_value(structure.get("context_strategy", {}).get("summary")) or "未提取上下文策略"),
        ("06 执行层", f"共 {len(steps)} 个步骤：" + _list_inline([_text_value(step.get('name', {})) for step in steps if isinstance(step, dict)], "未提取步骤")),
        ("07 控制层", _list_inline(workflow.get("verification_points", []) or workflow.get("failure_modes", []) or [], "未提取控制点")),
        ("08 产出层", _list_inline(structure.get("outputs", []) or [], "未提取产出")),
        ("09 证据层", f"review=`{review.get('status', 'unknown')}` issues={len(review.get('issues', []) or [])} approved={bool(review.get('approved_for_publish', {}).get('value'))}"),
        ("10 复用层", _list_inline(workflow.get("reusable_candidates", []) or [], "从两阶段流程、模板和验证点中提炼复用资产")),
    ]
    return "\n".join(f"### {title}\n\n{body}\n" for title, body in sections)


def _skill_composition_table(skill: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    package = skill.get("package", {})
    anatomy = structure.get("file_anatomy", {}) or {}
    rows = [
        ("SKILL.md", package.get("skill_md_path") or anatomy.get("main_skill_file") or "SKILL.md", "主指令、触发和流程"),
        ("frontmatter", structure.get("frontmatter", {}).get("name") or skill.get("name"), "入口元数据"),
        ("templates", _list_inline([_path_value(item) for item in anatomy.get("templates", [])], "无"), "稳定输出骨架"),
        ("related files", _list_inline([_path_value(item) for item in package.get("related_files", [])], "无"), "同包资源"),
        ("outputs", _list_inline(structure.get("outputs", []) or [], "未声明"), "最终交付"),
    ]
    table = ["| Part | Source | Role |", "|---|---|---|"]
    table.extend(f"| {part} | `{source}` | {role} |" for part, source, role in rows)
    return "\n".join(table)


def _skill_reuse_kit(skill: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    workflow = skill.get("workflow", {})
    risks = structure.get("risks", []) or []
    return f"""### 可迁移模式

`Concept → Template → Artifact`

先生成概念/哲学中间产物，再用固定模板实现稳定产物。适合创意代码、可视化、报告生成和交互式网页输出。

### 复用检查清单

- [ ] 触发条件是否足够明确？
- [ ] 是否先生成中间约束，再进入实现？
- [ ] 是否有模板或 schema 稳定输出？
- [ ] 每个关键步骤是否有证据？
- [ ] 是否有输出验证和风险提示？

### 风险提示

{_list_block(risks, "- 暂无风险")}

### 可复制骨架

1. Define activation signals.
2. Generate intermediate concept/specification.
3. Load stable template/schema.
4. Fill variable implementation slots.
5. Verify output constraints.
6. Publish learning/reuse assets.
"""


def _skill_learning_brief(skill: dict[str, Any]) -> str:
    structure = skill.get("structure", {})
    workflow = skill.get("workflow", {})
    review = skill.get("review", {})
    package = skill.get("package", {})
    trigger = _list_inline([*(structure.get("trigger_conditions", {}).get("explicit", []) or []), *(structure.get("trigger_conditions", {}).get("inferred", []) or [])], "未提取触发条件")
    outputs = _list_inline(structure.get("outputs", []) or [], "未声明输出")
    workflow_summary = _text_value(workflow.get("workflow_summary", {})) or "未提取工作流摘要"
    return f"""- **它是什么**：{_text_value(structure.get('summary', {})) or skill.get('name')}
- **什么时候用**：{trigger}
- **如何运行**：{workflow_summary}
- **产出什么**：{outputs}
- **复用价值**：可从 [[Reuse Asset Index]] 查看可迁移模式、模板和检查清单。
- **证据状态**：review=`{review.get('status', 'unknown')}`，quality issues=`{skill.get('quality_issue_count', 0)}`。
- **来源文件**：`{package.get('skill_md_path') or structure.get('source', {}).get('skill_md_path') or 'unknown'}`
"""


def _skill_mermaid_map(skill: dict[str, Any]) -> str:
    safe_name = str(skill.get("name") or "Skill").replace('"', "'")
    return "\n".join([
        "flowchart LR",
        f"  A[Trigger] --> B[\"{safe_name}\"]",
        "  B --> C[Resources]",
        "  C --> D[Workflow]",
        "  D --> E[Evidence Review]",
        "  E --> F[Reusable Assets]",
        "  F --> G[Report / Vault / Graph]",
    ])


def _text_value(value: Any, language: str = "zh") -> str:
    if isinstance(value, dict):
        return str(value.get(language) or value.get("en") or value.get("zh") or value.get("name") or value.get("id") or "")
    if value is None:
        return ""
    return str(value)



def _join_preview(values: list[Any], fallback: str) -> str:
    clean = [_text_value(value) for value in values if _text_value(value)]
    return " · ".join(clean[:3]) if clean else fallback


def _path_value(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("path") or value.get("name") or value.get("id") or value.get("role") or "")
    if value is None:
        return ""
    return str(value)


def _list_inline(values: list[Any], fallback: str) -> str:
    clean = [_text_value(value) for value in values if _text_value(value)]
    return "；".join(clean[:6]) if clean else fallback


def _list_block(values: list[Any], fallback: str) -> str:
    clean = [_text_value(value) for value in values if _text_value(value)]
    return "\n".join(f"- {item}" for item in clean) if clean else fallback

def _workflow_trace_pipeline(trace: dict[str, Any]) -> str:
    pipeline = trace.get("pipeline", []) or []
    if not pipeline:
        return "No trace pipeline recorded."
    return " → ".join(str(item) for item in pipeline)


def _workflow_trace_steps(trace: dict[str, Any]) -> str:
    steps = [step for step in trace.get("steps", []) or [] if isinstance(step, dict)]
    if not steps:
        return "- No trace steps recorded."
    lines = []
    for step in steps:
        name = _text_value(step.get("name", {})) or step.get("id", "trace_step")
        action = _text_value(step.get("action", {})) or str(step.get("action") or "")
        resources = _list_inline(step.get("resources", []) or [], "none")
        downstream = _list_inline(step.get("downstream", []) or [], "none")
        lines.append(f"- **{name}** — {action} (`actor={step.get('actor', 'unknown')}`, `confidence={step.get('confidence', 'unknown')}`)\n  - Resources: `{resources}`\n  - Downstream: `{downstream}`")
    return "\n".join(lines)


def _workflow_step_line(step: dict[str, Any]) -> str:
    name = step.get("name", {})
    action = step.get("action", {})
    confidence = step.get("confidence", "unknown")
    inferred = " inferred" if step.get("inferred") else ""
    return f"- **{name.get('zh') or name.get('en') or step.get('id', 'step')}** — {action.get('zh') or action.get('en') or ''} (`confidence={confidence}{inferred}`)"


def _skill_note_name(skill: dict[str, Any]) -> str:
    return f"{_slug(skill.get('name') or 'skill')} - {_slug(skill['id'])}"


def _workflow_note_name(skill: dict[str, Any]) -> str:
    return f"{_slug(skill.get('name') or 'skill')} - {_slug(skill['id'])}.workflow"


def _pattern_note_name(pattern: dict[str, Any]) -> str:
    return _slug(pattern.get("canonical_name") or pattern.get("id") or "pattern")


def _slug(value: Any) -> str:
    text = str(value).strip().replace("/", "-").replace("\\", "-")
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^\w\-.\u4e00-\u9fff]+", "-", text)
    return text.strip("-") or "untitled"


def _read_optional_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    return read_json(path)











