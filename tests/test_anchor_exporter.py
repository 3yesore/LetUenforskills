from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.anchor_exporter import export_anchors
from asa.cli import main
from asa.composition_planner import plan_anchor_composition


RUN_DIR = Path("runs/demo-multi-skill")


class AnchorExporterTest(unittest.TestCase):
    def test_export_anchors_from_demo_run_contains_core_anchor_types(self) -> None:
        document = export_anchors(RUN_DIR)
        anchor_types = {anchor["anchor_type"] for anchor in document["anchors"]}

        self.assertGreaterEqual(document["anchor_count"], 6)
        self.assertIn("identity_anchor", anchor_types)
        self.assertIn("workflow_anchor", anchor_types)
        self.assertIn("evidence_anchor", anchor_types)
        self.assertIn("reuse_anchor", anchor_types)

    def test_export_anchors_cli_writes_planner_compatible_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            anchors_path = root / "anchors.json"
            request_path = root / "request.json"
            plan_path = root / "plan.json"
            request_path.write_text(
                '{'
                '"schema_version":1,'
                '"goal":{"type":"temporary_composition","description":"borrow workflow and validation"},'
                '"constraints":{"avoid_full_workflow":true,"preserve_existing_skill_structure":true,"allowed_side_effects":["none"]},'
                '"selected_anchor_types":["workflow_anchor","validation_anchor"],'
                '"selected_source_skills":["research-skill-research-skill"],'
                '"excluded_source_skills":[],'
                '"preferred_outputs":["json"]'
                '}',
                encoding="utf-8",
            )

            export_exit = main(["export-anchors", "--run", str(RUN_DIR), "--output", str(anchors_path)])
            plan = plan_anchor_composition(anchors_path, request_path, plan_path)

            self.assertEqual(export_exit, 0)
            self.assertTrue(anchors_path.exists())
            self.assertTrue(plan_path.exists())
            self.assertEqual(plan["dispatch_policy"]["policy"], "prefer_existing_skill")
            self.assertTrue(plan["selected_anchors"])


if __name__ == "__main__":
    unittest.main()
