from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.cli import main
from asa.jsonio import write_json
from asa.quality.report import quality_report_for_run
from asa.report_exporter import export_report


STRUCTURE = {
    "schema_version": 1,
    "skill_id": "demo-skill",
    "summary": {"zh": "演示技能结构。", "en": "Demo skill structure."},
    "target_agents": ["codex"],
    "skill_type": {"primary": "workflow", "secondary": []},
    "confidence": {"overall": "medium"},
    "source": {"skill_md_path": "SKILL.md"},
    "identity": {
        "one_line": {"zh": "演示技能用于说明拆解链路。", "en": "Demo skill explains the anatomy path."},
        "primary_outputs": ["report"],
    },
    "activation": {
        "explicit_triggers": ["拆解这个 skill"],
        "negative_triggers": ["普通聊天"],
    },
    "resource_roles": [
        {"path": "SKILL.md", "role": "主指令", "stage": "inspect", "read_policy": "must_read", "reuse_value": "high"}
    ],
}

WORKFLOW = {
    "schema_version": 1,
    "skill_id": "demo-skill",
    "workflow_summary": {"zh": "演示工作流。", "en": "Demo workflow."},
    "workflow_trace": {"pipeline": ["detect", "inspect", "deliver"], "failure_modes": ["缺少证据"], "steps": [{"id": "trace_1", "name": {"zh": "定位入口", "en": "Locate entry"}, "input": "用户请求", "action": "读取 SKILL.md", "output": "结构线索", "actor": "model", "resources": ["SKILL.md"], "downstream": ["trace_2"], "confidence": "medium", "inferred": False, "evidence": []}]},
    "workflow_steps": [
        {
            "id": "step_1",
            "name": {"zh": "读取技能", "en": "Read skill"},
            "action": {"zh": "读取 SKILL.md。", "en": "Read SKILL.md."},
            "confidence": "medium",
            "inferred": False,
        }
    ],
}

REVIEW = {
    "schema_version": 1,
    "skill_id": "demo-skill",
    "status": "approved",
    "scores": {},
    "issues": [],
    "unsupported_claims": [],
    "missing_evidence": [],
    "over_inference": [],
    "approved_for_publish": {"value": True, "rationale": "demo"},
    "evidence_audit": {"publishable": "publishable", "rationale": "证据足够", "supported_claims": ["主指令存在"], "inferred_claims": ["执行顺序来自结构推断"], "unsupported_claims": ["无证据的性能承诺"], "missing_evidence": ["缺少脚本引用"], "conflicts": ["描述与文件结构不一致"]},
}


def make_run(root: Path) -> Path:
    run_dir = root / "runs" / "demo-run"
    write_json(
        run_dir / "inventory.json",
        {
            "skill_packages": [
                {
                    "id": "demo-skill",
                    "name": "demo-skill",
                    "skill_md_path": "SKILL.md",
                    "source_name": "demo-source",
                }
            ],
            "source_inventories": [{"name": "demo-source", "path": "sources/demo-source/inventory.json"}],
        },
    )
    skill_dir = run_dir / "skills" / "demo-skill"
    write_json(skill_dir / "structure_analysis.json", STRUCTURE)
    write_json(skill_dir / "workflow_analysis.json", WORKFLOW)
    write_json(skill_dir / "review_report.json", REVIEW)
    write_json(run_dir / "patterns" / "patterns.json", {"patterns": [], "reuse_assets": {"patterns": ["入口识别模式"], "templates": ["SKILL.md 模板"], "checklists": ["先确认触发边界"], "anti_patterns": ["只列文件不解释职责"], "extension_ideas": ["增加模型对比"]}})
    write_json(run_dir / "quality_report.json", {"checked_skill_count": 1, "issue_count": 0, "severity_counts": {}, "skills": [{"skill_id": "demo-skill", "issue_count": 0}], "issues": [], "publishable_by_rules": True})
    write_json(skill_dir / "source_snapshot.json", {"source": {"name": "demo-source", "path": str(root / "missing-source")}, "skill_package": {"source_name": "demo-source", "skill_md_path": "SKILL.md"}, "skill_context": {"skill_md": {"path": "SKILL.md", "content": "# Demo Skill\n\n读取 SKILL.md。\n"}, "scripts_manifest": [], "references_manifest": [], "assets_manifest": []}})
    write_json(run_dir / "review_summary.json", {"reviewed_skill_count": 1, "status_counts": {"approved": 1}, "average_scores": {}, "totals": {}, "skills": [{"skill_id": "demo-skill", "approved_for_publish": True}]})
    return run_dir


class ExportReportTest(unittest.TestCase):
    def test_exports_static_report_with_skill_page_and_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            output_dir = root / "site" / "report"

            result = export_report(run_dir, output_dir)

            self.assertEqual(result["skill_count"], 1)
            self.assertTrue((output_dir / "index.html").exists())
            self.assertTrue((output_dir / "skills" / "demo-skill.html").exists())
            self.assertTrue((output_dir / "assets" / "report.css").exists())
            self.assertTrue((output_dir / "artifacts" / "skills" / "demo-skill" / "structure_analysis.json").exists())
            index_html = (output_dir / "index.html").read_text(encoding="utf-8")
            self.assertIn("Agent Skill Anatomy Report", index_html)
            self.assertIn("方法层", index_html)
            self.assertIn("演示技能用于说明拆解链路", index_html)
            self.assertIn("SKILL.md", index_html)
            self.assertIn("must_read", index_html)
            self.assertIn("high", index_html)
            self.assertIn("定位入口", index_html)
            self.assertIn("缺少证据", index_html)
            self.assertIn("入口识别模式", index_html)
            self.assertIn("SKILL.md 模板", index_html)
            self.assertIn("只列文件不解释职责", index_html)
            self.assertIn("增加模型对比", index_html)
            self.assertIn("主指令存在", index_html)
            self.assertIn("执行顺序来自结构推断", index_html)
            self.assertIn("无证据的性能承诺", index_html)
            self.assertIn("缺少脚本引用", index_html)
            self.assertIn("描述与文件结构不一致", index_html)
            self.assertIn("证据足够", index_html)
            self.assertIn("读取技能", (output_dir / "skills" / "demo-skill.html").read_text(encoding="utf-8"))

    def test_exported_artifacts_include_source_mirror_for_offline_quality(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            output_dir = root / "site" / "report"

            export_report(run_dir, output_dir)
            artifacts_dir = output_dir / "artifacts"

            self.assertTrue((artifacts_dir / "sources" / "demo-source" / "files" / "SKILL.md").exists())
            quality = quality_report_for_run(artifacts_dir)
            self.assertNotIn("EVIDENCE_SOURCE_NOT_FOUND", quality["code_counts"])

    def test_cli_export_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            output_dir = root / "report"

            exit_code = main(["export-report", "--run", str(run_dir), "--output", str(output_dir)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((output_dir / "index.html").exists())


if __name__ == "__main__":
    unittest.main()
