from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.cli import init_evaluation_folder, main


class InitEvaluationTest(unittest.TestCase):
    def test_init_evaluation_folder_writes_request_and_review_template(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = init_evaluation_folder("Demo Skill Repo", "https://github.com/example/demo", Path(temp_dir), "deepseek-v4pro")
            evaluation_dir = Path(result["evaluation_dir"])

            self.assertTrue((evaluation_dir / "composition_request.yaml").exists())
            self.assertTrue((evaluation_dir / "evaluation.md").exists())
            self.assertTrue((evaluation_dir / "source.yaml").exists())
            self.assertIn("temporary_composition", (evaluation_dir / "composition_request.yaml").read_text(encoding="utf-8"))
            self.assertIn("preserve_existing_skill_structure: true", (evaluation_dir / "composition_request.yaml").read_text(encoding="utf-8"))
            self.assertIn("deepseek-v4pro", (evaluation_dir / "evaluation.md").read_text(encoding="utf-8"))

    def test_init_evaluation_cli_uses_safe_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            exit_code = main([
                "init-evaluation",
                "--name",
                "Skill Repo!",
                "--source",
                "./skills",
                "--output",
                temp_dir,
                "--model",
                "mock",
            ])

            self.assertEqual(exit_code, 0)
            self.assertTrue((Path(temp_dir) / "skill-repo" / "evaluation.md").exists())


if __name__ == "__main__":
    unittest.main()
