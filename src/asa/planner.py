from __future__ import annotations

from pathlib import Path
from typing import Any

from .collectors.inventory import collect_inventory
from .config import RuntimeConfig, load_sources
from .state import utc_now


PER_SKILL_AGENT_CALLS = ["structure_analyst", "workflow_analyst", "reviewer"]
RUN_LEVEL_AGENT_CALLS = ["pattern_miner"]


def plan_run(config: RuntimeConfig, limit_skills: int | None = None) -> dict[str, Any]:
    sources = load_sources(config.sources_file)
    discovered_packages: list[dict[str, Any]] = []
    source_summaries: list[dict[str, Any]] = []

    for source in sources:
        source_value = source.get("url") or source.get("path")
        if not source_value:
            continue
        if source.get("path") and not source.get("url"):
            source_value = str((config.path.parent / str(source_value)).resolve())
        inventory = collect_inventory(str(source_value), source.get("ref"), config.path.parent / ".cache" / "sources")
        source_summaries.append(
            {
                "name": inventory["source"]["name"],
                "type": inventory["source"]["type"],
                "url": inventory["source"].get("url"),
                "acquisition_method": inventory["source"].get("acquisition_method"),
                "skill_count": len(inventory["skill_packages"]),
            }
        )
        for package in inventory["skill_packages"]:
            discovered_packages.append(
                {
                    "id": package["id"],
                    "name": package["name"],
                    "skill_md_path": package["skill_md_path"],
                    "source_name": inventory["source"]["name"],
                }
            )

    selected_packages = discovered_packages
    limit_applied = False
    if limit_skills is not None and limit_skills >= 0:
        selected_packages = discovered_packages[:limit_skills]
        limit_applied = len(selected_packages) < len(discovered_packages)

    estimated_agent_calls = len(selected_packages) * len(PER_SKILL_AGENT_CALLS)
    if selected_packages:
        estimated_agent_calls += len(RUN_LEVEL_AGENT_CALLS)

    return {
        "planned_at": utc_now(),
        "config_file": str(config.path),
        "sources_file": str(config.sources_file),
        "provider": config.default_provider,
        "model": config.default_model,
        "sources": source_summaries,
        "discovered_skill_count": len(discovered_packages),
        "selected_skill_count": len(selected_packages),
        "limit_skills": limit_skills,
        "limit_applied": limit_applied,
        "per_skill_agent_calls": PER_SKILL_AGENT_CALLS,
        "run_level_agent_calls": RUN_LEVEL_AGENT_CALLS if selected_packages else [],
        "estimated_agent_calls": estimated_agent_calls,
        "selected_skills": selected_packages,
    }

