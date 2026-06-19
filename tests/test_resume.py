from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from asa.agent_call import generate_or_reuse_validated_json


class CountingProvider:
    def __init__(self) -> None:
        self.calls = 0

    def generate_json(self, **kwargs: Any) -> dict[str, Any]:
        self.calls += 1
        return {"schema_version": 1}


VALID_REVIEW = """{
  "schema_version": 1,
  "skill_id": "demo",
  "status": "needs_revision",
  "scores": {
    "evidence_score": 1,
    "structure_score": 1,
    "workflow_score": 1,
    "pattern_score": 1,
    "bilingual_score": 1,
    "obsidian_score": 1
  },
  "issues": [],
  "unsupported_claims": [],
  "missing_evidence": [],
  "over_inference": [],
  "approved_for_publish": {"value": false, "rationale": "demo"}
}
"""


class ResumeTest(unittest.TestCase):
    def test_reuses_existing_valid_artifact_without_provider_call(self) -> None:
        provider = CountingProvider()
        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "review_report.json"
            artifact_path.write_text(VALID_REVIEW, encoding="utf-8")
            output = generate_or_reuse_validated_json(
                provider=provider,
                system_prompt="Return JSON.",
                user_payload={"task": "review_report"},
                schema_name="review-report.schema.json",
                artifact_path=artifact_path,
                model="mock",
                resume=True,
            )

        self.assertEqual(output["skill_id"], "demo")
        self.assertEqual(provider.calls, 0)


if __name__ == "__main__":
    unittest.main()

