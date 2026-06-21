from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from asa.cli import main

from tests.test_export_report import make_run


class ExportLetUenTest(unittest.TestCase):
    def test_cli_export_letuen_writes_all_surfaces_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            output_dir = root / "letuen"

            exit_code = main(["export-letuen", "--run", str(run_dir), "--output", str(output_dir)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "report" / "index.html").exists())
            self.assertTrue((output_dir / "vault" / "00 Maps" / "Agent Skill Anatomy MOC.md").exists())
            self.assertTrue(any((output_dir / "vault").rglob("*.md")))
            self.assertTrue(any((output_dir / "vault").glob("Agent-Skill-Anatomy-Vault-*.zip")))
            self.assertTrue((output_dir / "data" / "data_manifest.json").exists())
            self.assertTrue((output_dir / "anchors" / "anchors.json").exists())
            manifest = json.loads((output_dir / "letuen_manifest.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(manifest["anchor_count"], 1)
            self.assertIsNone(manifest["composition_plan_path"])

    def test_cli_export_letuen_can_include_composition_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            request_path = root / "request.json"
            output_dir = root / "letuen"
            request_path.write_text(
                '{'
                '"schema_version":1,'
                '"goal":{"type":"temporary_composition","description":"borrow workflow"},'
                '"constraints":{"avoid_full_workflow":true,"preserve_existing_skill_structure":true,"allowed_side_effects":["none"]},'
                '"selected_anchor_types":["workflow_anchor"],'
                '"selected_source_skills":["demo-skill"],'
                '"excluded_source_skills":[],'
                '"preferred_outputs":["json"]'
                '}',
                encoding="utf-8",
            )

            exit_code = main(
                [
                    "export-letuen",
                    "--run",
                    str(run_dir),
                    "--output",
                    str(output_dir),
                    "--composition-request",
                    str(request_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "anchors" / "composition_plan.json").exists())
            manifest = json.loads((output_dir / "letuen_manifest.json").read_text(encoding="utf-8"))
            self.assertIn("composition_plan.json", manifest["composition_plan_path"])
            report_html = (output_dir / "report" / "index.html").read_text(encoding="utf-8")
            self.assertIn("Reusable Anchors", report_html)
            self.assertIn("Composition Plan", report_html)
            self.assertIn("prefer_existing_skill", report_html)
            self.assertTrue((output_dir / "vault" / "00 Maps" / "Anchor Index.md").exists())
            self.assertTrue((output_dir / "vault" / "07 Anchors" / "Composition Plan.md").exists())
            vault_manifest = json.loads((output_dir / "vault" / "06 Data" / "vault_manifest.json").read_text(encoding="utf-8"))
            self.assertGreaterEqual(vault_manifest["anchor_count"], 1)
            self.assertTrue(any(note.startswith("07 Anchors/") for note in vault_manifest["notes"]))


if __name__ == "__main__":
    unittest.main()
