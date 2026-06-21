from __future__ import annotations

import unittest
from pathlib import Path


class HomeConfigCopyTest(unittest.TestCase):
    def test_home_explains_key_vs_env_field(self) -> None:
        html = Path("site/index.html").read_text(encoding="utf-8")
        script = Path("site/script.js").read_text(encoding="utf-8")

        self.assertIn("Environment variable name", html)
        self.assertIn("Direct API key", html)
        self.assertIn("Keys stay in this browser/local bridge session", html)
        self.assertIn("api_key_env is an environment variable name", script)


if __name__ == "__main__":
    unittest.main()
