from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

from asa.jsonio import read_json
from asa.quality.rules import check_structure_quality, check_workflow_quality


def quality_report_for_run(run_dir: Path) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    skill_reports: list[dict[str, Any]] = []
    skills_dir = run_dir / "skills"
    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()) if skills_dir.exists() else []:
        structure_path = skill_dir / "structure_analysis.json"
        workflow_path = skill_dir / "workflow_analysis.json"
        snapshot_path = skill_dir / "source_snapshot.json"
        source_root = None
        if snapshot_path.exists():
            snapshot = read_json(snapshot_path)
            source_root = _source_root_for_snapshot(run_dir, snapshot)
        skill_issues = []
        if structure_path.exists():
            skill_issues.extend(check_structure_quality(read_json(structure_path), source_root))
        if workflow_path.exists():
            skill_issues.extend(check_workflow_quality(read_json(workflow_path), source_root))
        for item in skill_issues:
            item = dict(item)
            item["skill_id"] = skill_dir.name
            item["artifact"] = str(skill_dir.relative_to(run_dir))
            issues.append(item)
        content_quality = _content_quality_for_skill(
            read_json(structure_path) if structure_path.exists() else {},
            read_json(workflow_path) if workflow_path.exists() else {},
            read_json(skill_dir / "review_report.json") if (skill_dir / "review_report.json").exists() else {},
        )
        skill_reports.append({"skill_id": skill_dir.name, "issue_count": len(skill_issues), "content_quality": content_quality})

    severity_counts = Counter(issue["severity"] for issue in issues)
    code_counts = Counter(issue["code"] for issue in issues)
    content_quality = _aggregate_content_quality(skill_reports)
    return {
        "run_dir": str(run_dir),
        "checked_skill_count": len(skill_reports),
        "issue_count": len(issues),
        "severity_counts": dict(severity_counts),
        "code_counts": dict(code_counts),
        "content_quality": content_quality,
        "skills": skill_reports,
        "issues": issues,
        "publishable_by_rules": not any(issue["severity"] in {"blocker", "major"} for issue in issues),
    }


def _source_root_for_snapshot(run_dir: Path, snapshot: dict[str, Any]) -> Path | None:
    source_name = str(snapshot.get("skill_package", {}).get("source_name") or snapshot.get("source", {}).get("name") or "").strip()
    if source_name:
        packaged_root = run_dir / "sources" / _safe_file_name(source_name) / "files"
        if packaged_root.exists():
            return packaged_root
    root_path = snapshot.get("source", {}).get("path") or snapshot.get("source", {}).get("root_path")
    if root_path:
        source_root = Path(root_path)
        if source_root.exists():
            return source_root
    return None


def _safe_file_name(value: str) -> str:
    safe = "".join(character if character.isalnum() or character in {"-", "_", "."} else "-" for character in value).strip(".-")
    return safe or "source"


def _content_quality_for_skill(structure: dict[str, Any], workflow: dict[str, Any], review: dict[str, Any]) -> dict[str, Any]:
    joined = " ".join([str(structure), str(workflow), str(review)]).casefold()
    template_markers = [
        marker
        for marker in ["mock", "placeholder", "unknown", "awaiting real", "template", "todo", "待", "占位"]
        if marker in joined
    ]
    section_signals = [
        bool(structure.get("identity") or structure.get("summary")),
        bool(structure.get("activation") or structure.get("trigger_conditions")),
        bool(structure.get("resource_roles") or structure.get("file_anatomy")),
        bool(workflow.get("workflow_steps")),
        bool(review.get("evidence_audit") or review.get("supported_claims") or review.get("issues")),
        bool(review.get("reuse_assets") or review.get("scores")),
    ]
    evidence_count = _count_key_occurrences([structure, workflow, review], "evidence")
    workflow_steps = len(workflow.get("workflow_steps", []) or [])
    density_raw = sum(section_signals) / len(section_signals)
    evidence_bonus = min(evidence_count, 6) / 12
    workflow_bonus = min(workflow_steps, 4) / 12
    return {
        "density_score": min(1.0, round(density_raw * 0.74 + evidence_bonus + workflow_bonus, 3)),
        "template_tone_score": max(0.0, round(1.0 - min(len(template_markers), 6) * 0.14, 3)),
        "template_markers": template_markers,
        "evidence_count": evidence_count,
        "workflow_step_count": workflow_steps,
        "filled_section_count": sum(1 for item in section_signals if item),
    }


def _aggregate_content_quality(skill_reports: list[dict[str, Any]]) -> dict[str, Any]:
    qualities = [item.get("content_quality", {}) for item in skill_reports]
    if not qualities:
        return {"average_density_score": 0, "average_template_tone_score": 0, "template_marker_count": 0}
    return {
        "average_density_score": round(sum(float(item.get("density_score", 0)) for item in qualities) / len(qualities), 3),
        "average_template_tone_score": round(sum(float(item.get("template_tone_score", 0)) for item in qualities) / len(qualities), 3),
        "template_marker_count": sum(len(item.get("template_markers", []) or []) for item in qualities),
    }


def _count_key_occurrences(values: list[Any], key_name: str) -> int:
    count = 0
    for value in values:
        if isinstance(value, dict):
            for key, child in value.items():
                if key == key_name and child:
                    count += len(child) if isinstance(child, list) else 1
                count += _count_key_occurrences([child], key_name)
        elif isinstance(value, list):
            count += _count_key_occurrences(value, key_name)
    return count
