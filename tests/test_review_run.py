from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.jsonio import write_json
from asa.review_summary import summarize_run_reviews


REVIEW = {
    "schema_version": 1,
    "skill_id": "demo",
    "status": "needs_revision",
    "scores": {
        "evidence_score": 2,
        "structure_score": 3,
        "workflow_score": 4,
        "pattern_score": 1,
        "bilingual_score": 5,
        "obsidian_score": 4,
    },
    "issues": [{"severity": "major", "category": "evidence"}],
    "unsupported_claims": [{"claim": "x"}],
    "missing_evidence": [{"field": "workflow_steps"}],
    "over_inference": [],
    "approved_for_publish": {"value": False, "rationale": "demo"},
}


class ReviewRunTest(unittest.TestCase):
    def test_summarizes_review_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = Path(temp_dir)
            skill_dir = run_dir / "skills" / "demo"
            write_json(skill_dir / "review_report.json", REVIEW)

            summary = summarize_run_reviews(run_dir)

        self.assertEqual(summary["reviewed_skill_count"], 1)
        self.assertEqual(summary["status_counts"], {"needs_revision": 1})
        self.assertEqual(summary["average_scores"]["evidence_score"], 2)
        self.assertEqual(summary["totals"]["unsupported_claims"], 1)
        self.assertFalse(summary["skills"][0]["approved_for_publish"])


if __name__ == "__main__":
    unittest.main()

