from __future__ import annotations

from pathlib import Path
from typing import Any


def build_skill_context(inventory: dict[str, Any], package: dict[str, Any], max_text_kb: int = 128) -> dict[str, Any]:
    root_path = Path(inventory["repository"]["root_path"])
    skill_md_path = root_path / package["skill_md_path"]
    readme_path = root_path / package["readme_path"] if package.get("readme_path") else None
    return {
        "skill_md": read_limited_text(skill_md_path, root_path, max_text_kb),
        "readme": read_limited_text(readme_path, root_path, max_text_kb // 2) if readme_path else None,
        "scripts_manifest": package.get("scripts", []),
        "references_manifest": package.get("references", []),
        "assets_manifest": package.get("assets", []),
    }


def read_limited_text(path: Path | None, root_path: Path, max_text_kb: int) -> dict[str, Any] | None:
    if path is None or not path.exists() or not path.is_file():
        return None
    size_bytes = path.stat().st_size
    max_bytes = max_text_kb * 1024
    content = path.read_bytes()[:max_bytes].decode("utf-8", errors="replace")
    return {
        "path": path.relative_to(root_path).as_posix(),
        "size_bytes": size_bytes,
        "truncated": size_bytes > max_bytes,
        "content": content,
    }

