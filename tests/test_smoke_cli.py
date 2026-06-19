from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from asa.cli import main


class SmokeCliTest(unittest.TestCase):
    def test_smoke_github_writes_error_artifact_on_source_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            sources = root / "sources.yaml"
            output = root / "out"
            sources.write_text(
                "sources:\n"
                "  - name: broken\n"
                "    url: https://github.com/example/broken\n"
                "    ref: main\n",
                encoding="utf-8",
            )
            with patch("asa.cli.collect_inventory", side_effect=RuntimeError("network down")):
                exit_code = main(["smoke-github", "--sources", str(sources), "--output", str(output)])

            self.assertEqual(exit_code, 2)
            self.assertTrue((output / "broken.error.json").exists())


if __name__ == "__main__":
    unittest.main()

