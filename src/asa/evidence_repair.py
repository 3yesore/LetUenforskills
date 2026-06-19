from __future__ import annotations

from copy import deepcopy
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from .jsonio import read_json, write_json
from .quality.rules import normalize_text, quote_found_in_file

ARTIFACT_NAMES = ("structure_analysis.json", "workflow_analysis.json")
DEFAULT_THRESHOLD = 0.58


def repair_run_evidence(run_dir: Path, *, threshold: float = DEFAULT_THRESHOLD) -> dict[str, Any]:
    inventory = read_json(run_dir / "inventory.json")
    source_roots = _source_roots(inventory, run_dir)
    packages = {package.get("id"): package for package in inventory.get("skill_packages", []) if isinstance(package, dict)}
    all_changes: list[dict[str, Any]] = []
    artifact_count = 0

    skills_dir = run_dir / "skills"
    for skill_dir in sorted(path for path in skills_dir.glob("*") if path.is_dir()) if skills_dir.exists() else []:
        package = packages.get(skill_dir.name, {})
        source_root = _source_root_for_package(package, source_roots)
        if source_root is None:
            continue
        for artifact_name in ARTIFACT_NAMES:
            artifact_path = skill_dir / artifact_name
            if not artifact_path.exists():
                continue
            artifact = read_json(artifact_path)
            pre_changes: list[dict[str, Any]] = []
            if artifact_name == "structure_analysis.json":
                _repair_structure_manifest(artifact, package, pre_changes)
            repaired, changes = repair_evidence_in_artifact(artifact, source_root, threshold=threshold)
            changes = pre_changes + changes
            if changes:
                write_json(artifact_path, repaired)
                write_json(artifact_path.with_name(artifact_path.stem + ".evidence_repair.json"), {"changes": changes})
                all_changes.extend({**change, "skill_id": skill_dir.name, "artifact": artifact_name} for change in changes)
            artifact_count += 1

    report = {
        "run_dir": str(run_dir),
        "artifact_count": artifact_count,
        "change_count": len(all_changes),
        "changes": all_changes,
    }
    write_json(run_dir / "evidence_repair_report.json", report)
    return report


def repair_evidence_in_artifact(data: dict[str, Any], source_root: Path, *, threshold: float = DEFAULT_THRESHOLD) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    repaired = deepcopy(data)
    changes: list[dict[str, Any]] = []
    _walk(repaired, source_root, changes, threshold=threshold, path="$", parent=None)
    return repaired, changes


def _walk(value: Any, source_root: Path, changes: list[dict[str, Any]], *, threshold: float, path: str, parent: dict[str, Any] | None) -> None:
    if isinstance(value, dict):
        if _is_evidence(value):
            _repair_evidence(value, source_root, changes, threshold=threshold, path=path, parent=parent)
        for key, child in value.items():
            _walk(child, source_root, changes, threshold=threshold, path=f"{path}.{key}", parent=value)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk(child, source_root, changes, threshold=threshold, path=f"{path}[{index}]", parent=parent)


def _repair_evidence(evidence: dict[str, Any], source_root: Path, changes: list[dict[str, Any]], *, threshold: float, path: str, parent: dict[str, Any] | None) -> None:
    source_path = evidence.get("source_path")
    quote = evidence.get("quote")
    if not source_path or not isinstance(quote, str) or not quote.strip():
        return
    source_file = source_root / str(source_path)
    if not source_file.exists() or not source_file.is_file():
        return
    source_text = source_file.read_text(encoding="utf-8", errors="replace")
    if quote in source_text:
        return

    candidate = _best_quote_candidate(quote, source_text, threshold=threshold)
    if candidate:
        old_quote = quote
        evidence["quote"] = candidate
        changes.append({"code": "QUOTE_REPAIRED", "path": path, "source_path": str(source_path), "old_quote": old_quote, "new_quote": candidate})
        return

    if evidence.get("evidence_type") != "inferred":
        evidence["evidence_type"] = "inferred"
        notes = evidence.get("notes") or ""
        addition = "Evidence quote could not be matched exactly in source; downgraded to inferred."
        evidence["notes"] = (notes + " " + addition).strip()
        if parent is not None:
            if parent.get("confidence") == "high":
                parent["confidence"] = "medium"
            if parent.get("inferred") is False:
                parent["inferred"] = True
        changes.append({"code": "EVIDENCE_DOWNGRADED", "path": path, "source_path": str(source_path), "quote": quote})


def _best_quote_candidate(quote: str, source_text: str, *, threshold: float) -> str | None:
    normalized_quote = normalize_text(quote)
    if not normalized_quote:
        return None
    lines = [line.strip() for line in source_text.splitlines() if line.strip()]
    best_line = ""
    best_score = 0.0
    for line in lines:
        normalized_line = normalize_text(line)
        if not normalized_line:
            continue
        left_tokens = set(normalized_quote.split())
        right_tokens = set(normalized_line.split())
        overlap_count = len(left_tokens & right_tokens)
        if normalized_quote in normalized_line:
            return _trim_line(line)
        if normalized_line in normalized_quote and overlap_count >= 4:
            return _trim_line(line)
        score = SequenceMatcher(None, normalized_quote, normalized_line).ratio()
        token_score = _token_overlap(normalized_quote, normalized_line)
        combined = max(score, token_score)
        if combined > best_score:
            best_score = combined
            best_line = line
    if best_score >= threshold and best_line:
        return _trim_line(best_line)
    return None


def _trim_line(line: str, *, max_words: int = 25) -> str:
    words = line.split()
    if len(words) <= max_words:
        return line.strip()
    return " ".join(words[:max_words]).strip()


def _token_overlap(left: str, right: str) -> float:
    left_tokens = set(left.split())
    right_tokens = set(right.split())
    if not left_tokens or not right_tokens:
        return 0.0
    return len(left_tokens & right_tokens) / max(len(left_tokens), 1)


def _repair_structure_manifest(artifact: dict[str, Any], package: dict[str, Any], changes: list[dict[str, Any]]) -> None:
    scripts = package.get("scripts") if isinstance(package, dict) else None
    if not scripts:
        return
    file_anatomy = artifact.setdefault("file_anatomy", {})
    if not isinstance(file_anatomy, dict):
        artifact["file_anatomy"] = {"scripts": scripts}
        changes.append({"code": "SCRIPT_MANIFEST_REPAIRED", "path": "file_anatomy", "count": len(scripts)})
        return
    if not file_anatomy.get("scripts"):
        file_anatomy["scripts"] = scripts
        changes.append({"code": "SCRIPT_MANIFEST_REPAIRED", "path": "file_anatomy.scripts", "count": len(scripts)})


def _source_roots(inventory: dict[str, Any], run_dir: Path | None = None) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for source_inventory in inventory.get("source_inventories", []) or []:
        if not isinstance(source_inventory, dict):
            continue
        name = str((source_inventory.get("source") or {}).get("name") or source_inventory.get("name") or "")
        root = (source_inventory.get("repository") or {}).get("root_path")
        if not root and run_dir is not None and source_inventory.get("path"):
            nested_path = run_dir / str(source_inventory["path"])
            if nested_path.exists():
                nested = read_json(nested_path)
                name = str((nested.get("source") or {}).get("name") or name)
                root = (nested.get("repository") or {}).get("root_path")
        if name and root:
            roots[name] = Path(root)
    return roots


def _source_root_for_package(package: dict[str, Any], source_roots: dict[str, Path]) -> Path | None:
    source_name = str(package.get("source_name") or package.get("source") or "")
    if source_name in source_roots:
        return source_roots[source_name]
    if len(source_roots) == 1:
        return next(iter(source_roots.values()))
    return None


def _is_evidence(value: dict[str, Any]) -> bool:
    return "source_path" in value and "quote" in value and "evidence_type" in value
