from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.evidence_repair import repair_run_evidence, repair_evidence_in_artifact
from asa.quality.rules import check_workflow_quality


class EvidenceRepairTest(unittest.TestCase):
    def test_repairs_paraphrased_quote_to_exact_source_line(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "SKILL.md"
            source.write_text("### Step\n**CRITICAL STEP**: Before implementing the algorithm, identify the subtle conceptual thread from the original request.\n", encoding="utf-8")
            workflow = {
                "workflow_steps": [
                    {
                        "id": "step_1",
                        "confidence": "high",
                        "inferred": False,
                        "actor": "model",
                        "step_type": "execute",
                        "evidence": [
                            {
                                "source_path": "SKILL.md",
                                "quote": "CRITICAL STEP: Before implementing the algorithm, identify the subtle conceptual thread from the original request.",
                                "evidence_type": "explicit",
                            }
                        ],
                    }
                ]
            }

            repaired, changes = repair_evidence_in_artifact(workflow, root)

            quote = repaired["workflow_steps"][0]["evidence"][0]["quote"]
            self.assertEqual(quote, "**CRITICAL STEP**: Before implementing the algorithm, identify the subtle conceptual thread from the original request.")
            self.assertTrue(any(change["code"] == "QUOTE_REPAIRED" for change in changes))
            self.assertNotIn("EVIDENCE_QUOTE_NOT_FOUND", {issue["code"] for issue in check_workflow_quality(repaired, root)})

    def test_downgrades_unrepairable_explicit_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "SKILL.md").write_text("Only unrelated text is present.", encoding="utf-8")
            workflow = {
                "workflow_steps": [
                    {
                        "id": "step_1",
                        "confidence": "high",
                        "inferred": False,
                        "actor": "model",
                        "step_type": "execute",
                        "evidence": [
                            {
                                "source_path": "SKILL.md",
                                "quote": "Missing fabricated quote",
                                "evidence_type": "explicit",
                            }
                        ],
                    }
                ]
            }

            repaired, changes = repair_evidence_in_artifact(workflow, root)
            step = repaired["workflow_steps"][0]
            evidence = step["evidence"][0]

            self.assertTrue(step["inferred"])
            self.assertEqual(step["confidence"], "medium")
            self.assertEqual(evidence["evidence_type"], "inferred")
            self.assertIn("could not be matched", evidence["notes"])
            self.assertTrue(any(change["code"] == "EVIDENCE_DOWNGRADED" for change in changes))

    def test_repairs_run_artifacts_and_writes_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir) / "run"
            source_root = Path(temp_dir) / "source"
            skill_dir = run_dir / "skills" / "demo-skill"
            skill_dir.mkdir(parents=True)
            source_root.mkdir()
            (source_root / "SKILL.md").write_text("1. **Read** `templates/viewer.html` using the Read tool", encoding="utf-8")
            (run_dir / "sources" / "demo").mkdir(parents=True)
            (run_dir / "inventory.json").write_text(
                '{"skill_packages":[{"id":"demo-skill","source_name":"demo","skill_md_path":"SKILL.md"}],"source_inventories":[{"source":{"name":"demo"},"repository":{"root_path":"' + str(source_root).replace('\\', '\\\\') + '"}}]}',
                encoding="utf-8",
            )
            (skill_dir / "workflow_analysis.json").write_text(
                '{"schema_version":1,"skill_id":"demo-skill","workflow_summary":{"zh":"演示","en":"Demo"},"workflow_steps":[{"id":"s1","name":{"zh":"读","en":"Read"},"action":{"zh":"读","en":"Read"},"step_type":"load_context","actor":"model","confidence":"high","inferred":false,"evidence":[{"source_path":"SKILL.md","quote":"Read templates/viewer.html using the Read tool","evidence_type":"explicit"}]}]}',
                encoding="utf-8",
            )

            report = repair_run_evidence(run_dir)

            self.assertEqual(report["artifact_count"], 1)
            self.assertEqual(report["change_count"], 1)
            self.assertTrue((run_dir / "evidence_repair_report.json").exists())


if __name__ == "__main__":
    unittest.main()
