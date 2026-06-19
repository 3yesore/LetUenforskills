from __future__ import annotations

from pathlib import Path

from asa.agent_call import generate_or_reuse_validated_json
from asa.providers import ModelProvider
from asa.meta_skills import build_meta_skill_context
from asa.resources import load_prompt


def run_structure_analyst(
    provider: ModelProvider,
    run_dir: Path,
    inventory: dict,
    package: dict,
    skill_context: dict,
    model: str = "mock",
    resume: bool = False,
) -> dict:
    return generate_or_reuse_validated_json(
        provider=provider,
        system_prompt=build_meta_skill_context(load_prompt("structure-analyst.md"), "structure_analyst"),
        user_payload={
            "task": "structure_analysis",
            "source": inventory["source"],
            "skill_package": package,
            "skill_context": skill_context,
        },
        schema_name="structure-analysis.schema.json",
        artifact_path=run_dir / "skills" / package["id"] / "structure_analysis.json",
        model=model,
        resume=resume,
    )
