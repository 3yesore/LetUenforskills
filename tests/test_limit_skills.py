from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.config import load_config
from asa.jsonio import read_json
from asa.runtime import run_harness


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


class LimitSkillsTest(unittest.TestCase):
    def test_run_harness_limits_number_of_analyzed_skills(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "skills" / "one").mkdir(parents=True)
            (root / "skills" / "two").mkdir(parents=True)
            (root / "skills" / "one" / "SKILL.md").write_text("# One", encoding="utf-8")
            (root / "skills" / "two" / "SKILL.md").write_text("# Two", encoding="utf-8")
            config_path = root / "anatomy.config.yaml"
            config_path.write_text(CONFIG, encoding="utf-8")
            (root / "sources.yaml").write_text(SOURCES, encoding="utf-8")

            run_dir = run_harness(load_config(config_path), limit_skills=1)
            inventory = read_json(run_dir / "inventory.json")

        self.assertEqual(len(inventory["skill_packages"]), 1)


if __name__ == "__main__":
    unittest.main()

