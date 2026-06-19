from __future__ import annotations

from pathlib import Path
import re
from typing import Any


def check_workflow_quality(workflow: dict[str, Any], source_root: Path | None) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for step in workflow.get("workflow_steps", []):
        step_id = step.get("id", "unknown")
        confidence = step.get("confidence")
        inferred = bool(step.get("inferred"))
        evidence = step.get("evidence", []) or []

        if confidence == "high" and not evidence:
            issues.append(
                issue(
                    "HIGH_CONFIDENCE_WITHOUT_EVIDENCE",
                    "major",
                    f"Workflow step {step_id} is high confidence but has no evidence.",
                    f"workflow_steps.{step_id}.evidence",
                )
            )
        if inferred and confidence == "high":
            issues.append(
                issue(
                    "INFERRED_HIGH_CONFIDENCE",
                    "major",
                    f"Workflow step {step_id} is inferred but marked high confidence.",
                    f"workflow_steps.{step_id}.confidence",
                )
            )
        for index, evidence_item in enumerate(evidence):
            issues.extend(check_evidence_item(evidence_item, source_root, f"workflow_steps.{step_id}.evidence[{index}]"))
    return issues


def check_structure_quality(structure: dict[str, Any], source_root: Path | None = None) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    overall_confidence = structure.get("confidence", {}).get("overall")
    target_agents = structure.get("target_agents", []) or []
    if _has_unsupported_high_confidence_target_agents(target_agents, overall_confidence) and not structure_has_evidence(structure, "target_agents"):
        issues.append(
            issue(
                "TARGET_AGENTS_WITHOUT_EVIDENCE",
                "major",
                "target_agents are present with high confidence but no evidence was found.",
                "target_agents",
            )
        )

    scripts_manifest = structure.get("file_anatomy", {}).get("scripts", []) or []
    tools = structure.get("tools", []) or []
    for index, tool in enumerate(tools):
        if not isinstance(tool, dict):
            issues.append(
                issue(
                    "TOOL_ITEM_NOT_OBJECT",
                    "minor",
                    "Tool item should be an object with type, required, and evidence fields.",
                    f"tools[{index}]",
                )
            )
            continue
        tool_type = tool.get("type")
        evidence = tool.get("evidence", []) or []
        if tool_type == "cli" and not scripts_manifest and tool.get("required"):
            issues.append(
                issue(
                    "SCRIPT_TOOL_WITHOUT_SCRIPT_MANIFEST",
                    "major",
                    f"Required {tool_type} tool is listed but scripts manifest is empty.",
                    f"tools[{index}]",
                )
            )
        if tool.get("required") and not evidence:
            issues.append(
                issue(
                    "REQUIRED_TOOL_WITHOUT_EVIDENCE",
                    "major",
                    "Required tool lacks evidence.",
                    f"tools[{index}].evidence",
                )
            )
        for evidence_index, evidence_item in enumerate(evidence):
            issues.extend(check_evidence_item(evidence_item, source_root, f"tools[{index}].evidence[{evidence_index}]"))
    return issues



def _has_unsupported_high_confidence_target_agents(target_agents: Any, overall_confidence: Any) -> bool:
    if not target_agents or overall_confidence != "high":
        return False
    if not isinstance(target_agents, list):
        return False
    for target_agent in target_agents:
        if not isinstance(target_agent, dict):
            return True
        if target_agent.get("inferred"):
            continue
        if target_agent.get("confidence") == "high" or target_agent.get("confidence") is None:
            return True
    return False


def structure_has_evidence(value: Any, key_hint: str) -> bool:
    if isinstance(value, dict):
        if key_hint in value and isinstance(value[key_hint], dict) and value[key_hint].get("evidence"):
            return True
        if key_hint in value and isinstance(value[key_hint], list):
            return any(isinstance(item, dict) and item.get("evidence") for item in value[key_hint])
        return any(structure_has_evidence(item, key_hint) for item in value.values())
    if isinstance(value, list):
        return any(structure_has_evidence(item, key_hint) for item in value)
    return False


def check_evidence_item(evidence: dict[str, Any], source_root: Path | None, location: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    if not isinstance(evidence, dict):
        return [issue("EVIDENCE_ITEM_NOT_OBJECT", "minor", "Evidence item should be an object.", location)]
    source_path = evidence.get("source_path")
    quote = evidence.get("quote", "")
    evidence_type = evidence.get("evidence_type")

    if not source_path:
        issues.append(issue("EVIDENCE_SOURCE_MISSING", "major", "Evidence item lacks source_path.", location))
    source_file = source_root / source_path if source_root is not None and source_path else None
    if source_file is not None and not source_file.exists():
        issues.append(
            issue(
                "EVIDENCE_SOURCE_NOT_FOUND",
                "major",
                f"Evidence source path does not exist: {source_path}",
                location,
            )
        )
    elif source_file is not None and quote and evidence_type != "inferred" and not quote_found_in_file(source_file, quote):
        issues.append(
            issue(
                "EVIDENCE_QUOTE_NOT_FOUND",
                "major",
                f"Evidence quote was not found in source file: {source_path}",
                location,
            )
        )
    if quote and len(quote.split()) > 25:
        issues.append(issue("EVIDENCE_QUOTE_TOO_LONG", "minor", "Evidence quote exceeds 25 words.", location))
    if evidence_type == "inferred" and quote and not _notes_explain_inference(evidence.get("notes") or ""):
        issues.append(
            issue(
                "INFERRED_EVIDENCE_NEEDS_NOTES",
                "minor",
                "Inferred evidence should include notes explaining the inference.",
                location,
            )
        )
    return issues


def quote_found_in_file(source_file: Path, quote: str) -> bool:
    try:
        source_text = source_file.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return normalize_text(quote) in normalize_text(source_text)


def normalize_text(value: str) -> str:
    text = re.sub(r"https?://\S+", " url ", value)
    text = re.sub(r"[^0-9A-Za-z_\u4e00-\u9fff]+", " ", text)
    return " ".join(text.split()).casefold()


def _notes_explain_inference(notes: str) -> bool:
    normalized = notes.casefold()
    markers = ["infer", "inferred", "推断", "optional", "not a required", "on-demand", "surrounding structure"]
    return any(marker in normalized for marker in markers)


def issue(code: str, severity: str, message: str, location: str) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "message": message,
        "location": location,
    }
