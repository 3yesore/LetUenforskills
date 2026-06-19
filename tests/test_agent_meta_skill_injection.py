from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from asa.agents.structure_analyst import run_structure_analyst
from asa.providers.mock import mock_structure_analysis


class CapturingProvider:
    def __init__(self) -> None:
        self.system_prompt = ""

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
        model: str = "mock",
        temperature: float = 0,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        self.system_prompt = system_prompt
        return mock_structure_analysis(user_payload)


class AgentMetaSkillInjectionTest(unittest.TestCase):
    def test_structure_analyst_receives_internal_method_context(self) -> None:
        provider = CapturingProvider()
        inventory = {"source": {"url": None, "resolved_commit": None}}
        package = {
            "id": "demo-skill",
            "name": "demo-skill",
            "root_path": ".",
            "skill_md_path": "SKILL.md",
            "scripts": [],
            "references": [],
            "assets": [],
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            run_structure_analyst(
                provider=provider,
                run_dir=Path(temp_dir),
                inventory=inventory,
                package=package,
                skill_context={"files": []},
                model="mock",
                resume=False,
            )

        self.assertIn("Internal decomposition method skills", provider.system_prompt)
        self.assertIn("asa-skill-identity-decomposer", provider.system_prompt)
        self.assertIn("asa-trigger-boundary-mapper", provider.system_prompt)


if __name__ == "__main__":
    unittest.main()
