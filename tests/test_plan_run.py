from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.config import load_config
from asa.planner import plan_run


CONFIG = """project:
  language: bilingual
providers:
  default:
    type: mock
    model: mock
sources_file: sources.yaml
obsidian:
  vault_path: ./vault
"""


SOURCES = """sources:
  - name: multi-skill
    path: ./skills
    language: bilingual
"""


class PlanRunTest(unittest.TestCase):
    def test_plan_run_counts_skills_and_agent_calls(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "skills" / "one").mkdir(parents=True)
            (root / "skills" / "two").mkdir(parents=True)
            (root / "skills" / "one" / "SKILL.md").write_text("# One", encoding="utf-8")
            (root / "skills" / "two" / "SKILL.md").write_text("# Two", encoding="utf-8")
            config_path = root / "anatomy.config.yaml"
            config_path.write_text(CONFIG, encoding="utf-8")
            (root / "sources.yaml").write_text(SOURCES, encoding="utf-8")

            plan = plan_run(load_config(config_path), limit_skills=1)

        self.assertEqual(plan["discovered_skill_count"], 2)
        self.assertEqual(plan["selected_skill_count"], 1)
        self.assertEqual(plan["estimated_agent_calls"], 4)
        self.assertEqual(plan["selected_skills"][0]["name"], "one")


if __name__ == "__main__":
    unittest.main()

