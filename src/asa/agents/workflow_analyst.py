from __future__ import annotations

from pathlib import Path

from asa.agent_call import generate_or_reuse_validated_json
from asa.providers import ModelProvider
from asa.meta_skills import build_meta_skill_context
from asa.resources import load_prompt


def run_workflow_analyst(
    provider: ModelProvider,
    run_dir: Path,
    package: dict,
    structure_analysis: dict,
    skill_context: dict,
    model: str = "mock",
    resume: bool = False,
) -> dict:
    return generate_or_reuse_validated_json(
        provider=provider,
        system_prompt=build_meta_skill_context(load_prompt("workflow-analyst.md"), "workflow_analyst"),
        user_payload={
            "task": "workflow_analysis",
            "skill_package": package,
            "structure_analysis": structure_analysis,
            "skill_context": skill_context,
        },
        schema_name="workflow-analysis.schema.json",
        artifact_path=run_dir / "skills" / package["id"] / "workflow_analysis.json",
        model=model,
        resume=resume,
    )
