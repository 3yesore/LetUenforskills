from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .config import parse_simple_yaml
from .jsonio import read_json, write_json


DEFAULT_DISPATCH_POLICY = "prefer_existing_skill"


def plan_anchor_composition(anchors_path: Path, request_path: Path, output_path: Path | None = None) -> dict[str, Any]:
    anchors_doc = read_json(anchors_path)
    request = _read_request(request_path)
    anchors = list(anchors_doc.get("anchors", []))
    constraints = request.get("constraints", {})
    goal = request.get("goal", {})
    selected_types = set(request.get("selected_anchor_types") or [])
    selected_sources = set(request.get("selected_source_skills") or [])
    excluded_sources = set(request.get("excluded_source_skills") or [])
    preferred_outputs = request.get("preferred_outputs") or ["json"]
    composition_form = str(goal.get("type") or "temporary_composition")

    selected: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for anchor in anchors:
        anchor_id = str(anchor.get("id") or "")
        anchor_type = str(anchor.get("anchor_type") or "")
        source_skill_id = str(anchor.get("source_skill_id") or "")
        rejection_reason = _rejection_reason(
            anchor=anchor,
            selected_types=selected_types,
            selected_sources=selected_sources,
            excluded_sources=excluded_sources,
            allowed_side_effects=set(constraints.get("allowed_side_effects") or ["none"]),
            composition_form=composition_form,
        )
        if rejection_reason:
            rejected.append({"anchor_id": anchor_id, "reason": rejection_reason})
            continue
        selected.append(
            {
                "anchor_id": anchor_id,
                "reason": _selection_reason(anchor, composition_form),
                "evidence_confidence": _evidence_confidence(anchor),
                "portability_score": _nested_value(anchor, "portability", "score", default="unknown"),
                "risk_score": _nested_value(anchor, "risk", "score", default="unknown"),
                "selected_reuse_mode": _select_reuse_mode(anchor, composition_form),
            }
        )

    compatibility_matrix = _build_compatibility_matrix(selected)
    output_kind = _preferred_output_kind(preferred_outputs, composition_form)
    plan = {
        "schema_version": 1,
        "request_id": _request_id(anchors_path, composition_form),
        "composition_form": composition_form,
        "summary": {
            "zh": "基于锚点的轻量组合计划；默认不修改用户已有 skill。",
            "en": "Lightweight anchor composition plan; existing user skills are not modified by default.",
        },
        "composition": {
            "form": composition_form,
            "dispatch_strategy": DEFAULT_DISPATCH_POLICY,
            "summary": {
                "zh": "基于锚点的轻量组合计划；默认不修改用户已有 skill。",
                "en": "Lightweight anchor composition plan; existing user skills are not modified by default.",
            },
        },
        "selected_anchors": selected,
        "rejected_anchors": rejected,
        "compatibility_matrix": compatibility_matrix,
        "dispatch_policy": {
            "policy": DEFAULT_DISPATCH_POLICY,
            "reason": "LetUen compositions are sidecar outputs by default; existing user skill triggers remain primary.",
        },
        "outputs": [
            {
                "path": _default_output_path(output_path, output_kind),
                "kind": output_kind,
                "destructive": False,
                "reversible": True,
            }
        ],
        "solidification": {
            "requested": composition_form in {"full_workflow_blueprint", "new_skill_spec"},
            "reason": _solidification_reason(composition_form),
            "approved": False,
        },
        "next_steps": _next_steps(composition_form, selected),
    }
    if output_path:
        write_json(output_path, plan)
    return plan


def _read_request(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        loaded = json.loads(path.read_text(encoding="utf-8"))
    else:
        loaded = parse_simple_yaml(path)
    if not isinstance(loaded, dict):
        raise ValueError("Composition request must decode to an object.")
    return loaded


def _rejection_reason(
    *,
    anchor: dict[str, Any],
    selected_types: set[str],
    selected_sources: set[str],
    excluded_sources: set[str],
    allowed_side_effects: set[str],
    composition_form: str,
) -> str | None:
    anchor_type = str(anchor.get("anchor_type") or "")
    source_skill_id = str(anchor.get("source_skill_id") or "")
    if selected_sources and source_skill_id not in selected_sources:
        return "source skill is not selected"
    if source_skill_id in excluded_sources:
        return "source skill is explicitly excluded"
    if selected_types and anchor_type not in selected_types:
        return "anchor type is not requested for this composition"
    side_effect = str(_nested_value(anchor, "harness_contract", "side_effects", default="none"))
    if side_effect not in allowed_side_effects:
        return f"side effect '{side_effect}' is not allowed"
    reuse_modes = set(anchor.get("reuse_modes") or [])
    if composition_form not in reuse_modes and not _compatible_reuse_mode(composition_form, reuse_modes):
        return f"anchor does not support composition form '{composition_form}'"
    return None


def _compatible_reuse_mode(composition_form: str, reuse_modes: set[str]) -> bool:
    if composition_form == "temporary_composition":
        return bool(reuse_modes & {"workflow_step", "quality_gate", "prompt_fragment"})
    if composition_form == "learning_note":
        return "reference_only" in reuse_modes
    if composition_form == "prompt_patch":
        return "prompt_fragment" in reuse_modes
    return False


def _selection_reason(anchor: dict[str, Any], composition_form: str) -> str:
    anchor_type = str(anchor.get("anchor_type") or "anchor")
    return f"Selected {anchor_type} because it matches the requested {composition_form} form and passes side-effect constraints."


def _evidence_confidence(anchor: dict[str, Any]) -> str:
    evidence = anchor.get("source_evidence") or anchor.get("evidence") or []
    confidences = [str(item.get("confidence")) for item in evidence if isinstance(item, dict) and item.get("confidence")]
    if "high" in confidences:
        return "high"
    if "medium" in confidences:
        return "medium"
    if "low" in confidences:
        return "low"
    return str(anchor.get("confidence") or "unknown")


def _nested_value(data: dict[str, Any], first: str, second: str, *, default: Any) -> Any:
    value = data.get(first)
    if isinstance(value, dict):
        return value.get(second, default)
    return default


def _select_reuse_mode(anchor: dict[str, Any], composition_form: str) -> str:
    reuse_modes = list(anchor.get("reuse_modes") or [])
    if composition_form in reuse_modes:
        return composition_form
    for candidate in ["quality_gate", "workflow_step", "prompt_fragment", "temporary_composition", "reference_only"]:
        if candidate in reuse_modes:
            return candidate
    return "reference_only"


def _build_compatibility_matrix(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    matrix: list[dict[str, Any]] = []
    for index, left in enumerate(selected):
        for right in selected[index + 1 :]:
            matrix.append(
                {
                    "left_anchor": left["anchor_id"],
                    "right_anchor": right["anchor_id"],
                    "compatibility": "compatible",
                    "notes": "Selected anchors passed deterministic type, source, reuse-mode, and side-effect filters.",
                }
            )
    return matrix


def _preferred_output_kind(preferred_outputs: list[Any], composition_form: str) -> str:
    values = [str(item) for item in preferred_outputs]
    if "markdown" in values:
        return "prompt_patch" if composition_form in {"temporary_composition", "prompt_patch"} else "learning_note"
    if "json" in values:
        return "composition_plan"
    return values[0] if values else "composition_plan"


def _default_output_path(output_path: Path | None, output_kind: str) -> str:
    if output_path:
        return str(output_path.with_name(f"{output_path.stem}.{output_kind}.md"))
    return f"composition.{output_kind}.md"


def _request_id(anchors_path: Path, composition_form: str) -> str:
    return f"{anchors_path.stem}-{composition_form}"


def _solidification_reason(composition_form: str) -> str:
    if composition_form in {"full_workflow_blueprint", "new_skill_spec"}:
        return "The requested composition form requires an explicit persistent artifact, but approval is still false by default."
    return "The requested composition form is lightweight and does not require workflow solidification."


def _next_steps(composition_form: str, selected: list[dict[str, Any]]) -> list[str]:
    if not selected:
        return ["Review rejected anchors and loosen source, type, reuse-mode, or side-effect constraints."]
    if composition_form in {"full_workflow_blueprint", "new_skill_spec"}:
        return ["Review the dry-run plan before generating persistent artifacts.", "Keep existing user skills unchanged unless explicit approval is given."]
    return ["Use selected anchors as a temporary sidecar plan.", "Persist or solidify only if the user explicitly asks for it."]
