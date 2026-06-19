from __future__ import annotations

import unittest

from asa.quality.rules import check_structure_quality


class StructureQualityRulesTest(unittest.TestCase):
    def test_flags_target_agents_without_evidence(self) -> None:
        structure = {
            "target_agents": ["claude"],
            "confidence": {"overall": "high"},
            "tools": [],
            "file_anatomy": {"scripts": []},
        }

        issues = check_structure_quality(structure)

        self.assertIn("TARGET_AGENTS_WITHOUT_EVIDENCE", {issue["code"] for issue in issues})

    def test_allows_inferred_target_agents_without_evidence(self) -> None:
        structure = {
            "target_agents": [
                {"name": "AI Coding Agent", "confidence": "medium", "inferred": True, "evidence": []}
            ],
            "confidence": {"overall": "medium"},
            "tools": [],
            "file_anatomy": {"scripts": []},
        }

        issues = check_structure_quality(structure)

        self.assertNotIn("TARGET_AGENTS_WITHOUT_EVIDENCE", {issue["code"] for issue in issues})

    def test_allows_required_filesystem_tool_without_scripts_manifest(self) -> None:
        structure = {
            "target_agents": [],
            "confidence": {"overall": "medium"},
            "tools": [{"name": "Read", "type": "filesystem", "required": True, "evidence": []}],
            "file_anatomy": {"scripts": []},
        }

        issues = check_structure_quality(structure)

        self.assertNotIn("SCRIPT_TOOL_WITHOUT_SCRIPT_MANIFEST", {issue["code"] for issue in issues})

    def test_flags_script_tool_when_scripts_manifest_empty(self) -> None:
        structure = {
            "target_agents": [],
            "confidence": {"overall": "medium"},
            "tools": [{"name": "helper", "type": "cli", "required": True, "evidence": []}],
            "file_anatomy": {"scripts": []},
        }

        issues = check_structure_quality(structure)

        self.assertIn("SCRIPT_TOOL_WITHOUT_SCRIPT_MANIFEST", {issue["code"] for issue in issues})


if __name__ == "__main__":
    unittest.main()


