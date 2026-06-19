from __future__ import annotations

from copy import deepcopy
from typing import Any

DEFAULT_INFERRED_NOTE = "Inferred by model from surrounding structure; not directly stated by source."


def normalize_structure_analysis(data: dict[str, Any], *, max_quote_words: int = 25) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    normalized = deepcopy(data)
    changes: list[dict[str, Any]] = []

    normalized["tools"] = _normalize_tools(normalized.get("tools", []) or [], changes)
    _normalize_target_agents(normalized, changes)
    _normalize_evidence_tree(normalized, changes, max_quote_words=max_quote_words)
    return normalized, changes


def normalize_workflow_analysis(data: dict[str, Any], *, max_quote_words: int = 25) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    normalized = deepcopy(data)
    changes: list[dict[str, Any]] = []

    for step_index, step in enumerate(normalized.get("workflow_steps", []) or []):
        if not isinstance(step, dict):
            continue
        if step.get("inferred") and step.get("confidence") == "high":
            step["confidence"] = "medium"
            changes.append({"code": "INFERRED_CONFIDENCE_DOWNGRADED", "path": f"workflow_steps[{step_index}].confidence"})
        for evidence_index, evidence in enumerate(step.get("evidence", []) or []):
            if isinstance(evidence, dict):
                _normalize_evidence_item(
                    evidence,
                    changes,
                    max_quote_words=max_quote_words,
                    path=f"workflow_steps[{step_index}].evidence[{evidence_index}]",
                )
    _normalize_evidence_tree(normalized, changes, max_quote_words=max_quote_words)
    return normalized, changes


def normalize_artifact(schema_name: str, data: dict[str, Any], *, max_quote_words: int = 25) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if schema_name == "structure-analysis.schema.json":
        return normalize_structure_analysis(data, max_quote_words=max_quote_words)
    if schema_name == "workflow-analysis.schema.json":
        return normalize_workflow_analysis(data, max_quote_words=max_quote_words)
    return data, []


def _normalize_tools(tools: list[Any], changes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized_tools: list[dict[str, Any]] = []
    for index, tool in enumerate(tools):
        if isinstance(tool, str):
            normalized_tools.append({"name": tool, "type": "unknown", "required": False, "purpose": "", "evidence": []})
            changes.append({"code": "TOOL_STRING_NORMALIZED", "path": f"tools[{index}]", "value": tool})
            continue
        if isinstance(tool, dict):
            normalized_tool = dict(tool)
            if "name" not in normalized_tool:
                normalized_tool["name"] = str(normalized_tool.get("type") or normalized_tool.get("tool") or "unknown")
                changes.append({"code": "TOOL_NAME_DEFAULTED", "path": f"tools[{index}].name"})
            if "type" not in normalized_tool:
                normalized_tool["type"] = "unknown"
                changes.append({"code": "TOOL_TYPE_DEFAULTED", "path": f"tools[{index}].type"})
            if "required" not in normalized_tool:
                normalized_tool["required"] = False
                changes.append({"code": "TOOL_REQUIRED_DEFAULTED", "path": f"tools[{index}].required"})
            if "evidence" not in normalized_tool or not isinstance(normalized_tool.get("evidence"), list):
                normalized_tool["evidence"] = []
                changes.append({"code": "TOOL_EVIDENCE_DEFAULTED", "path": f"tools[{index}].evidence"})
            normalized_tools.append(normalized_tool)
            continue
        normalized_tools.append({"name": str(tool), "type": "unknown", "required": False, "purpose": "", "evidence": []})
        changes.append({"code": "TOOL_VALUE_NORMALIZED", "path": f"tools[{index}]"})
    return normalized_tools


def _normalize_target_agents(structure: dict[str, Any], changes: list[dict[str, Any]]) -> None:
    target_agents = structure.get("target_agents") or []
    if not isinstance(target_agents, list):
        return

    normalized_agents: list[dict[str, Any]] = []
    any_unsupported = False
    for index, agent in enumerate(target_agents):
        if isinstance(agent, str):
            normalized_agents.append(
                {
                    "name": agent,
                    "confidence": "medium",
                    "inferred": True,
                    "evidence": [],
                    "notes": "Inferred from task framing; source does not explicitly name the agent audience.",
                }
            )
            any_unsupported = True
            changes.append({"code": "TARGET_AGENT_INFERRED", "path": f"target_agents[{index}]", "value": agent})
            continue
        if isinstance(agent, dict):
            normalized_agent = dict(agent)
            evidence = normalized_agent.get("evidence") or []
            if "name" not in normalized_agent:
                normalized_agent["name"] = str(normalized_agent.get("agent") or "unknown")
            if not evidence:
                normalized_agent["inferred"] = True
                if normalized_agent.get("confidence") == "high" or "confidence" not in normalized_agent:
                    normalized_agent["confidence"] = "medium"
                normalized_agent.setdefault("notes", "Inferred from task framing; source does not explicitly name the agent audience.")
                any_unsupported = True
                changes.append({"code": "TARGET_AGENT_INFERRED", "path": f"target_agents[{index}]"})
            normalized_agent.setdefault("evidence", [])
            normalized_agents.append(normalized_agent)
            continue
    structure["target_agents"] = normalized_agents

    confidence = structure.get("confidence")
    if any_unsupported and isinstance(confidence, dict) and confidence.get("overall") == "high":
        confidence["overall"] = "medium"
        notes = confidence.get("notes") or ""
        addition = " Target-agent audience was inferred without direct source evidence."
        confidence["notes"] = (notes + addition).strip()
        changes.append({"code": "OVERALL_CONFIDENCE_DOWNGRADED", "path": "confidence.overall"})


def _normalize_evidence_tree(value: Any, changes: list[dict[str, Any]], *, max_quote_words: int, path: str = "$") -> None:
    if isinstance(value, dict):
        if _looks_like_evidence(value):
            _normalize_evidence_item(value, changes, max_quote_words=max_quote_words, path=path)
        for key, child in value.items():
            _normalize_evidence_tree(child, changes, max_quote_words=max_quote_words, path=f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _normalize_evidence_tree(child, changes, max_quote_words=max_quote_words, path=f"{path}[{index}]")


def _normalize_evidence_item(evidence: dict[str, Any], changes: list[dict[str, Any]], *, max_quote_words: int, path: str) -> None:
    quote = evidence.get("quote")
    if isinstance(quote, str) and len(quote.split()) > max_quote_words:
        original = quote
        evidence["quote"] = " ".join(quote.split()[:max_quote_words])
        changes.append({"code": "QUOTE_TRIMMED", "path": f"{path}.quote", "original_word_count": len(original.split())})
    if evidence.get("evidence_type") == "inferred" and not evidence.get("notes"):
        evidence["notes"] = DEFAULT_INFERRED_NOTE
        changes.append({"code": "INFERRED_EVIDENCE_NOTES_ADDED", "path": f"{path}.notes"})


def _looks_like_evidence(value: dict[str, Any]) -> bool:
    return any(key in value for key in ("source_path", "quote", "evidence_type"))
