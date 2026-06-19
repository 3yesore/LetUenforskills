from __future__ import annotations

from pathlib import Path

from .jsonio import read_json
from .schemas import SchemaValidationError, validate_named_schema


ARTIFACT_SCHEMAS = {
    "inventory.json": "inventory.schema.json",
    "patterns/patterns.json": "pattern.schema.json",
}


SKILL_ARTIFACT_SCHEMAS = {
    "structure_analysis.json": "structure-analysis.schema.json",
    "workflow_analysis.json": "workflow-analysis.schema.json",
    "review_report.json": "review-report.schema.json",
}


def validate_run(run_dir: Path) -> dict:
    issues: list[dict] = []
    checked: list[str] = []

    for relative_path, schema_name in ARTIFACT_SCHEMAS.items():
        validate_artifact(run_dir / relative_path, schema_name, run_dir, checked, issues)

    skills_dir = run_dir / "skills"
    if skills_dir.exists():
        for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
            for artifact_name, schema_name in SKILL_ARTIFACT_SCHEMAS.items():
                validate_artifact(skill_dir / artifact_name, schema_name, run_dir, checked, issues)
    else:
        issues.append({"path": "skills", "error": "skills directory not found"})

    return {
        "run_dir": str(run_dir),
        "checked": checked,
        "issues": issues,
        "valid": not issues,
    }


def validate_artifact(path: Path, schema_name: str, run_dir: Path, checked: list[str], issues: list[dict]) -> None:
    relative = str(path.relative_to(run_dir)) if path.exists() or path.parent.exists() else str(path)
    if not path.exists():
        issues.append({"path": relative, "schema": schema_name, "error": "missing artifact"})
        return
    try:
        validate_named_schema(read_json(path), schema_name)
        checked.append(relative)
    except (SchemaValidationError, ValueError) as exc:
        issues.append({"path": relative, "schema": schema_name, "error": str(exc)})

