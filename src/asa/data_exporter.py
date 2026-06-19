from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .jsonio import read_json, write_json


DATA_FILES = {
    "skills": "skills.jsonl",
    "resource_roles": "resource_roles.csv",
    "workflow_trace": "workflow_trace.jsonl",
    "evidence_audit": "evidence_audit.jsonl",
    "reuse_assets": "reuse_assets.jsonl",
}


def export_data(run_dir: Path, output_dir: Path) -> dict[str, Any]:
    run_dir = run_dir.resolve()
    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    inventory = _read_optional_json(run_dir / "inventory.json", {})
    patterns = _read_optional_json(run_dir / "patterns" / "patterns.json", {"patterns": []})
    skills = _collect_skills(run_dir, inventory)

    skill_rows = [_skill_row(run_dir, skill) for skill in skills]
    resource_rows = [row for skill in skills for row in _resource_role_rows(run_dir, skill)]
    trace_rows = [row for skill in skills for row in _workflow_trace_rows(run_dir, skill)]
    audit_rows = [row for skill in skills for row in _evidence_audit_rows(run_dir, skill)]
    reuse_rows = _reuse_asset_rows(run_dir, patterns)

    _write_jsonl(output_dir / DATA_FILES["skills"], skill_rows)
    _write_csv(output_dir / DATA_FILES["resource_roles"], resource_rows, ["run_id", "skill_id", "path", "role", "stage", "read_policy", "reuse_value", "risk"])
    _write_jsonl(output_dir / DATA_FILES["workflow_trace"], trace_rows)
    _write_jsonl(output_dir / DATA_FILES["evidence_audit"], audit_rows)
    _write_jsonl(output_dir / DATA_FILES["reuse_assets"], reuse_rows)
    graph = _build_graph(run_dir, skill_rows, resource_rows, trace_rows, audit_rows, reuse_rows)
    write_json(output_dir / "graph-data.json", graph)
    (output_dir / "graph.mmd").write_text(_graph_mermaid(graph), encoding="utf-8")

    manifest = {
        "schema_version": 1,
        "run_id": run_dir.name,
        "skill_count": len(skills),
        "files": {**DATA_FILES, "graph": "graph-data.json", "graph_mermaid": "graph.mmd"},
        "row_counts": {
            "skills": len(skill_rows),
            "resource_roles": len(resource_rows),
            "workflow_trace": len(trace_rows),
            "evidence_audit": len(audit_rows),
            "reuse_assets": len(reuse_rows),
        },
    }
    write_json(output_dir / "data_manifest.json", manifest)
    return manifest


def _collect_skills(run_dir: Path, inventory: dict[str, Any]) -> list[dict[str, Any]]:
    packages = {item.get("id"): item for item in inventory.get("skill_packages", [])}
    skills_dir = run_dir / "skills"
    skills: list[dict[str, Any]] = []
    for skill_dir in sorted(path for path in skills_dir.glob("*") if path.is_dir()) if skills_dir.exists() else []:
        skill_id = skill_dir.name
        skills.append(
            {
                "id": skill_id,
                "package": packages.get(skill_id, {}),
                "structure": _read_optional_json(skill_dir / "structure_analysis.json", {}),
                "workflow": _read_optional_json(skill_dir / "workflow_analysis.json", {}),
                "review": _read_optional_json(skill_dir / "review_report.json", {}),
            }
        )
    return skills


def _skill_row(run_dir: Path, skill: dict[str, Any]) -> dict[str, Any]:
    structure = skill.get("structure", {})
    review = skill.get("review", {})
    identity = structure.get("identity", {}) or {}
    activation = structure.get("activation", {}) or {}
    return {
        "run_id": run_dir.name,
        "skill_id": skill.get("id"),
        "skill_name": skill.get("package", {}).get("name") or skill.get("id"),
        "source_path": skill.get("package", {}).get("skill_md_path") or structure.get("source", {}).get("skill_md_path"),
        "skill_type": structure.get("skill_type", {}).get("primary", "unknown"),
        "identity": _text_value(identity.get("one_line", {})) or _text_value(structure.get("summary", {})),
        "explicit_triggers": activation.get("explicit_triggers", []) or structure.get("trigger_conditions", {}).get("explicit", []) or [],
        "review_status": review.get("status", "unknown"),
        "publishable": review.get("approved_for_publish", {}).get("value"),
    }


def _resource_role_rows(run_dir: Path, skill: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    roles = skill.get("structure", {}).get("resource_roles", []) or []
    if not roles:
        package = skill.get("package", {}) or {}
        roles = [
            {"path": package.get("skill_md_path") or "SKILL.md", "role": "Primary skill instruction", "stage": "inspect", "read_policy": "must_read", "reuse_value": "medium"},
            *[{"path": item.get("path"), "role": item.get("reason", "script"), "stage": "execute", "read_policy": "on_demand", "reuse_value": "medium"} for item in package.get("scripts", []) or [] if isinstance(item, dict)],
            *[{"path": item.get("path"), "role": item.get("reason", "reference"), "stage": "inspect", "read_policy": "on_demand", "reuse_value": "medium"} for item in package.get("references", []) or [] if isinstance(item, dict)],
            *[{"path": item.get("path"), "role": item.get("reason", "asset"), "stage": "deliver", "read_policy": "optional", "reuse_value": "medium"} for item in package.get("assets", []) or [] if isinstance(item, dict)],
            *[{"path": item.get("path"), "role": item.get("reason", "related file"), "stage": "inspect", "read_policy": "on_demand", "reuse_value": "medium"} for item in package.get("related_files", []) or [] if isinstance(item, dict)],
        ]
    for item in roles:
        if not isinstance(item, dict) or not item.get("path"):
            continue
        rows.append(
            {
                "run_id": run_dir.name,
                "skill_id": skill.get("id"),
                "path": item.get("path", ""),
                "role": item.get("role", ""),
                "stage": item.get("stage", ""),
                "read_policy": item.get("read_policy", "unknown"),
                "reuse_value": item.get("reuse_value", "unknown"),
                "risk": item.get("risk", ""),
            }
        )
    return rows


def _workflow_trace_rows(run_dir: Path, skill: dict[str, Any]) -> list[dict[str, Any]]:
    workflow = skill.get("workflow", {}) or {}
    trace = workflow.get("workflow_trace", {}) or {}
    steps = trace.get("steps", []) or workflow.get("workflow_steps", []) or []
    rows = []
    for index, step in enumerate(steps, 1):
        if not isinstance(step, dict):
            continue
        rows.append(
            {
                "run_id": run_dir.name,
                "skill_id": skill.get("id"),
                "step_index": index,
                "step_id": step.get("id"),
                "name": _text_value(step.get("name", {})) or step.get("id"),
                "input": step.get("input"),
                "action": _text_value(step.get("action", {})) or step.get("action"),
                "output": step.get("output"),
                "actor": step.get("actor", "unknown"),
                "resources": step.get("resources", []) or [],
                "downstream": step.get("downstream", []) or [],
                "confidence": step.get("confidence", "unknown"),
                "inferred": step.get("inferred"),
            }
        )
    return rows


def _evidence_audit_rows(run_dir: Path, skill: dict[str, Any]) -> list[dict[str, Any]]:
    review = skill.get("review", {}) or {}
    audit = review.get("evidence_audit", {}) or {}
    rows = []
    categories = {
        "supported_claims": audit.get("supported_claims", []) or [],
        "inferred_claims": audit.get("inferred_claims", []) or [],
        "unsupported_claims": audit.get("unsupported_claims", []) or review.get("unsupported_claims", []) or [],
        "missing_evidence": audit.get("missing_evidence", []) or review.get("missing_evidence", []) or [],
        "conflicts": audit.get("conflicts", []) or [],
    }
    for category, claims in categories.items():
        for claim in claims:
            rows.append(
                {
                    "run_id": run_dir.name,
                    "skill_id": skill.get("id"),
                    "category": category,
                    "claim": _text_value(claim) or str(claim),
                    "publishable": audit.get("publishable") or review.get("status"),
                    "rationale": audit.get("rationale", "") or review.get("approved_for_publish", {}).get("rationale", ""),
                }
            )
    return rows


def _reuse_asset_rows(run_dir: Path, patterns: dict[str, Any]) -> list[dict[str, Any]]:
    reuse_assets = patterns.get("reuse_assets", {}) or {}
    rows = []
    for category in ["patterns", "templates", "checklists", "anti_patterns", "extension_ideas"]:
        for value in reuse_assets.get(category, []) or []:
            rows.append({"run_id": run_dir.name, "category": category, "value": _text_value(value) or str(value)})
    if not rows:
        for pattern in patterns.get("patterns", []) or []:
            rows.append(
                {
                    "run_id": run_dir.name,
                    "category": "patterns",
                    "value": pattern.get("zh_name") or pattern.get("canonical_name") or pattern.get("id"),
                }
            )
    return rows


def _build_graph(
    run_dir: Path,
    skill_rows: list[dict[str, Any]],
    resource_rows: list[dict[str, Any]],
    trace_rows: list[dict[str, Any]],
    audit_rows: list[dict[str, Any]],
    reuse_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    nodes: dict[str, dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    def add_node(node_id: str, node_type: str, label: str, **extra: Any) -> None:
        nodes.setdefault(node_id, {"id": node_id, "type": node_type, "label": label, **extra})

    add_node(f"run:{run_dir.name}", "run", run_dir.name)
    for skill in skill_rows:
        skill_id = str(skill.get("skill_id"))
        skill_node = f"skill:{skill_id}"
        add_node(skill_node, "skill", str(skill.get("skill_name") or skill_id), status=skill.get("review_status"), skill_type=skill.get("skill_type"))
        edges.append({"source": f"run:{run_dir.name}", "target": skill_node, "type": "contains_skill", "confidence": "deterministic"})
    for row in resource_rows:
        skill_node = f"skill:{row.get('skill_id')}"
        resource_path = str(row.get("path") or "resource")
        resource_node = f"resource:{row.get('skill_id')}:{resource_path}"
        add_node(resource_node, "resource", resource_path.split("/")[-1] or resource_path, path=resource_path, read_policy=row.get("read_policy"), reuse_value=row.get("reuse_value"))
        edges.append({"source": skill_node, "target": resource_node, "type": "uses_resource", "confidence": "structural"})
    previous_step_by_skill: dict[str, str] = {}
    for row in trace_rows:
        skill_id = str(row.get("skill_id"))
        skill_node = f"skill:{skill_id}"
        step_node = f"step:{skill_id}:{row.get('step_id') or row.get('step_index')}"
        add_node(step_node, "workflow_step", str(row.get("name") or row.get("step_id")), actor=row.get("actor"), confidence=row.get("confidence"))
        edges.append({"source": skill_node, "target": step_node, "type": "has_step", "confidence": row.get("confidence") or "unknown"})
        if previous_step_by_skill.get(skill_id):
            edges.append({"source": previous_step_by_skill[skill_id], "target": step_node, "type": "next_step", "confidence": row.get("confidence") or "unknown"})
        previous_step_by_skill[skill_id] = step_node
        for resource in row.get("resources", []) or []:
            resource_path = str(resource)
            resource_node = f"resource:{skill_id}:{resource_path}"
            add_node(resource_node, "resource", resource_path.split("/")[-1] or resource_path, path=resource_path)
            edges.append({"source": step_node, "target": resource_node, "type": "step_uses_resource", "confidence": row.get("confidence") or "unknown"})
    for row in audit_rows:
        skill_id = str(row.get("skill_id"))
        audit_node = f"audit:{skill_id}:{row.get('category')}:{abs(hash(row.get('claim'))) % 1000000}"
        add_node(audit_node, "evidence", str(row.get("claim"))[:80], category=row.get("category"), publishable=row.get("publishable"))
        edges.append({"source": f"skill:{skill_id}", "target": audit_node, "type": "has_evidence_audit", "confidence": "reviewer"})
    for index, row in enumerate(reuse_rows, 1):
        reuse_node = f"reuse:{index}:{row.get('category')}"
        add_node(reuse_node, "reuse", str(row.get("value"))[:80], category=row.get("category"))
        for skill in skill_rows:
            edges.append({"source": f"skill:{skill.get('skill_id')}", "target": reuse_node, "type": "has_reuse_asset", "confidence": "analysis"})
    return {"schema_version": 1, "run_id": run_dir.name, "nodes": list(nodes.values()), "edges": edges}


def _graph_mermaid(graph: dict[str, Any]) -> str:
    lines = ["graph TD"]
    safe_ids: dict[str, str] = {}
    for index, node in enumerate(graph.get("nodes", []), 1):
        safe_id = f"N{index}"
        safe_ids[node["id"]] = safe_id
        label = str(node.get("label") or node.get("id", "node")).replace('"', "'")
        lines.append(f'  {safe_id}["{label}"]')
    for edge in graph.get("edges", []):
        source = safe_ids.get(edge.get("source"))
        target = safe_ids.get(edge.get("target"))
        if not source or not target:
            continue
        label = str(edge.get("type", "rel")).replace('"', "'")
        lines.append(f'  {source} -- "{label}" --> {target}')
    return "\n".join(lines) + "\n"


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _read_optional_json(path: Path, fallback: Any) -> Any:
    return read_json(path) if path.exists() else fallback


def _text_value(value: Any, language: str = "zh") -> str:
    if isinstance(value, dict):
        return str(value.get(language) or value.get("en") or value.get("zh") or value.get("name") or value.get("id") or "")
    if value is None:
        return ""
    return str(value)
