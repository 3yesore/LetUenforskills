from __future__ import annotations

from pathlib import Path
from typing import Any

from .jsonio import read_json, write_json


ANCHOR_SCHEMA_VERSION = 1


def export_anchors(run_dir: Path, output_path: Path | None = None) -> dict[str, Any]:
    skills_dir = run_dir / "skills"
    if not skills_dir.exists():
        raise FileNotFoundError(f"Run skills directory not found: {skills_dir}")

    anchors: list[dict[str, Any]] = []
    for skill_dir in sorted(path for path in skills_dir.iterdir() if path.is_dir()):
        structure = _read_optional_json(skill_dir / "structure_analysis.json")
        workflow = _read_optional_json(skill_dir / "workflow_analysis.json")
        review = _read_optional_json(skill_dir / "review_report.json")
        if not structure and not workflow:
            continue
        anchors.extend(_anchors_for_skill(skill_dir.name, structure, workflow, review))

    patterns = _read_optional_json(run_dir / "patterns" / "patterns.json")
    anchors.extend(_reuse_anchors(patterns))

    document = {
        "schema_version": ANCHOR_SCHEMA_VERSION,
        "run_dir": str(run_dir),
        "anchor_count": len(anchors),
        "anchors": anchors,
    }
    if output_path:
        write_json(output_path, document)
    return document


def _read_optional_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = read_json(path)
    return data if isinstance(data, dict) else {}


def _anchors_for_skill(skill_dir_name: str, structure: dict[str, Any], workflow: dict[str, Any], review: dict[str, Any]) -> list[dict[str, Any]]:
    skill_id = str(structure.get("skill_id") or workflow.get("skill_id") or review.get("skill_id") or skill_dir_name)
    source = structure.get("source") if isinstance(structure.get("source"), dict) else {}
    skill_path = str(source.get("skill_md_path") or "SKILL.md")
    skill_name = str(_nested(structure, "frontmatter", "name", default=skill_id))
    confidence = str(_nested(structure, "confidence", "overall", default="unknown"))
    anchors: list[dict[str, Any]] = []

    summary = structure.get("summary") if isinstance(structure.get("summary"), dict) else {}
    if summary:
        anchors.append(
            _base_anchor(
                skill_id=skill_id,
                anchor_type="identity_anchor",
                local_name="identity",
                name={"zh": f"{skill_name} 身份", "en": f"{skill_name} Identity"},
                summary=summary,
                evidence=_evidence(skill_path, str(summary.get("en") or summary.get("zh") or skill_name), "reviewer_note", confidence),
                reuse_modes=["reference_only", "learning_note", "new_skill_spec"],
                confidence=confidence,
            )
        )

    triggers = structure.get("trigger_conditions") if isinstance(structure.get("trigger_conditions"), dict) else {}
    explicit_triggers = list(triggers.get("explicit") or [])
    if explicit_triggers:
        anchors.append(
            _base_anchor(
                skill_id=skill_id,
                anchor_type="trigger_anchor",
                local_name="explicit-triggers",
                name={"zh": "显式触发条件", "en": "Explicit Trigger Conditions"},
                summary={"zh": "；".join(map(str, explicit_triggers)), "en": "; ".join(map(str, explicit_triggers))},
                evidence=_evidence(skill_path, str(explicit_triggers[0]), "explicit_instruction", confidence),
                reuse_modes=["reference_only", "agent_rule_patch", "temporary_composition"],
                confidence=confidence,
            )
        )

    workflow_steps = workflow.get("workflow_steps") if isinstance(workflow.get("workflow_steps"), list) else []
    if workflow_steps:
        workflow_summary = workflow.get("workflow_summary") if isinstance(workflow.get("workflow_summary"), dict) else {}
        anchors.append(
            _base_anchor(
                skill_id=skill_id,
                anchor_type="workflow_anchor",
                local_name="workflow-chain",
                name={"zh": "工作流链路", "en": "Workflow Chain"},
                summary=workflow_summary or {"zh": "；".join(_step_names(workflow_steps, "zh")), "en": "; ".join(_step_names(workflow_steps, "en"))},
                evidence=_step_evidence(skill_path, workflow_steps),
                reuse_modes=["temporary_composition", "workflow_step", "prompt_fragment", "learning_note"],
                confidence=_lowest_step_confidence(workflow_steps, confidence),
            )
        )

    verification_points = workflow.get("verification_points") if isinstance(workflow.get("verification_points"), list) else []
    for index, point in enumerate(verification_points, start=1):
        if not isinstance(point, dict):
            continue
        point_name = str(point.get("name") or point.get("id") or f"verification {index}")
        anchors.append(
            _base_anchor(
                skill_id=skill_id,
                anchor_type="validation_anchor",
                local_name=f"validation-{index}",
                name={"zh": point_name, "en": point_name},
                summary={"zh": f"验证点：{point_name}", "en": f"Validation point: {point_name}"},
                evidence=_evidence(skill_path, point_name, "workflow_order", "medium"),
                reuse_modes=["quality_gate", "temporary_composition", "workflow_step"],
                confidence="medium",
            )
        )

    risks = structure.get("risks") if isinstance(structure.get("risks"), list) else []
    failure_modes = workflow.get("failure_modes") if isinstance(workflow.get("failure_modes"), list) else []
    for index, risk in enumerate([*risks, *failure_modes], start=1):
        if not isinstance(risk, dict):
            continue
        risk_name = str(risk.get("name") or risk.get("id") or f"risk {index}")
        severity = str(risk.get("severity") or "medium")
        anchors.append(
            _base_anchor(
                skill_id=skill_id,
                anchor_type="risk_anchor",
                local_name=f"risk-{index}",
                name={"zh": risk_name, "en": risk_name},
                summary={"zh": f"风险：{risk_name}", "en": f"Risk: {risk_name}"},
                evidence=_evidence(skill_path, risk_name, "reviewer_note", severity if severity in {"high", "medium", "low"} else "medium"),
                reuse_modes=["reference_only", "quality_gate", "learning_note"],
                confidence="medium",
                risk_score=severity if severity in {"high", "medium", "low"} else "medium",
            )
        )

    if review:
        approved = bool(_nested(review, "approved_for_publish", "value", default=False))
        status = str(review.get("status") or "unknown")
        anchors.append(
            _base_anchor(
                skill_id=skill_id,
                anchor_type="evidence_anchor",
                local_name="review-status",
                name={"zh": "证据审查状态", "en": "Evidence Review Status"},
                summary={"zh": f"发布状态：{status}", "en": f"Publish status: {status}"},
                evidence=_evidence(skill_path, str(_nested(review, "approved_for_publish", "rationale", default=status)), "reviewer_note", "high" if approved else "medium"),
                reuse_modes=["reference_only", "quality_gate", "learning_note"],
                confidence="high" if approved else "medium",
            )
        )
    return anchors


def _reuse_anchors(patterns_doc: dict[str, Any]) -> list[dict[str, Any]]:
    anchors: list[dict[str, Any]] = []
    patterns = patterns_doc.get("patterns") if isinstance(patterns_doc.get("patterns"), list) else []
    for pattern in patterns:
        if not isinstance(pattern, dict):
            continue
        pattern_id = str(pattern.get("id") or pattern.get("canonical_name") or "pattern")
        definition = pattern.get("definition") if isinstance(pattern.get("definition"), dict) else {}
        examples = pattern.get("examples") if isinstance(pattern.get("examples"), list) else []
        first_example = examples[0] if examples and isinstance(examples[0], dict) else {}
        skill_id = str(first_example.get("skill_id") or "patterns")
        source_path = str(first_example.get("source_path") or "patterns/patterns.json")
        confidence = str(pattern.get("confidence") or "unknown")
        anchors.append(
            _base_anchor(
                skill_id=skill_id,
                anchor_type="reuse_anchor",
                local_name=f"pattern-{_slug(pattern_id)}",
                name={"zh": str(pattern.get("zh_name") or pattern_id), "en": str(pattern.get("canonical_name") or pattern_id)},
                summary=definition or {"zh": str(pattern.get("problem") or pattern_id), "en": str(pattern.get("solution") or pattern_id)},
                evidence=_evidence(source_path, str(definition.get("en") or definition.get("zh") or pattern_id), "reviewer_note", confidence),
                reuse_modes=["reference_only", "temporary_composition", "learning_note", "prompt_fragment"],
                confidence=confidence,
            )
        )
    return anchors


def _base_anchor(
    *,
    skill_id: str,
    anchor_type: str,
    local_name: str,
    name: dict[str, str],
    summary: dict[str, str],
    evidence: list[dict[str, str]],
    reuse_modes: list[str],
    confidence: str,
    risk_score: str = "low",
) -> dict[str, Any]:
    return {
        "id": f"anchor.{_slug(skill_id)}.{anchor_type}.{_slug(local_name)}",
        "source_skill_id": skill_id,
        "anchor_type": anchor_type,
        "name": {"zh": str(name.get("zh") or name.get("en") or local_name), "en": str(name.get("en") or name.get("zh") or local_name)},
        "summary": {"zh": str(summary.get("zh") or summary.get("en") or ""), "en": str(summary.get("en") or summary.get("zh") or "")},
        "source_evidence": evidence,
        "portability": {"score": "medium", "reasons": ["Exported deterministically from run artifacts."]},
        "risk": {"score": risk_score, "notes": []},
        "reuse_modes": reuse_modes,
        "harness_contract": {
            "input_shape": "markdown",
            "output_shape": "markdown",
            "side_effects": "none",
            "requires_user_approval": False,
            "reversible": True,
        },
        "confidence": confidence,
    }


def _evidence(path: str, quote: str, evidence_type: str, confidence: str) -> list[dict[str, str]]:
    return [{"path": path, "quote": quote[:240], "evidence_type": evidence_type, "confidence": _normalize_confidence(confidence)}]


def _step_evidence(path: str, steps: list[Any]) -> list[dict[str, str]]:
    evidence: list[dict[str, str]] = []
    for step in steps[:5]:
        if not isinstance(step, dict):
            continue
        action = step.get("action") if isinstance(step.get("action"), dict) else {}
        quote = str(action.get("en") or action.get("zh") or step.get("id") or "workflow step")
        evidence.append({"path": path, "quote": quote[:240], "evidence_type": "workflow_order", "confidence": _normalize_confidence(str(step.get("confidence") or "unknown"))})
    return evidence


def _step_names(steps: list[Any], lang: str) -> list[str]:
    names: list[str] = []
    for step in steps:
        if not isinstance(step, dict):
            continue
        name = step.get("name") if isinstance(step.get("name"), dict) else {}
        names.append(str(name.get(lang) or name.get("en") or name.get("zh") or step.get("id") or "step"))
    return names


def _lowest_step_confidence(steps: list[Any], default: str) -> str:
    values = [_normalize_confidence(str(step.get("confidence") or default)) for step in steps if isinstance(step, dict)]
    if "low" in values:
        return "low"
    if "medium" in values:
        return "medium"
    if "high" in values:
        return "high"
    return _normalize_confidence(default)


def _normalize_confidence(value: str) -> str:
    lowered = value.lower()
    if lowered in {"high", "medium", "low"}:
        return lowered
    return "unknown"


def _nested(data: dict[str, Any], first: str, second: str, *, default: Any) -> Any:
    value = data.get(first)
    if isinstance(value, dict):
        return value.get(second, default)
    return default


def _slug(value: str) -> str:
    slug = "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug or "anchor"
