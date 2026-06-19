from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from .agents import (
    render_mocs,
    render_pattern_notes,
    render_skill_note,
    render_source_note,
    run_pattern_miner,
    run_reviewer,
    run_structure_analyst,
    run_workflow_analyst,
)
from .collectors.inventory import collect_inventory
from .config import RuntimeConfig, load_sources
from .context import build_skill_context
from .env import load_dotenv
from .jsonio import read_json, write_json
from .providers import AnthropicProvider, MockProvider, OpenAIProvider
from .schemas import validate_named_schema
from .state import RunState, new_run_id, utc_now


def run_harness(
    config: RuntimeConfig,
    provider_override: str | None = None,
    resume_dir: Path | None = None,
    limit_skills: int | None = None,
) -> Path:
    load_dotenv(config.path.parent / ".env")
    provider_type = provider_override or config.default_provider
    provider = build_provider(provider_type, config)

    resume = resume_dir is not None
    run_id = resume_dir.name if resume_dir else new_run_id()
    run_dir = resume_dir if resume_dir else config.path.parent / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    state = RunState(run_dir, run_id)
    state.write()

    write_json(
        run_dir / "run.json",
        {
            "run_id": run_id,
            "created_at": utc_now(),
            "status": "resuming" if resume else "running",
            "language": config.language,
            "config_file": str(config.path),
            "sources_file": str(config.sources_file),
            "provider": provider_type,
            "model": config.default_model,
        },
    )
    if config.path.resolve() != (run_dir / "config.resolved.yaml").resolve():
        shutil.copyfile(config.path, run_dir / "config.resolved.yaml")

    sources = load_sources(config.sources_file)
    write_json(run_dir / "sources.lock.json", {"sources": sources, "locked_at": utc_now()})

    state.set_stage("collector", "running")
    source_inventories = []
    rendered_source_inventories = []
    all_packages = []
    for source in sources:
        source_value = source.get("url") or source.get("path")
        if not source_value:
            continue
        if source.get("path") and not source.get("url"):
            source_value = str((config.path.parent / str(source_value)).resolve())
        inventory = collect_inventory(
            str(source_value),
            source.get("ref"),
            config.path.parent / ".cache" / "sources",
        )
        source_name = inventory["source"]["name"]
        source_inventory_path = run_dir / "sources" / source_name / "inventory.json"
        write_json(source_inventory_path, inventory)
        source_inventories.append({"name": source_name, "path": str(source_inventory_path.relative_to(run_dir))})
        rendered_source_inventories.append(inventory)
        render_source_note(config.vault_path, inventory)
        for package in inventory["skill_packages"]:
            package["source_name"] = source_name
            package["source_inventory_path"] = str(source_inventory_path.relative_to(run_dir))
            all_packages.append((inventory, package))

    total_discovered_packages = len(all_packages)
    limit_warning = None
    if limit_skills is not None and limit_skills >= 0:
        all_packages = all_packages[:limit_skills]
        if total_discovered_packages > len(all_packages):
            limit_warning = f"Limited analysis to {len(all_packages)} of {total_discovered_packages} discovered skill package(s)."

    aggregate_inventory = {
        "schema_version": 1,
        "source": {
            "name": "aggregate",
            "type": "multi",
            "url": None,
            "path": None,
            "ref": None,
            "resolved_commit": None,
            "fetched_at": utc_now(),
            "license": None,
        },
        "repository": {
            "root_path": str(config.path.parent),
            "readme_path": "README.md" if (config.path.parent / "README.md").exists() else None,
            "license_path": None,
            "total_files_scanned": sum(len(item[0]["skill_packages"]) for item in all_packages),
        },
        "skill_packages": [package for _, package in all_packages],
        "source_inventories": source_inventories,
        "warnings": [warning for warning in [limit_warning] if warning]
        or ([] if all_packages else ["No SKILL.md files found in configured sources."]),
    }
    validate_named_schema(aggregate_inventory, "inventory.schema.json")
    write_json(run_dir / "inventory.json", aggregate_inventory)
    state.set_stage("collector", "completed")
    state.set_status("INVENTORY_BUILT")

    skill_summaries: list[dict[str, Any]] = []
    for inventory, package in all_packages:
        skill_dir = run_dir / "skills" / package["id"]
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_context = build_skill_context(inventory, package)
        write_json(
            skill_dir / "source_snapshot.json",
            {"source": inventory["source"], "skill_package": package, "skill_context": skill_context},
        )

        state.set_skill_stage(package["id"], "structure_analyst", "running")
        structure = run_structure_analyst(provider, run_dir, inventory, package, skill_context, config.default_model, resume)
        state.set_skill_stage(package["id"], "structure_analyst", "completed")

        state.set_skill_stage(package["id"], "workflow_analyst", "running")
        workflow = run_workflow_analyst(provider, run_dir, package, structure, skill_context, config.default_model, resume)
        state.set_skill_stage(package["id"], "workflow_analyst", "completed")

        state.set_skill_stage(package["id"], "reviewer", "running")
        review = run_reviewer(
            provider,
            run_dir,
            package["id"],
            {"structure": structure, "workflow": workflow},
            config.default_model,
            resume,
        )
        state.set_skill_stage(package["id"], "reviewer", "completed")

        render_skill_note(config.vault_path, package, structure, workflow, review)
        skill_summaries.append({"skill_id": package["id"], "source_path": package["skill_md_path"]})

    state.set_stage("skill_agents", "completed")
    state.set_status("SKILLS_ANALYZED")

    state.set_stage("pattern_miner", "running")
    patterns = run_pattern_miner(provider, run_dir, skill_summaries, config.default_model, resume)
    render_pattern_notes(config.vault_path, patterns)
    render_mocs(
        config.vault_path,
        [inventory["source"] for inventory in rendered_source_inventories],
        [package for _, package in all_packages],
        patterns,
    )
    state.set_stage("pattern_miner", "completed")
    state.set_status("PATTERNS_MINED")

    generated_notes = [build_note_manifest_entry(config.vault_path, path) for path in sorted(config.vault_path.rglob("*.md"))]
    render_manifest = {
        "generated_notes": generated_notes,
        "generated_note_count": len(generated_notes),
        "patterns_count": len(patterns.get("patterns", [])),
        "generated_at": utc_now(),
    }
    write_json(run_dir / "render" / "render_manifest.json", render_manifest)
    state.set_stage("asset_builder", "completed")
    state.set_status("COMPLETED")
    run_metadata_path = run_dir / "run.json"
    run_metadata = read_json(run_metadata_path) if run_metadata_path.exists() else {"run_id": run_id}
    run_metadata.update({"completed_at": utc_now(), "status": "completed"})
    write_json(run_metadata_path, run_metadata)
    return run_dir


def resume_harness(run_dir: Path, provider_override: str | None = None, limit_skills: int | None = None) -> Path:
    config_path = run_dir / "config.resolved.yaml"
    run_metadata_path = run_dir / "run.json"
    if run_metadata_path.exists():
        original_config_path = Path(read_json(run_metadata_path).get("config_file", ""))
        if original_config_path.exists():
            config_path = original_config_path
    if not config_path.exists():
        raise FileNotFoundError(f"Cannot resume without a readable config file for run: {run_dir}")
    from .config import load_config

    config = load_config(config_path)
    return run_harness(config, provider_override=provider_override, resume_dir=run_dir, limit_skills=limit_skills)


def build_provider(provider_type: str, config: RuntimeConfig):
    if provider_type == "mock":
        return MockProvider()
    if provider_type == "openai":
        settings = config.provider_settings("default")
        return OpenAIProvider(
            base_url=settings.get("base_url", "https://api.openai.com/v1"),
            api_key_env=settings.get("api_key_env", "OPENAI_API_KEY"),
            api_mode=settings.get("api_mode", "responses"),
        )
    if provider_type == "anthropic":
        settings = config.provider_settings("default")
        return AnthropicProvider(
            base_url=settings.get("base_url", "https://api.anthropic.com/v1"),
            api_key_env=settings.get("api_key_env", "ANTHROPIC_API_KEY"),
        )
    raise ValueError(f"Unsupported provider type: {provider_type}")


def build_note_manifest_entry(vault_path: Path, path: Path) -> dict[str, str]:
    relative = path.relative_to(vault_path).as_posix()
    first_part = relative.split("/", 1)[0]
    note_type = {
        "00 Maps": "moc",
        "01 Sources": "source",
        "02 Skills": "skill",
        "03 Patterns": "pattern",
        "04 Reusable Assets": "asset",
        "05 Comparisons": "comparison",
        "99 System": "system",
    }.get(first_part, "unknown")
    return {"path": relative, "note_type": note_type}
