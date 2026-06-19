from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.quality.rules import check_workflow_quality


class QualityRulesTest(unittest.TestCase):
    def test_flags_high_confidence_step_without_evidence(self) -> None:
        workflow = {
            "workflow_steps": [
                {
                    "id": "step_1",
                    "confidence": "high",
                    "inferred": False,
                    "evidence": [],
                    "actor": "model",
                    "step_type": "execute",
                }
            ]
        }

        issues = check_workflow_quality(workflow, source_root=None)

        self.assertEqual(issues[0]["code"], "HIGH_CONFIDENCE_WITHOUT_EVIDENCE")

    def test_flags_inferred_step_with_high_confidence(self) -> None:
        workflow = {
            "workflow_steps": [
                {
                    "id": "step_1",
                    "confidence": "high",
                    "inferred": True,
                    "evidence": [],
                    "actor": "model",
                    "step_type": "execute",
                }
            ]
        }

        issues = check_workflow_quality(workflow, source_root=None)

        self.assertIn("INFERRED_HIGH_CONFIDENCE", {issue["code"] for issue in issues})

    def test_flags_missing_evidence_source_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            workflow = {
                "workflow_steps": [
                    {
                        "id": "step_1",
                        "confidence": "medium",
                        "inferred": False,
                        "evidence": [
                            {
                                "source_path": "missing/SKILL.md",
                                "quote": "demo",
                                "evidence_type": "explicit",
                            }
                        ],
                        "actor": "model",
                        "step_type": "execute",
                    }
                ]
            }

            issues = check_workflow_quality(workflow, source_root=Path(temp_dir))

        self.assertEqual(issues[0]["code"], "EVIDENCE_SOURCE_NOT_FOUND")

    def test_flags_quote_not_found_in_source_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_file = root / "SKILL.md"
            source_file.write_text("This file contains grounded evidence.", encoding="utf-8")
            workflow = {
                "workflow_steps": [
                    {
                        "id": "step_1",
                        "confidence": "medium",
                        "inferred": False,
                        "evidence": [
                            {
                                "source_path": "SKILL.md",
                                "quote": "not present here",
                                "evidence_type": "explicit",
                            }
                        ],
                        "actor": "model",
                        "step_type": "execute",
                    }
                ]
            }

            issues = check_workflow_quality(workflow, source_root=root)

        self.assertIn("EVIDENCE_QUOTE_NOT_FOUND", {issue["code"] for issue in issues})

    def test_quote_matching_ignores_markdown_markup(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_file = root / "SKILL.md"
            source_file.write_text("1. **Read** `templates/viewer.html` using the Read tool", encoding="utf-8")
            workflow = {
                "workflow_steps": [
                    {
                        "id": "step_1",
                        "confidence": "medium",
                        "inferred": False,
                        "evidence": [
                            {
                                "source_path": "SKILL.md",
                                "quote": "Read templates/viewer.html using the Read tool",
                                "evidence_type": "explicit",
                            }
                        ],
                        "actor": "model",
                        "step_type": "execute",
                    }
                ]
            }

            issues = check_workflow_quality(workflow, source_root=root)

        self.assertNotIn("EVIDENCE_QUOTE_NOT_FOUND", {issue["code"] for issue in issues})

    def test_inferred_notes_accept_optional_wording(self) -> None:
        workflow = {
            "workflow_steps": [
                {
                    "id": "step_1",
                    "confidence": "medium",
                    "inferred": True,
                    "evidence": [
                        {
                            "source_path": "SKILL.md",
                            "quote": "Reference for p5.js best practices",
                            "evidence_type": "inferred",
                            "notes": "Optional resource, not a required step.",
                        }
                    ],
                    "actor": "model",
                    "step_type": "execute",
                }
            ]
        }

        issues = check_workflow_quality(workflow, source_root=None)

        self.assertNotIn("INFERRED_EVIDENCE_NEEDS_NOTES", {issue["code"] for issue in issues})

    def test_inferred_quote_does_not_require_exact_source_match(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source_file = root / "SKILL.md"
            source_file.write_text("Reference for p5.js best practices and code structure principles.", encoding="utf-8")
            workflow = {
                "workflow_steps": [
                    {
                        "id": "step_1",
                        "confidence": "medium",
                        "inferred": True,
                        "evidence": [
                            {
                                "source_path": "SKILL.md",
                                "quote": "Reference for p5.js best practices and code structure principles. ... NOT a pattern menu",
                                "evidence_type": "inferred",
                                "notes": "Optional resource, not a required step.",
                            }
                        ],
                        "actor": "model",
                        "step_type": "execute",
                    }
                ]
            }

            issues = check_workflow_quality(workflow, source_root=root)

        self.assertNotIn("EVIDENCE_QUOTE_NOT_FOUND", {issue["code"] for issue in issues})


if __name__ == "__main__":
    unittest.main()
