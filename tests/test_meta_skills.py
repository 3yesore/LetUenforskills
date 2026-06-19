from __future__ import annotations

import unittest

from asa.meta_skills import AGENT_META_SKILLS, build_meta_skill_context, load_meta_skill, load_meta_skill_context


class MetaSkillLoaderTest(unittest.TestCase):
    def test_load_meta_skill_returns_internal_method_text(self) -> None:
        text = load_meta_skill("asa-skill-identity-decomposer")

        self.assertIn("internal_meta_skill: true", text)
        self.assertIn("asa-skill-identity-decomposer", text)

    def test_structure_agent_context_loads_identity_and_boundary_methods(self) -> None:
        context = load_meta_skill_context("structure_analyst")

        self.assertIn("asa-skill-identity-decomposer", context)
        self.assertIn("asa-trigger-boundary-mapper", context)
        self.assertNotIn("asa-workflow-trace-builder", context)

    def test_build_meta_skill_context_appends_to_prompt(self) -> None:
        prompt = build_meta_skill_context("Base prompt", "workflow_analyst")

        self.assertTrue(prompt.startswith("Base prompt"))
        self.assertIn("Internal decomposition method skills", prompt)
        self.assertIn("asa-workflow-trace-builder", prompt)

    def test_all_mapped_meta_skills_exist_and_are_internal(self) -> None:
        skill_names = sorted({name for names in AGENT_META_SKILLS.values() for name in names})

        self.assertEqual(len(skill_names), 8)
        for skill_name in skill_names:
            text = load_meta_skill(skill_name)
            self.assertIn(f"name: {skill_name}", text)
            self.assertIn("internal_meta_skill: true", text)
            self.assertIn("# ASA", text)

    def test_reviewer_and_pattern_agents_use_specialized_methods(self) -> None:
        reviewer_context = load_meta_skill_context("reviewer")
        pattern_context = load_meta_skill_context("pattern_miner")
        benchmark_context = load_meta_skill_context("benchmark")

        self.assertIn("asa-evidence-grounding-auditor", reviewer_context)
        self.assertIn("asa-reuse-pattern-miner", pattern_context)
        self.assertIn("asa-model-comparison-judge", benchmark_context)


if __name__ == "__main__":
    unittest.main()
