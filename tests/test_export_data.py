from __future__ import annotations

import csv
import json
import tempfile
import unittest
from pathlib import Path

from asa.cli import main
from asa.data_exporter import export_data

from tests.test_export_report import make_run


class ExportDataTest(unittest.TestCase):
    def test_exports_flattened_jsonl_csv_and_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            output_dir = root / "data"

            manifest = export_data(run_dir, output_dir)

            self.assertEqual(manifest["skill_count"], 1)
            self.assertTrue((output_dir / "skills.jsonl").exists())
            self.assertTrue((output_dir / "resource_roles.csv").exists())
            self.assertTrue((output_dir / "workflow_trace.jsonl").exists())
            self.assertTrue((output_dir / "evidence_audit.jsonl").exists())
            self.assertTrue((output_dir / "reuse_assets.jsonl").exists())
            self.assertTrue((output_dir / "data_manifest.json").exists())
            self.assertTrue((output_dir / "graph-data.json").exists())
            self.assertTrue((output_dir / "graph.mmd").exists())

            skill_row = json.loads((output_dir / "skills.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(skill_row["skill_id"], "demo-skill")
            self.assertEqual(skill_row["skill_type"], "workflow")
            self.assertIn("演示技能用于说明拆解链路", skill_row["identity"])

            with (output_dir / "resource_roles.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows[0]["path"], "SKILL.md")
            self.assertEqual(rows[0]["read_policy"], "must_read")

            trace_row = json.loads((output_dir / "workflow_trace.jsonl").read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(trace_row["step_id"], "trace_1")
            self.assertEqual(trace_row["resources"], ["SKILL.md"])

            audit_lines = (output_dir / "evidence_audit.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertTrue(any(json.loads(line)["claim"] == "主指令存在" for line in audit_lines))

            reuse_lines = (output_dir / "reuse_assets.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertTrue(any(json.loads(line)["value"] == "入口识别模式" for line in reuse_lines))

            graph = json.loads((output_dir / "graph-data.json").read_text(encoding="utf-8"))
            self.assertTrue(any(node["type"] == "skill" for node in graph["nodes"]))
            self.assertTrue(any(node["type"] == "resource" and node["label"] == "SKILL.md" for node in graph["nodes"]))
            self.assertTrue(any(edge["type"] == "uses_resource" for edge in graph["edges"]))
            self.assertTrue(any(edge["type"] == "has_step" for edge in graph["edges"]))
            self.assertIn("clusters", graph)
            self.assertTrue(any(cluster["id"] == "cluster:workflow" for cluster in graph["clusters"]))
            self.assertTrue(all("lane" in node for node in graph["nodes"]))
            self.assertIn("subgraph", (output_dir / "graph.mmd").read_text(encoding="utf-8"))

    def test_cli_export_all_includes_data_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir = make_run(root)
            dist_dir = root / "dist"

            exit_code = main(["export-all", "--run", str(run_dir), "--output", str(dist_dir)])

            self.assertEqual(exit_code, 0)
            self.assertTrue((dist_dir / "data" / "skills.jsonl").exists())
            self.assertTrue((dist_dir / "data" / "data_manifest.json").exists())


if __name__ == "__main__":
    unittest.main()
