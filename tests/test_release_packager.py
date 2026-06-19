from __future__ import annotations

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from asa.release_packager import package_letuen_skill_pack
from asa.cli import main


class ReleasePackagerTest(unittest.TestCase):
    def test_package_letuen_skill_pack_writes_real_release_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "release"

            manifest = package_letuen_skill_pack(output_dir, version="v0.2.0-dev-test")

            root = output_dir / "letuen-skill-anchor-pack"
            self.assertTrue((root / "SKILL.md").exists())
            self.assertTrue((root / "skills" / "asa-anchor-composition-planner" / "SKILL.md").exists())
            self.assertTrue((root / "EVIDENCE_REPAIR.md").exists())
            self.assertTrue((root / "PACK_MANIFEST.json").exists())
            self.assertTrue((root / "INSTALL_CHECK.md").exists())
            self.assertEqual(manifest["skill_count"], 9)
            self.assertEqual(manifest["version"], "v0.2.0-dev-test")
            self.assertIn("asa-evidence-grounding-auditor", manifest["skills"])
            self.assertTrue((output_dir / "letuen-skill-anchor-pack-v0.2.0-dev-test.zip").exists())
            self.assertTrue((output_dir / "letuen-skill-anchor-pack-v0.2.0-dev-test.tar.gz").exists())
            self.assertTrue((output_dir / "SHA256SUMS.txt").exists())

            with zipfile.ZipFile(output_dir / "letuen-skill-anchor-pack-v0.2.0-dev-test.zip") as archive:
                names = set(archive.namelist())
            self.assertIn("letuen-skill-anchor-pack/SKILL.md", names)
            self.assertIn("letuen-skill-anchor-pack/PACK_MANIFEST.json", names)
            self.assertIn("letuen-skill-anchor-pack/skills/asa-workflow-trace-builder/SKILL.md", names)

            pack_manifest = json.loads((root / "PACK_MANIFEST.json").read_text(encoding="utf-8"))
            self.assertEqual(pack_manifest["skill_count"], 9)
            self.assertTrue(pack_manifest["non_destructive_by_default"])

    def test_cli_package_letuen_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "release"

            exit_code = main(["package-letuen-skill", "--output", str(output_dir), "--version", "v0.2.0-dev-test"])

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "letuen-skill-anchor-pack-v0.2.0-dev-test.zip").exists())
            self.assertTrue((output_dir / "letuen-skill-anchor-pack" / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
