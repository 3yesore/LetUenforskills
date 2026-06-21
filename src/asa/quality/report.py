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
        skill_reports.append({"skill_id": skill_dir.name, "issue_count": len(skill_issues)})

    severity_counts = Counter(issue["severity"] for issue in issues)
    code_counts = Counter(issue["code"] for issue in issues)
    return {
        "run_dir": str(run_dir),
        "checked_skill_count": len(skill_reports),
        "issue_count": len(issues),
        "severity_counts": dict(severity_counts),
        "code_counts": dict(code_counts),
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
