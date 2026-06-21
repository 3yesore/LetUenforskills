from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.cli import main
from asa.vault_exporter import export_vault

from tests.test_export_report import make_run


class ExportVaultTest(unittest.TestCase):
    def test_exports_obsidian_vault_from_run_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            output_dir = root / "vault"

            manifest = export_vault(run_dir, output_dir)

            self.assertEqual(manifest["skill_count"], 1)
            self.assertTrue((output_dir / "00 Maps" / "Agent Skill Anatomy MOC.md").exists())
            self.assertTrue((output_dir / "02 Skills" / "demo-skill - demo-skill.md").exists())
            self.assertTrue((output_dir / "03 Workflows" / "demo-skill - demo-skill.workflow.md").exists())
            self.assertTrue((output_dir / "00 Maps" / "Skill Anatomy Canvas.canvas").exists())
            self.assertTrue((output_dir / ".obsidian" / "app.json").exists())
            self.assertTrue((output_dir / "00 Maps" / "Skill Index.md").exists())
            self.assertTrue((output_dir / "05 Quality" / "Quality Report.md").exists())
            self.assertTrue((output_dir / "06 Data" / "vault_manifest.json").exists())
            self.assertTrue((output_dir / "Open in Obsidian.html").exists())
            self.assertTrue((output_dir / "Open Agent Skill Anatomy Vault.url").exists())
            self.assertTrue((output_dir / "README - Open in Obsidian.md").exists())
            zip_path = next(output_dir.glob("Agent-Skill-Anatomy-Vault-*.zip"))
            self.assertTrue(zip_path.exists())
            import zipfile
            with zipfile.ZipFile(zip_path) as archive:
                names = set(archive.namelist())
            self.assertIn("vault/.obsidian/app.json", names)
            self.assertNotIn("vault/.obsidian/workspace.json", names)
            manifest_text = (output_dir / "06 Data" / "vault_manifest.json").read_text(encoding="utf-8")
            self.assertIn("Open in Obsidian.html", manifest_text)
            moc_text = (output_dir / "00 Maps" / "Agent Skill Anatomy MOC.md").read_text(encoding="utf-8")
            self.assertIn("Everyone Can Use This", moc_text)
            self.assertIn("Learning Path", moc_text)
            self.assertIn("Reuse Path", moc_text)
            self.assertIn("Review Path", moc_text)
            skill_index_text = (output_dir / "00 Maps" / "Skill Index.md").read_text(encoding="utf-8")
            self.assertIn("How To Read", skill_index_text)
            self.assertIn("Open the skill note first", skill_index_text)
            skill_note = (output_dir / "02 Skills" / "demo-skill - demo-skill.md").read_text(encoding="utf-8")
            self.assertIn("## Learning Brief", skill_note)
            self.assertIn("## Visual Map", skill_note)
            self.assertIn("## Method Layer", skill_note)
            self.assertIn("演示技能用于说明拆解链路", skill_note)
            self.assertIn("must_read", skill_note)
            self.assertIn("## Evidence Audit", skill_note)
            self.assertIn("主指令存在", skill_note)
            self.assertIn("无证据的性能承诺", skill_note)
            self.assertIn("## Reuse Assets", skill_note)
            self.assertIn("入口识别模式", skill_note)
            self.assertIn("只列文件不解释职责", skill_note)
            workflow_note = (output_dir / "03 Workflows" / "demo-skill - demo-skill.workflow.md").read_text(encoding="utf-8")
            self.assertIn("读取技能", workflow_note)
            self.assertIn("## Trace Pipeline", workflow_note)
            self.assertIn("detect → inspect → deliver", workflow_note)
            self.assertIn("## Trace Steps", workflow_note)
            self.assertIn("定位入口", workflow_note)
            self.assertIn("Resources: `SKILL.md`", workflow_note)
            self.assertIn("Downstream: `trace_2`", workflow_note)
            self.assertIn("## Failure Modes", workflow_note)
            self.assertIn("缺少证据", workflow_note)

    def test_cli_export_vault_and_export_all(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            vault_dir = root / "vault"
            dist_dir = root / "dist"

            vault_exit = main(["export-vault", "--run", str(run_dir), "--output", str(vault_dir)])
            all_exit = main(["export-all", "--run", str(run_dir), "--output", str(dist_dir)])

            self.assertEqual(vault_exit, 0)
            self.assertEqual(all_exit, 0)
            self.assertTrue((vault_dir / "00 Maps" / "Agent Skill Anatomy MOC.md").exists())
            self.assertTrue((dist_dir / "report" / "index.html").exists())
            self.assertTrue((dist_dir / "vault" / "06 Data" / "vault_manifest.json").exists())
            self.assertTrue((dist_dir / "vault" / "Open in Obsidian.html").exists())
            self.assertTrue(any((dist_dir / "vault").glob("Agent-Skill-Anatomy-Vault-*.zip")))


if __name__ == "__main__":
    unittest.main()


