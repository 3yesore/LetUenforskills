# Publishing LetUen Skill Anchor Pack v0.2.0-dev

Prepared local release artifacts:

- `letuen-skill-anchor-pack-v0.2.0-dev.zip`
- `letuen-skill-anchor-pack-v0.2.0-dev.tar.gz`
- `SHA256SUMS.txt`
- unpacked inspection directory: `releases/letuen-skill-anchor-pack/`

## What This Release Contains

This is a developer-preview skill anchor pack, not the full LetUen web UI or Python harness.

The package contains:

- main `SKILL.md` coordinator contract;
- 9 internal method skills under `skills/asa-*`;
- anchor schema and composition specs;
- non-destructive invocation policy;
- source-aware evidence repair specification;
- sample anchor composition assets;
- install check and pack manifest.

## Local Verification Already Run

```powershell
$env:PYTHONPATH='src'
python -m unittest discover -s tests
python -m compileall src scripts -q
node --check site\script.js
python -m asa package-letuen-skill --output releases --version v0.2.0-dev
```

Result:

- `58 tests OK`
- package generated successfully
- method skill count: `9`
- archive structure checked via `tar -tf releases\letuen-skill-anchor-pack-v0.2.0-dev.zip`

## Capability Evidence

DeepSeek v4pro five-skill benchmark:

- Run: `evaluations/runs/20260618T143729Z`
- Final quality: `evaluations/deepseek-v4pro-benchmark-five-quality.repaired.json`
- Result: `0 issues`, `publishable_by_rules=true`
- Release evaluation: `evaluations/deepseek-v4pro-benchmark-five/release_evaluation.md`

Important nuance:

- Deterministic quality gates pass after source-aware evidence repair.
- Model reviewer status is mixed: 2 of 5 benchmark skill analyses are publishable, 3 are `needs_revision` by reviewer-level quality judgment.
- This supports a developer-preview release, not a polished public benchmark claim.

## Install Check

After unpacking, verify:

```text
letuen-skill-anchor-pack/SKILL.md
letuen-skill-anchor-pack/PACK_MANIFEST.json
letuen-skill-anchor-pack/EVIDENCE_REPAIR.md
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

Expected method skill count: `9`.

## GitHub Release

The v0.2.0-dev release has been created at `https://github.com/3yesore/LetUenforskills/releases/tag/v0.2.0-dev`. To recreate it manually:

```powershell
gh auth login
gh release create v0.2.0-dev `
  releases/letuen-skill-anchor-pack-v0.2.0-dev.zip `
  releases/letuen-skill-anchor-pack-v0.2.0-dev.tar.gz `
  releases/SHA256SUMS.txt `
  --title "LetUen Skill Anchor Pack v0.2.0-dev" `
  --notes-file evaluations/deepseek-v4pro-benchmark-five/release_evaluation.md
```

## Release Positioning

Recommended wording:

> LetUen decomposes Agent Skills into evidence-grounded reports, reusable anchors, Obsidian notes, and non-destructive composition plans. This v0.2.0-dev package is a developer-preview method skill pack with source-aware evidence repair and deterministic quality gates.

Do not claim broad model-agnostic benchmark quality until DeepSeek flash, GPT, Claude, and Qwen routes have also been evaluated.
