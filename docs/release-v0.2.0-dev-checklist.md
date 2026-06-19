# LetUen v0.2.0-dev Release Checklist

This checklist captures the current LetUen anchor-pack state before capability review and real-world evaluation.

## 1. Release Goal

v0.2.0-dev should prove that LetUen can:

- decompose skills into reusable anchors;
- preserve existing user skill structures;
- generate report, Obsidian, data, anchors, and optional composition plans;
- keep composition non-destructive by default;
- package the built-in method skills as a lightweight anchor-aware skill pack.

## 2. Current Capability Snapshot

| Capability | Status | Evidence |
|---|---:|---|
| 9 internal method skills packaged | Done | `skills/asa-*/SKILL.md` |
| All method skills anchor-aware | Done | `docs/letuen-skill-anchor-pack-roadmap.md` |
| Planner-only composition skill | Done | `skills/asa-anchor-composition-planner/SKILL.md` |
| Lightweight anchor schema | Done | `docs/letuen-anchor-schema.md` |
| Non-destructive policy | Done | `docs/letuen-non-destructive-invocation-policy.md` |
| Sample anchor composition | Done | `examples/anchor-composition/sample-skill/` |
| `export-anchors` CLI | Done | `src/asa/anchor_exporter.py` |
| `plan-composition` CLI | Done | `src/asa/composition_planner.py` |
| `export-letuen` CLI | Done | `src/asa/cli.py` |
| Report anchors section | Done | `src/asa/report_exporter.py` |
| Obsidian anchor notes | Done | `src/asa/vault_exporter.py` |
| Release package | Done | `releases/letuen-skill-anchor-pack-v0.2.0-dev.zip` |

## 3. Expected Package Contents

```text
letuen-skill-anchor-pack/
  README.md
  CALL_ORDER.md
  ANCHOR_SCHEMA.md
  COMPOSITION_FORMS.md
  HARNESS_INTEGRATION.md
  LIGHTWEIGHT_PROFILE.md
  NON_DESTRUCTIVE_INVOCATION.md
  examples/
    anchor-composition/
      sample-skill/
        README.md
        anchors.json
        composition_request.temporary.yaml
        composition_plan.temporary.json
        temporary_prompt_bundle.md
  skills/
    asa-anchor-composition-planner/
    asa-skill-identity-decomposer/
    asa-trigger-boundary-mapper/
    asa-resource-role-analyzer/
    asa-workflow-trace-builder/
    asa-evidence-grounding-auditor/
    asa-reuse-pattern-miner/
    asa-reader-layer-writer/
    asa-model-comparison-judge/
```

## 4. Acceptance Commands

Run from repository root:

```powershell
$env:PYTHONPATH='src'
python -m asa export-letuen `
  --run runs\demo-multi-skill `
  --output tmp\letuen-release-check `
  --composition-request examples\anchor-composition\sample-skill\composition_request.temporary.yaml
```

Expected files:

```text
tmp/letuen-release-check/report/index.html
tmp/letuen-release-check/vault/00 Maps/Agent Skill Anatomy MOC.md
tmp/letuen-release-check/vault/00 Maps/Anchor Index.md
tmp/letuen-release-check/vault/07 Anchors/Composition Plan.md
tmp/letuen-release-check/data/data_manifest.json
tmp/letuen-release-check/anchors/anchors.json
tmp/letuen-release-check/anchors/composition_plan.json
tmp/letuen-release-check/letuen_manifest.json
```

Run validation:

```powershell
node --check site/script.js
$env:PYTHONPATH='src'
python -m unittest discover -s tests
python -m compileall src scripts -q
```

## 5. Manual Review Checklist

### Report

- `report/index.html` has a `Reusable Anchors` section.
- The anchor section shows anchor type, confidence, risk, and reuse modes.
- The composition panel shows form, selected count, rejected count, dispatch policy, and solidification state.
- The report links to `../anchors/anchors.json` and `../anchors/composition_plan.json`.

### Obsidian

- `vault/Open in Obsidian.html` can open the vault flow.
- `00 Maps/Agent Skill Anatomy MOC.md` links to `Anchor Index`.
- `00 Maps/Anchor Index.md` lists anchor notes.
- `07 Anchors/` contains anchor notes and optional `Composition Plan.md`.
- Native Obsidian Graph View can show links without custom graph clutter.

### Data / Machine Outputs

- `anchors/anchors.json` is valid JSON.
- `anchors/composition_plan.json` is valid JSON when a request is provided.
- `letuen_manifest.json` points to report, vault, data, anchors, and optional composition plan.
- `vault/06 Data/vault_manifest.json` includes `anchor_count` and `07 Anchors/` notes.

## 6. Known Boundaries

- `export-anchors` is deterministic and conservative; it does not yet fully consume all future anchor fields emitted by LLM meta-skills.
- `plan-composition` is a lightweight filter/planner, not a full compatibility reasoning engine.
- Real model quality still depends on provider output quality and prompt/schema adherence.
- Multi-model comparison remains a development/testing capability, not a user-facing product entry.
- The release package contains method skills and examples, not the entire ASA harness.

## 7. Remaining Risks Before Public Release

| Risk | Impact | Mitigation |
|---|---|---|
| Anchor exporter may under-extract from rich real runs | Medium | Add fixtures from real GitHub skill repos |
| Composition planner may select anchors too mechanically | Medium | Add compatibility scoring and risk gates after evaluation |
| Obsidian anchor notes may be too dense for beginners | Low | Add reader-layer anchor cards after user review |
| Package naming still references historical ASA in paths | Low | Keep LetUen identity in docs while preserving existing compatibility |
| Provider-specific output variance | Medium | Use model comparison judge only in development tests |

## 8. Release Decision

Current recommendation: suitable for internal/dev release and capability evaluation.

Not yet recommended as a polished public release until real skill repo evaluations confirm:

- anchor extraction quality;
- composition usefulness;
- report readability;
- Obsidian graph clarity;
- non-destructive behavior under trigger overlap.
