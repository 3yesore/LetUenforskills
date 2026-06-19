from __future__ import annotations

import hashlib
import json
import shutil
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PACKAGE_ROOT_NAME = "letuen-skill-anchor-pack"
DEFAULT_VERSION = "v0.2.0-dev"

DOC_SOURCES = {
    "ANCHOR_SCHEMA.md": "docs/letuen-anchor-schema.md",
    "COMPOSITION_FORMS.md": "docs/letuen-composition-forms.md",
    "HARNESS_INTEGRATION.md": "docs/letuen-harness-integration-spec.md",
    "LIGHTWEIGHT_PROFILE.md": "docs/letuen-lightweight-profile.md",
    "NON_DESTRUCTIVE_INVOCATION.md": "docs/letuen-non-destructive-invocation-policy.md",
    "ANCHOR_COMPOSITION_PLANNER.md": "docs/letuen-anchor-composition-planner-spec.md",
    "USAGE_GUIDE.md": "docs/letuen-usage-guide.md",
}


def package_letuen_skill_pack(output_dir: Path, *, version: str = DEFAULT_VERSION) -> dict[str, Any]:
    repo_root = Path(__file__).resolve().parents[2]
    output_dir.mkdir(parents=True, exist_ok=True)
    package_root = output_dir / PACKAGE_ROOT_NAME
    if package_root.exists():
        shutil.rmtree(package_root)
    package_root.mkdir(parents=True)

    _write_main_skill(package_root, version)
    _write_readme(package_root, version)
    _copy_method_skills(repo_root, package_root)
    _copy_docs(repo_root, package_root)
    _copy_examples(repo_root, package_root)
    _write_evidence_repair_doc(package_root)
    _write_call_order(package_root)
    _write_install_check(package_root)

    skill_names = sorted(path.parent.name for path in (package_root / "skills").glob("*/SKILL.md"))
    manifest = {
        "schema_version": 1,
        "name": "letuen-skill-anchor-pack",
        "version": version,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "skill_count": len(skill_names),
        "skills": skill_names,
        "non_destructive_by_default": True,
        "harness_contract": {
            "side_effects": "none_by_default",
            "requires_user_approval_for_solidification": True,
            "preserve_existing_user_skills": True,
            "supports_anchor_composition": True,
            "supports_evidence_repair": True,
        },
        "entrypoints": {
            "main_skill": "SKILL.md",
            "method_skills": "skills/asa-*/SKILL.md",
            "anchor_schema": "ANCHOR_SCHEMA.md",
            "evidence_repair": "EVIDENCE_REPAIR.md",
            "install_check": "INSTALL_CHECK.md",
        },
    }
    (package_root / "PACK_MANIFEST.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    zip_path = output_dir / f"letuen-skill-anchor-pack-{version}.zip"
    tar_path = output_dir / f"letuen-skill-anchor-pack-{version}.tar.gz"
    _write_zip(package_root, zip_path)
    _write_tar(package_root, tar_path)
    _write_checksums(output_dir, [zip_path, tar_path])
    return manifest


def _write_main_skill(package_root: Path, version: str) -> None:
    content = f"""---
name: LetUen
description: Use when decomposing Agent Skills or workflow repositories into evidence-grounded reports, reusable anchors, Obsidian notes, and non-destructive composition plans.
version: {version}
internal_meta_skill_pack: true
non_destructive_by_default: true
output_contract: letuen.skill_anatomy_report + letuen.anchor_pack + letuen.obsidian_vault
---

# LetUen Skill Anatomy Pack

Use LetUen when the user wants to understand, compare, reuse, or recombine Agent Skills without blindly copying an entire workflow.

LetUen is not a single heavy workflow. It is an anchor-aware skill pack that can be used as:

- a decomposition guide,
- a quality/evidence gate,
- a reusable anchor extractor,
- a lightweight composition planner,
- an Obsidian/report authoring method,
- a development benchmark helper.

## Activation

Use this pack when the request mentions:

- decomposing a `SKILL.md` package,
- analyzing an agent skill repository,
- extracting reusable workflow parts,
- comparing model outputs for skill analysis,
- generating Obsidian learning notes from a skill,
- composing anchors without modifying existing user skills.

Do not use this pack as a generic coding helper. Do not override existing user skills with the same trigger. If trigger ownership is unclear, prefer the existing user skill and use LetUen as a sidecar analysis layer.

## Operating Contract

- Read source files before making claims.
- Keep quotes short and source-backed.
- Run evidence repair or equivalent source-aware quote checking before publishing.
- Emit anchors as sidecar assets by default.
- Do not mutate existing user skill directories unless the user explicitly asks.
- If solidifying a workflow, first produce a dry-run plan and ask for approval.

## Method Skill Order

1. `asa-skill-identity-decomposer`
2. `asa-trigger-boundary-mapper`
3. `asa-resource-role-analyzer`
4. `asa-workflow-trace-builder`
5. `asa-evidence-grounding-auditor`
6. `asa-reuse-pattern-miner`
7. `asa-reader-layer-writer`
8. `asa-anchor-composition-planner`
9. `asa-model-comparison-judge` only for development/model comparison tests

## Required Outputs

For a complete decomposition, produce or preserve:

- identity summary,
- trigger/boundary map,
- resource role map,
- workflow trace,
- evidence audit,
- reusable anchors,
- reader-facing report layers,
- optional composition plan,
- explicit unsupported-claim list.

## Quality Gate

A result is not publishable until:

- deterministic schema validation passes,
- evidence quote checks pass,
- unsupported high-confidence claims are removed or downgraded,
- existing user skill structure is preserved,
- generated anchors include risk and reuse metadata.
"""
    (package_root / "SKILL.md").write_text(content, encoding="utf-8")


def _write_readme(package_root: Path, version: str) -> None:
    content = f"""# LetUen Skill Anchor Pack {version}

LetUen decomposes Agent Skills into evidence-grounded explanations, reusable anchors, Obsidian-ready notes, and non-destructive composition plans.

This package contains the lightweight method skills only. It does not bundle the full local web UI or Python harness.

## Contents

- `SKILL.md` — main pack entry and operating contract.
- `skills/asa-*/SKILL.md` — internal method skills.
- `ANCHOR_SCHEMA.md` — anchor data contract.
- `COMPOSITION_FORMS.md` — reuse/composition forms.
- `HARNESS_INTEGRATION.md` — how a host harness should call the skills.
- `NON_DESTRUCTIVE_INVOCATION.md` — trigger and mutation safety policy.
- `EVIDENCE_REPAIR.md` — source-aware evidence repair behavior.
- `examples/` — anchor composition example.

## Install Shape

Install the whole directory as one skill pack, or copy individual `skills/asa-*` method skills into an existing harness that already has a coordinator.

## Release Status

Developer preview. Deterministic quality gates pass on the DeepSeek v4pro five-skill benchmark after source-aware evidence repair, but broader multi-model public benchmark claims are still pending.
"""
    (package_root / "README.md").write_text(content, encoding="utf-8")


def _copy_method_skills(repo_root: Path, package_root: Path) -> None:
    target = package_root / "skills"
    target.mkdir()
    for skill_dir in sorted((repo_root / "skills").glob("asa-*")):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            shutil.copytree(skill_dir, target / skill_dir.name)


def _copy_docs(repo_root: Path, package_root: Path) -> None:
    for output_name, source in DOC_SOURCES.items():
        source_path = repo_root / source
        if source_path.exists():
            shutil.copyfile(source_path, package_root / output_name)


def _copy_examples(repo_root: Path, package_root: Path) -> None:
    examples_target = package_root / "examples"
    examples_target.mkdir()
    source = repo_root / "examples" / "anchor-composition"
    if source.exists():
        shutil.copytree(source, examples_target / "anchor-composition")


def _write_evidence_repair_doc(package_root: Path) -> None:
    content = """# Evidence Repair

LetUen requires source-grounded evidence before a decomposition can be treated as publishable.

A host harness should run a source-aware evidence repair pass after model generation and before final quality gating.

Expected behavior:

1. Resolve every evidence object back to its source file.
2. If the quote is an exact source substring, keep it.
3. If the quote is a paraphrase of a nearby source line, replace it with the exact source line or a short exact source substring.
4. If no reliable source match exists, downgrade the evidence to `inferred`, lower confidence, and record a repair note.
5. Write a repair report so users can audit every change.

In the LetUen Python harness this is implemented by:

```powershell
python -m asa repair-evidence --run <run-dir>
python -m asa quality-run --run <run-dir>
```

The skill pack itself does not require this exact CLI, but any compatible harness should implement equivalent behavior before publishing reports.
"""
    (package_root / "EVIDENCE_REPAIR.md").write_text(content, encoding="utf-8")


def _write_call_order(package_root: Path) -> None:
    content = """# Call Order

1. Identity decomposer
2. Trigger/boundary mapper
3. Resource role analyzer
4. Workflow trace builder
5. Evidence grounding auditor
6. Reuse pattern miner
7. Reader layer writer
8. Anchor composition planner
9. Model comparison judge only for development benchmarks

The evidence repair pass runs after model artifacts are produced and before deterministic publishability checks.
"""
    (package_root / "CALL_ORDER.md").write_text(content, encoding="utf-8")


def _write_install_check(package_root: Path) -> None:
    content = """# Install Check

After unpacking, verify:

```text
letuen-skill-anchor-pack/SKILL.md
letuen-skill-anchor-pack/PACK_MANIFEST.json
letuen-skill-anchor-pack/skills/asa-anchor-composition-planner/SKILL.md
letuen-skill-anchor-pack/skills/asa-evidence-grounding-auditor/SKILL.md
letuen-skill-anchor-pack/skills/asa-model-comparison-judge/SKILL.md
letuen-skill-anchor-pack/skills/asa-reader-layer-writer/SKILL.md
letuen-skill-anchor-pack/skills/asa-resource-role-analyzer/SKILL.md
letuen-skill-anchor-pack/skills/asa-reuse-pattern-miner/SKILL.md
letuen-skill-anchor-pack/skills/asa-skill-identity-decomposer/SKILL.md
letuen-skill-anchor-pack/skills/asa-trigger-boundary-mapper/SKILL.md
letuen-skill-anchor-pack/skills/asa-workflow-trace-builder/SKILL.md
```

Expected method skill count: 9.

Do not install this pack in a way that overrides existing user skills with the same trigger. LetUen should run as a sidecar analysis/composition layer unless explicitly selected.
"""
    (package_root / "INSTALL_CHECK.md").write_text(content, encoding="utf-8")


def _write_zip(package_root: Path, zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_root.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_root.parent).as_posix())


def _write_tar(package_root: Path, tar_path: Path) -> None:
    if tar_path.exists():
        tar_path.unlink()
    with tarfile.open(tar_path, "w:gz") as archive:
        archive.add(package_root, arcname=package_root.name)


def _write_checksums(output_dir: Path, files: list[Path]) -> None:
    lines = []
    for path in files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        lines.append(f"{digest}  {path.name}")
    (output_dir / "SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
