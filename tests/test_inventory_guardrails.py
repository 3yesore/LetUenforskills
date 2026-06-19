from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.collectors.inventory import collect_inventory


class InventoryGuardrailTest(unittest.TestCase):
    def test_internal_meta_skills_are_excluded_from_skill_packages(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            internal_root = root / "skills" / "asa-resource-role-analyzer"
            public_root = root / "skills" / "public-skill"
            internal_root.mkdir(parents=True)
            public_root.mkdir(parents=True)
            (internal_root / "SKILL.md").write_text(
                "---\n"
                "name: asa-resource-role-analyzer\n"
                "internal_meta_skill: true\n"
                "---\n"
                "# Internal analyzer\n",
                encoding="utf-8",
            )
            (public_root / "SKILL.md").write_text(
                "---\n"
                "name: public-skill\n"
                "description: Public target skill.\n"
                "---\n"
                "# Public skill\n",
                encoding="utf-8",
            )

            inventory = collect_inventory(str(root), None, root / ".cache")

        package_paths = [package["skill_md_path"] for package in inventory["skill_packages"]]
        self.assertEqual(package_paths, ["skills/public-skill/SKILL.md"])
        self.assertIn("Excluded 1 internal meta-skill", inventory["warnings"])

    def test_asa_prefixed_skill_directories_are_excluded_as_guardrail(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            internal_root = root / "skills" / "asa-workflow-trace-builder"
            internal_root.mkdir(parents=True)
            (internal_root / "SKILL.md").write_text("# Internal analyzer\n", encoding="utf-8")

            inventory = collect_inventory(str(root), None, root / ".cache")

        self.assertEqual(inventory["skill_packages"], [])
        self.assertIn("No SKILL.md files found.", inventory["warnings"])
        self.assertIn("Excluded 1 internal meta-skill", inventory["warnings"])

    def test_all_project_internal_meta_skills_are_excluded_from_local_discovery(self) -> None:
        inventory = collect_inventory(".", None, Path(".cache") / "test-sources")

        internal_paths = [
            package["skill_md_path"]
            for package in inventory["skill_packages"]
            if package["skill_md_path"].startswith("skills/asa-")
        ]
        self.assertEqual(internal_paths, [])
        expected_count = len([path for path in Path("skills").glob("asa-*/SKILL.md")])
        self.assertIn(f"Excluded {expected_count} internal meta-skills", inventory["warnings"])


    def test_release_unpack_directory_is_excluded_from_local_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            live_skill = root / "skills" / "asa-workflow-trace-builder"
            unpacked_skill = root / "releases" / "letuen-skill-anchor-pack" / "skills" / "asa-workflow-trace-builder"
            live_skill.mkdir(parents=True)
            unpacked_skill.mkdir(parents=True)
            (live_skill / "SKILL.md").write_text("# Internal analyzer\n", encoding="utf-8")
            (unpacked_skill / "SKILL.md").write_text("# Unpacked release copy\n", encoding="utf-8")

            inventory = collect_inventory(str(root), None, root / ".cache")

        self.assertIn("Excluded 1 internal meta-skill", inventory["warnings"])
if __name__ == "__main__":
    unittest.main()


