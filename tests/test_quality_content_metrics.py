from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from asa.quality.report import quality_report_for_run

from tests.test_export_report import make_run


class QualityContentMetricsTest(unittest.TestCase):
    def test_quality_report_includes_density_and_template_tone_metrics(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = make_run(Path(temp_dir))

            report = quality_report_for_run(run_dir)

        self.assertIn("content_quality", report)
        content = report["content_quality"]
        self.assertIn("average_density_score", content)
        self.assertIn("average_template_tone_score", content)
        self.assertGreaterEqual(content["average_density_score"], 0)
        self.assertLessEqual(content["average_density_score"], 1)
        self.assertIn("content_quality", report["skills"][0])
        self.assertIn("template_markers", report["skills"][0]["content_quality"])


if __name__ == "__main__":
    unittest.main()
