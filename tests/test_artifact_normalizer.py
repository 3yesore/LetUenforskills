from __future__ import annotations

import unittest

from asa.artifact_normalizer import normalize_structure_analysis, normalize_workflow_analysis
from asa.quality.rules import check_structure_quality, check_workflow_quality


class ArtifactNormalizerTest(unittest.TestCase):
    def test_normalizes_tool_strings_to_objects(self) -> None:
        structure = {
            "schema_version": 1,
            "skill_id": "demo",
            "source": {},
            "summary": {"zh": "演示", "en": "Demo"},
            "skill_type": {"primary": "workflow"},
            "tools": ["web_fetch", {"name": "python", "required": True}],
            "confidence": {"overall": "medium"},
        }

        normalized, changes = normalize_structure_analysis(structure)

        self.assertEqual(normalized["tools"][0]["name"], "web_fetch")
        self.assertEqual(normalized["tools"][0]["type"], "unknown")
        self.assertFalse(normalized["tools"][0]["required"])
        self.assertEqual(normalized["tools"][0]["evidence"], [])
        self.assertEqual(normalized["tools"][1]["type"], "unknown")
        self.assertTrue(any(change["code"] == "TOOL_STRING_NORMALIZED" for change in changes))
        self.assertNotIn("TOOL_ITEM_NOT_OBJECT", {issue["code"] for issue in check_structure_quality(normalized)})

    def test_downgrades_target_agents_without_evidence(self) -> None:
        structure = {
            "schema_version": 1,
            "skill_id": "demo",
            "source": {},
            "summary": {"zh": "演示", "en": "Demo"},
            "skill_type": {"primary": "workflow"},
            "target_agents": ["AI Coding Agent"],
            "confidence": {"overall": "high"},
        }

        normalized, changes = normalize_structure_analysis(structure)

        self.assertIsInstance(normalized["target_agents"][0], dict)
        self.assertTrue(normalized["target_agents"][0]["inferred"])
        self.assertEqual(normalized["target_agents"][0]["confidence"], "medium")
        self.assertEqual(normalized["confidence"]["overall"], "medium")
        self.assertTrue(any(change["code"] == "TARGET_AGENT_INFERRED" for change in changes))
        self.assertNotIn("TARGET_AGENTS_WITHOUT_EVIDENCE", {issue["code"] for issue in check_structure_quality(normalized)})

    def test_trims_long_workflow_quotes_and_adds_inferred_notes(self) -> None:
        workflow = {
            "schema_version": 1,
            "skill_id": "demo",
            "workflow_summary": {"zh": "演示", "en": "Demo"},
            "workflow_steps": [
                {
                    "id": "step_1",
                    "name": {"zh": "推断", "en": "Infer"},
                    "action": {"zh": "推断行为", "en": "Infer behavior"},
                    "step_type": "analyze",
                    "actor": "model",
                    "inferred": True,
                    "confidence": "high",
                    "evidence": [
                        {
                            "source_path": "SKILL.md",
                            "quote": "one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo twentythree twentyfour twentyfive twentysix",
                            "evidence_type": "inferred",
                        }
                    ],
                }
            ],
        }

        normalized, changes = normalize_workflow_analysis(workflow)
        step = normalized["workflow_steps"][0]
        evidence = step["evidence"][0]

        self.assertEqual(step["confidence"], "medium")
        self.assertLessEqual(len(evidence["quote"].split()), 25)
        self.assertIn("Inferred", evidence["notes"])
        self.assertTrue(any(change["code"] == "QUOTE_TRIMMED" for change in changes))
        issue_codes = {issue["code"] for issue in check_workflow_quality(normalized, source_root=None)}
        self.assertNotIn("INFERRED_HIGH_CONFIDENCE", issue_codes)
        self.assertNotIn("EVIDENCE_QUOTE_TOO_LONG", issue_codes)
        self.assertNotIn("INFERRED_EVIDENCE_NEEDS_NOTES", issue_codes)

    def test_structure_normalizer_caps_activation_confidence_and_documents_no_tools(self) -> None:
        normalized, changes = normalize_structure_analysis(
            {
                "schema_version": 1,
                "skill_id": "demo",
                "tools": [],
                "activation": {
                    "semantic_triggers": ["demo requests"],
                    "misfire_risks": ["real task confusion"],
                    "confidence": "high",
                },
            }
        )

        self.assertEqual(normalized["activation"]["confidence"], "medium")
        self.assertEqual(normalized["inventory_evidence"]["tools"]["evidence_type"], "deterministic_inventory")
        self.assertIn("ACTIVATION_CONFIDENCE_DOWNGRADED", {change["code"] for change in changes})
        self.assertIn("NO_TOOLS_INVENTORY_EVIDENCE_ADDED", {change["code"] for change in changes})


if __name__ == "__main__":
    unittest.main()
