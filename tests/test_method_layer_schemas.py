from __future__ import annotations

import unittest

from asa.schemas import SchemaValidationError, validate_named_schema


class MethodLayerSchemaTest(unittest.TestCase):
    def test_structure_schema_accepts_identity_activation_and_resource_roles(self) -> None:
        structure = {
            "schema_version": 1,
            "skill_id": "demo",
            "source": {},
            "summary": {"zh": "演示", "en": "Demo"},
            "skill_type": {"primary": "workflow", "secondary": []},
            "confidence": {"overall": "medium", "notes": "grounded"},
            "identity": {
                "one_line": {"zh": "一个演示技能", "en": "A demo skill"},
                "skill_type": {"primary": "workflow", "secondary": []},
                "target_agents": ["codex"],
                "primary_outputs": ["report"],
                "value_proposition": {"zh": "帮助理解", "en": "Helps understanding"},
                "confidence": {"overall": "medium", "notes": "frontmatter"},
                "evidence": [],
            },
            "activation": {
                "explicit_triggers": ["analyze this skill"],
                "semantic_triggers": ["skill decomposition"],
                "negative_triggers": ["general coding"],
                "boundary_conditions": ["needs SKILL.md"],
                "misfire_risks": ["too broad"],
                "evidence": [],
            },
            "resource_roles": [
                {
                    "path": "SKILL.md",
                    "role": "primary instruction",
                    "stage": "read",
                    "read_policy": "must_read",
                    "reuse_value": "high",
                    "risk": "none",
                    "evidence": [],
                }
            ],
        }

        validate_named_schema(structure, "structure-analysis.schema.json")

    def test_structure_schema_rejects_invalid_resource_read_policy(self) -> None:
        structure = {
            "schema_version": 1,
            "skill_id": "demo",
            "source": {},
            "summary": {"zh": "演示", "en": "Demo"},
            "skill_type": {"primary": "workflow"},
            "confidence": {"overall": "medium"},
            "resource_roles": [{"path": "SKILL.md", "read_policy": "always"}],
        }

        with self.assertRaises(SchemaValidationError):
            validate_named_schema(structure, "structure-analysis.schema.json")

    def test_workflow_schema_accepts_workflow_trace(self) -> None:
        workflow = {
            "schema_version": 1,
            "skill_id": "demo",
            "workflow_summary": {"zh": "读取再输出", "en": "Read then deliver"},
            "workflow_steps": [],
            "workflow_trace": {
                "summary": {"zh": "用户意图到报告", "en": "Intent to report"},
                "pipeline": ["detect", "inspect", "deliver"],
                "steps": [
                    {
                        "id": "trace_1",
                        "name": {"zh": "读取技能", "en": "Read skill"},
                        "input": "SKILL.md",
                        "action": "inspect",
                        "output": "notes",
                        "actor": "model",
                        "resources": ["SKILL.md"],
                        "downstream": ["trace_2"],
                        "confidence": "medium",
                        "inferred": False,
                        "evidence": [],
                    }
                ],
                "decision_points": [],
                "verification_points": [],
                "failure_modes": [],
            },
        }

        validate_named_schema(workflow, "workflow-analysis.schema.json")

    def test_review_schema_accepts_evidence_audit(self) -> None:
        review = {
            "schema_version": 1,
            "skill_id": "demo",
            "status": "publishable",
            "scores": {"evidence_score": 5},
            "approved_for_publish": {"value": True, "rationale": "grounded"},
            "evidence_audit": {
                "supported_claims": ["identity"],
                "inferred_claims": [],
                "unsupported_claims": [],
                "missing_evidence": [],
                "conflicts": [],
                "publishable": "publishable",
                "rationale": "Evidence is sufficient.",
            },
        }

        validate_named_schema(review, "review-report.schema.json")

    def test_pattern_schema_accepts_reuse_assets(self) -> None:
        patterns = {
            "schema_version": 1,
            "patterns": [],
            "reuse_assets": {
                "patterns": [],
                "templates": [],
                "checklists": ["Map trigger before workflow"],
                "anti_patterns": [],
                "extension_ideas": [],
            },
        }

        validate_named_schema(patterns, "pattern.schema.json")


if __name__ == "__main__":
    unittest.main()
