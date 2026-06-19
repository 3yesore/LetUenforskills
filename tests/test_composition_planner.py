from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.cli import main
from asa.composition_planner import plan_anchor_composition


EXAMPLE_DIR = Path("examples/anchor-composition/sample-skill")


class AnchorCompositionPlannerTest(unittest.TestCase):
    def test_plan_anchor_composition_selects_temporary_safe_response_anchors(self) -> None:
        plan = plan_anchor_composition(
            EXAMPLE_DIR / "anchors.json",
            EXAMPLE_DIR / "composition_request.temporary.yaml",
        )

        selected_ids = {item["anchor_id"] for item in plan["selected_anchors"]}
        rejected_ids = {item["anchor_id"] for item in plan["rejected_anchors"]}

        self.assertEqual(plan["composition_form"], "temporary_composition")
        self.assertIn("anchor.sample-skill.workflow.progressive-read-then-deliver", selected_ids)
        self.assertIn("anchor.sample-skill.boundary.no-destructive-commands", selected_ids)
        self.assertIn("anchor.sample-skill.validation.requested-format-check", selected_ids)
        self.assertIn("anchor.sample-skill.identity.runtime-skeleton-test", rejected_ids)
        self.assertEqual(plan["dispatch_policy"]["policy"], "prefer_existing_skill")
        self.assertEqual(plan["composition"]["form"], "temporary_composition")
        self.assertEqual(plan["composition"]["dispatch_strategy"], "prefer_existing_skill")
        self.assertFalse(plan["solidification"]["requested"])
        self.assertFalse(plan["outputs"][0]["destructive"])

    def test_plan_composition_cli_writes_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "composition_plan.json"

            exit_code = main(
                [
                    "plan-composition",
                    "--anchors",
                    str(EXAMPLE_DIR / "anchors.json"),
                    "--request",
                    str(EXAMPLE_DIR / "composition_request.temporary.yaml"),
                    "--output",
                    str(output_path),
                ]
            )

            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            self.assertIn("temporary_composition", output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
