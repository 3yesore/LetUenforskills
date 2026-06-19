from __future__ import annotations

from pathlib import Path

from asa.agent_call import generate_or_reuse_validated_json
from asa.providers import ModelProvider
from asa.meta_skills import build_meta_skill_context
from asa.resources import load_prompt


def run_pattern_miner(
    provider: ModelProvider,
    run_dir: Path,
    skill_summaries: list[dict],
    model: str = "mock",
    resume: bool = False,
) -> dict:
    return generate_or_reuse_validated_json(
        provider=provider,
        system_prompt=build_meta_skill_context(load_prompt("pattern-miner.md"), "pattern_miner"),
        user_payload={"task": "patterns", "skills": skill_summaries},
        schema_name="pattern.schema.json",
        artifact_path=run_dir / "patterns" / "patterns.json",
        model=model,
        resume=resume,
    )
