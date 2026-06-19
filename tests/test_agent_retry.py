from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from typing import Any

from asa.agent_call import generate_validated_json
from asa.jsonio import read_json
from asa.schemas import SchemaValidationError


class FlakyProvider:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def generate_json(self, **kwargs: Any) -> dict[str, Any]:
        self.calls.append(kwargs)
        if len(self.calls) == 1:
            return {"schema_version": 1, "skill_id": "demo"}
        return {
            "schema_version": 1,
            "skill_id": "demo",
            "workflow_summary": {"zh": "演示", "en": "Demo"},
            "workflow_steps": [
                {
                    "id": "step_1",
                    "name": {"zh": "交付", "en": "Deliver"},
                    "action": {"zh": "输出结果", "en": "Deliver result"},
                    "step_type": "deliver",
                    "actor": "model",
                    "evidence": [],
                    "inferred": True,
                    "confidence": "low",
                }
            ],
        }


class AgentRetryTest(unittest.TestCase):
    def test_retries_once_after_schema_validation_failure(self) -> None:
        provider = FlakyProvider()

        with tempfile.TemporaryDirectory() as temp_dir:
            output = generate_validated_json(
                provider=provider,
                system_prompt="Return JSON.",
                user_payload={"task": "workflow_analysis"},
                schema_name="workflow-analysis.schema.json",
                artifact_path=Path(temp_dir) / "workflow_analysis.json",
                model="mock",
                max_attempts=2,
            )

        self.assertEqual(output["skill_id"], "demo")
        self.assertEqual(len(provider.calls), 2)
        retry_payload = provider.calls[1]["user_payload"]
        self.assertIn("previous_validation_error", retry_payload)
        self.assertIn("workflow_summary", retry_payload["previous_validation_error"])

    def test_writes_error_artifact_after_final_validation_failure(self) -> None:
        class AlwaysInvalidProvider:
            def generate_json(self, **kwargs: Any) -> dict[str, Any]:
                return {"schema_version": 1, "skill_id": "demo"}

        with tempfile.TemporaryDirectory() as temp_dir:
            artifact_path = Path(temp_dir) / "workflow_analysis.json"
            with self.assertRaises(SchemaValidationError):
                generate_validated_json(
                    provider=AlwaysInvalidProvider(),
                    system_prompt="Return JSON.",
                    user_payload={"task": "workflow_analysis"},
                    schema_name="workflow-analysis.schema.json",
                    artifact_path=artifact_path,
                    model="mock",
                    max_attempts=1,
                )
            error = read_json(artifact_path.with_suffix(".error.json"))

        self.assertEqual(error["code"], "SCHEMA_VALIDATION_FAILED")
        self.assertTrue(error["recoverable"])


if __name__ == "__main__":
    unittest.main()
