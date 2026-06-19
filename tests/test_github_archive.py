from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from asa.collectors.inventory import github_archive_url, unpack_github_archive


class GitHubArchiveTest(unittest.TestCase):
    def test_builds_archive_url_with_ref(self) -> None:
        url = github_archive_url("https://github.com/anthropics/skills", "main")

        self.assertEqual(url, "https://github.com/anthropics/skills/archive/main.zip")

    def test_builds_archive_url_with_default_head(self) -> None:
        url = github_archive_url("https://github.com/anthropics/skills", None)

        self.assertEqual(url, "https://github.com/anthropics/skills/archive/HEAD.zip")

    def test_unpack_archive_returns_single_top_level_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            archive_path = root / "repo.zip"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("repo-main/SKILL.md", "# Demo")
            destination = root / "dest"

            unpacked = unpack_github_archive(archive_path, destination)
            self.assertEqual(unpacked.name, "repo-main")
            self.assertTrue((unpacked / "SKILL.md").exists())


if __name__ == "__main__":
    unittest.main()
