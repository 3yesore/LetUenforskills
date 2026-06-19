from __future__ import annotations

from .jsonio import read_text
from .paths import project_path


AGENT_META_SKILLS: dict[str, tuple[str, ...]] = {
    "structure_analyst": (
        "asa-skill-identity-decomposer",
        "asa-trigger-boundary-mapper",
        "asa-resource-role-analyzer",
    ),
    "workflow_analyst": (
        "asa-workflow-trace-builder",
        "asa-resource-role-analyzer",
    ),
    "reviewer": (
        "asa-evidence-grounding-auditor",
        "asa-skill-identity-decomposer",
        "asa-trigger-boundary-mapper",
        "asa-workflow-trace-builder",
    ),
    "pattern_miner": (
        "asa-reuse-pattern-miner",
        "asa-skill-identity-decomposer",
        "asa-workflow-trace-builder",
    ),
    "report_exporter": (
        "asa-reader-layer-writer",
    ),
    "vault_exporter": (
        "asa-reader-layer-writer",
        "asa-reuse-pattern-miner",
    ),
    "benchmark": (
        "asa-model-comparison-judge",
    ),
}


def load_meta_skill(name: str) -> str:
    skill_path = project_path("skills", name, "SKILL.md")
    return read_text(skill_path).strip()


def load_meta_skill_context(agent_name: str) -> str:
    skill_names = AGENT_META_SKILLS.get(agent_name, ())
    if not skill_names:
        return ""
    blocks = []
    for skill_name in skill_names:
        blocks.append(f"## {skill_name}\n\n{load_meta_skill(skill_name)}")
    return "\n\n".join(blocks)


def build_meta_skill_context(base_prompt: str, agent_name: str) -> str:
    context = load_meta_skill_context(agent_name)
    if not context:
        return base_prompt
    return (
        f"{base_prompt.rstrip()}\n\n"
        "# Internal decomposition method skills\n\n"
        "Use the following internal Agent Skill Anatomy method skills as analysis procedure. "
        "They guide reasoning only; deterministic source facts and JSON schemas remain authoritative.\n\n"
        f"{context}\n"
    )
