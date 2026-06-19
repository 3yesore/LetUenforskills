#!/usr/bin/env python3
"""Collect skill package inventory from a local path or GitHub repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


SKIP_DIRS = {
    ".cache",
    ".git",
    ".venv",
    "__pycache__",
    "dist",
    "node_modules",
    "tmp",
    "venv",
}
SKIP_RELATIVE_DIRS = {
    ("releases", "letuen-skill-anchor-pack"),
}
SCRIPT_DIRS = {"scripts", "script", "bin", "tools"}
REFERENCE_DIRS = {"references", "reference", "refs", "docs"}
ASSET_DIRS = {"assets", "asset", "static", "images"}
EXAMPLE_DIRS = {"examples", "example", "samples", "sample"}
INTERNAL_META_SKILL_PREFIX = "asa-"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def slugify(value: str) -> str:
    cleaned = "".join(character.lower() if character.isalnum() else "-" for character in value)
    parts = [part for part in cleaned.split("-") if part]
    return "-".join(parts) or "source"


def run_git(args: list[str], cwd: Path | None = None) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip()


def is_github_url(source: str) -> bool:
    parsed = urlparse(source)
    return parsed.scheme in {"http", "https"} and parsed.netloc.lower() == "github.com"


def source_name_from_url(url: str) -> str:
    parsed = urlparse(url)
    path_parts = [part for part in parsed.path.strip("/").split("/") if part]
    if len(path_parts) >= 2:
        return slugify(f"{path_parts[0]}-{path_parts[1].removesuffix('.git')}")
    return slugify(parsed.path or "github-source")


def clone_source(url: str, ref: str | None, cache_root: Path) -> Path:
    source_name = source_name_from_url(url)
    digest = hashlib.sha256(f"{url}@{ref or 'default'}".encode("utf-8")).hexdigest()[:12]
    target_path = cache_root / f"{source_name}-{digest}"
    if target_path.exists() and (target_path / ".git").exists():
        return target_path
    if target_path.exists():
        shutil.rmtree(target_path)

    target_path.parent.mkdir(parents=True, exist_ok=True)
    clone_args = ["clone", "--depth", "1", "--filter", "blob:none"]
    if ref:
        clone_args.extend(["--branch", ref])
    clone_args.extend([url, str(target_path)])
    try:
        subprocess.run(["git", *clone_args], check=True)
    except subprocess.CalledProcessError:
        if target_path.exists():
            shutil.rmtree(target_path)
        return download_archive_source(url, ref, cache_root)
    return target_path


def github_archive_url(url: str, ref: str | None) -> str:
    parsed = urlparse(url)
    path = parsed.path.strip("/").removesuffix(".git")
    if ref:
        return f"https://github.com/{path}/archive/{ref}.zip"
    return f"https://github.com/{path}/archive/HEAD.zip"


def download_archive_source(url: str, ref: str | None, cache_root: Path) -> Path:
    source_name = source_name_from_url(url)
    digest = hashlib.sha256(f"archive:{url}@{ref or 'HEAD'}".encode("utf-8")).hexdigest()[:12]
    target_path = cache_root / f"{source_name}-archive-{digest}"
    if target_path.exists():
        return target_path

    archive_url = github_archive_url(url, ref)
    archive_path = cache_root / f"{source_name}-{digest}.zip"
    temp_path = cache_root / f"{source_name}-archive-{digest}.tmp"
    cache_root.mkdir(parents=True, exist_ok=True)
    if temp_path.exists():
        shutil.rmtree(temp_path)
    if archive_path.exists():
        archive_path.unlink()
    urllib.request.urlretrieve(archive_url, archive_path)
    unpacked_path = unpack_github_archive(archive_path, temp_path)
    if target_path.exists():
        shutil.rmtree(target_path)
    shutil.move(str(unpacked_path), str(target_path))
    shutil.rmtree(temp_path, ignore_errors=True)
    archive_path.unlink(missing_ok=True)
    return target_path


def unpack_github_archive(archive_path: Path, destination: Path) -> Path:
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        archive.extractall(destination)
    top_level_dirs = [path for path in destination.iterdir() if path.is_dir()]
    if len(top_level_dirs) != 1:
        raise ValueError(f"Expected one top-level directory in GitHub archive, found {len(top_level_dirs)}")
    return top_level_dirs[0]


def relative_path(root_path: Path, file_path: Path) -> str:
    return file_path.relative_to(root_path).as_posix()


def should_skip(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return True
    return any(path.parts[: len(relative_dir)] == relative_dir for relative_dir in SKIP_RELATIVE_DIRS)


def iter_files(root_path: Path) -> list[Path]:
    files: list[Path] = []
    for file_path in root_path.rglob("*"):
        if should_skip(file_path.relative_to(root_path)):
            continue
        if file_path.is_file():
            files.append(file_path)
    return files


def file_ref(root_path: Path, file_path: Path, reason: str | None = None) -> dict:
    suffix = file_path.suffix.lower().lstrip(".") or "none"
    return {
        "path": relative_path(root_path, file_path),
        "file_type": suffix,
        "size_bytes": file_path.stat().st_size,
        "reason": reason,
    }


def extract_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---"):
        return {}
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    frontmatter: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return frontmatter
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"\'')
    return {}


def is_internal_meta_skill(root_path: Path, skill_file: Path) -> bool:
    skill_root = skill_file.parent
    relative_parts = skill_root.relative_to(root_path).parts
    if len(relative_parts) >= 2 and relative_parts[-2] == "skills" and relative_parts[-1].startswith(INTERNAL_META_SKILL_PREFIX):
        return True
    try:
        frontmatter = extract_frontmatter(skill_file.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        frontmatter = extract_frontmatter(skill_file.read_text(encoding="utf-8", errors="ignore"))
    return frontmatter.get("internal_meta_skill", "").lower() == "true"


def find_first(root_path: Path, names: set[str]) -> str | None:
    lower_names = {name.lower() for name in names}
    for file_path in iter_files(root_path):
        if file_path.name.lower() in lower_names:
            return relative_path(root_path, file_path)
    return None


def categorize_related_files(root_path: Path, skill_root: Path) -> dict[str, list[dict]]:
    categories = {
        "scripts": [],
        "references": [],
        "assets": [],
        "examples": [],
        "related_files": [],
    }
    for file_path in iter_files(skill_root):
        if file_path.name == "SKILL.md":
            continue
        local_parts = file_path.relative_to(skill_root).parts
        top_dir = local_parts[0].lower() if local_parts else ""
        if top_dir in SCRIPT_DIRS:
            categories["scripts"].append(file_ref(root_path, file_path, "script directory"))
        elif top_dir in REFERENCE_DIRS:
            categories["references"].append(file_ref(root_path, file_path, "reference directory"))
        elif top_dir in ASSET_DIRS:
            categories["assets"].append(file_ref(root_path, file_path, "asset directory"))
        elif top_dir in EXAMPLE_DIRS:
            categories["examples"].append(file_ref(root_path, file_path, "example directory"))
        else:
            categories["related_files"].append(file_ref(root_path, file_path, "same skill package"))
    return categories


def collect_inventory(source: str, ref: str | None, cache_root: Path) -> dict:
    source_type = "github" if is_github_url(source) else "local"
    if source_type == "github":
        root_path = clone_source(source, ref, cache_root).resolve()
        source_name = source_name_from_url(source)
        source_url = source
    else:
        root_path = Path(source).expanduser().resolve()
        source_name = slugify(root_path.name)
        source_url = None

    if not root_path.exists():
        raise FileNotFoundError(f"Source path not found: {root_path}")

    all_files = iter_files(root_path)
    skill_files = [file_path for file_path in all_files if file_path.name == "SKILL.md"]
    resolved_commit = run_git(["rev-parse", "HEAD"], cwd=root_path)
    acquisition_method = "git_clone" if (root_path / ".git").exists() else "github_archive" if source_type == "github" else "local"
    license_path = find_first(root_path, {"LICENSE", "LICENSE.md", "COPYING"})
    readme_path = find_first(root_path, {"README.md", "README"})

    skill_packages = []
    excluded_internal_count = 0
    for skill_file in sorted(skill_files):
        if is_internal_meta_skill(root_path, skill_file):
            excluded_internal_count += 1
            continue
        skill_root = skill_file.parent
        skill_name = skill_root.name if skill_root != root_path else source_name
        skill_id = slugify(f"{source_name}-{relative_path(root_path, skill_root)}")
        if not skill_id or skill_id == source_name:
            skill_id = slugify(f"{source_name}-{skill_name}")
        categories = categorize_related_files(root_path, skill_root)
        package_readme = None
        for readme_name in ("README.md", "README"):
            candidate = skill_root / readme_name
            if candidate.exists():
                package_readme = relative_path(root_path, candidate)
                break
        skill_packages.append(
            {
                "id": skill_id,
                "name": skill_name,
                "root_path": relative_path(root_path, skill_root),
                "skill_md_path": relative_path(root_path, skill_file),
                "readme_path": package_readme,
                **categories,
            }
        )

    warnings = []
    if not skill_packages:
        warnings.append("No SKILL.md files found.")
    if excluded_internal_count:
        warnings.append(f"Excluded {excluded_internal_count} internal meta-skill" + ("s" if excluded_internal_count != 1 else ""))

    return {
        "schema_version": 1,
        "source": {
            "name": source_name,
            "type": source_type,
            "url": source_url,
            "path": str(root_path) if source_type == "local" else None,
            "ref": ref,
            "resolved_commit": resolved_commit,
            "fetched_at": utc_now(),
            "license": None,
            "acquisition_method": acquisition_method,
        },
        "repository": {
            "root_path": str(root_path),
            "readme_path": readme_path,
            "license_path": license_path,
            "total_files_scanned": len(all_files),
        },
        "skill_packages": skill_packages,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect Agent Skill Anatomy inventory.")
    parser.add_argument("--source", required=True, help="GitHub URL or local directory.")
    parser.add_argument("--ref", default=None, help="Git branch, tag, or commit-ish for GitHub sources.")
    parser.add_argument("--cache-root", default=".cache/sources", help="Directory for cloned GitHub repositories.")
    parser.add_argument("--output", required=True, help="Output inventory JSON path.")
    args = parser.parse_args()

    inventory = collect_inventory(args.source, args.ref, Path(args.cache_root))
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(inventory, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote inventory for {len(inventory['skill_packages'])} skill package(s): {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




