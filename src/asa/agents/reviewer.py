from __future__ import annotations

from pathlib import Path

from asa.agent_call import generate_or_reuse_validated_json
from asa.providers import ModelProvider
from asa.meta_skills import build_meta_skill_context
from asa.resources import load_prompt


def run_reviewer(
    provider: ModelProvider,
    run_dir: Path,
    skill_id: str,
    artifacts: dict,
    model: str = "mock",
    resume: bool = False,
) -> dict:
    return generate_or_reuse_validated_json(
        provider=provider,
        system_prompt=build_meta_skill_context(load_prompt("reviewer.md"), "reviewer"),
        user_payload={"task": "review_report", "skill_id": skill_id, "artifacts": artifacts},
        schema_name="review-report.schema.json",
        artifact_path=run_dir / "skills" / skill_id / "review_report.json",
        model=model,
        resume=resume,
    )
