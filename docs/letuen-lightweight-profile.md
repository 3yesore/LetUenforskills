# LetUen Lightweight Profile

LetUen should remain a thin, composable method layer. It should not become a heavy framework that users must adopt wholesale before benefiting from skill anchors.

This profile defines the minimum useful version and the optional layers that can be added only when needed.

## 1. Lightweight Principle

LetUen should prefer:

- small anchor cards over large monolithic reports;
- optional composition over mandatory workflow generation;
- sidecar outputs over modifying user files;
- native host features over custom visual systems;
- progressive detail over full schema burden at first contact.

## 2. Three Operating Levels

| Level | Name | Purpose | Required Artifacts |
|---|---|---|---|
| L1 | Anchor Notes | Understand and borrow parts of skills | `anchors.jsonl`, Obsidian/Markdown notes |
| L2 | Composition Plan | Combine selected anchors safely | `composition_plan.json`, `dispatch_policy.json` when needed |
| L3 | Project Apply | Persist changes into a project | dry-run diff, rollback, approval log |

Most users should start at L1 or L2. L3 is optional and should be disabled by default.

## 3. Minimal Anchor Card

A minimal anchor does not need the full schema. It only needs enough information to be useful and safe:

```yaml
id: string
source_skill_id: string
anchor_type: string
name: string
summary: string
evidence:
  path: string
  quote: string
confidence: low | medium | high
reuse_modes:
  - reference_only
  - temporary_composition
risks:
  - string
```

The full schema in `letuen-anchor-schema.md` is the normalized export contract, not the minimum UI or prompt surface.

## 4. Minimal Composition Plan

```yaml
goal: string
composition_form: temporary_composition | prompt_patch | agent_rule_patch | learning_note
selected_anchors:
  - anchor_id
conflicts:
  - none | trigger_overlap | resource_missing | output_mismatch
recommendation: string
outputs:
  - path
```

Only generate compatibility matrices, dry-run diffs, and rollback plans when the user asks to integrate with a project or persist changes.

## 5. Optional Heavy Features

These are useful but should not be required for the default experience:

- full compatibility matrix;
- project apply workflow;
- new skill generation;
- workflow solidification;
- benchmark/model comparison;
- custom graph visualization;
- multi-stage approval logs.

## 6. Host-Native First

LetUen should use the host's native structures whenever possible:

- Obsidian native links and Graph View instead of custom graph clutter;
- Codex/Claude/Cursor existing skill directories instead of proprietary wrappers;
- plain Markdown and JSONL before complex databases;
- sidecar `.letuen/` directories before modifying project files.

## 7. Good Default UX

Default output should answer four questions:

1. What anchors did we find?
2. Which anchors are safe to borrow?
3. Which anchors can be combined now?
4. What is the lightest useful output for the user's goal?

If the answer requires more structure, LetUen can escalate from L1 to L2 or L3.
