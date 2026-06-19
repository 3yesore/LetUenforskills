# Decomposition Manual Spec / 拆解说明书规格

## Purpose

The generated report must read like a real skill manual, not a model transcript or code-only summary. It should let two audiences understand the same skill:

- **New reader**: understands what the skill does, when it activates, which files matter, and what to copy.
- **Experienced skill designer**: sees composition choices, workflow boundaries, evidence quality, reusable patterns, and failure modes.

Default language is Chinese. English remains available through the UI/report toggle.

## Core Reading Contract

Every report page should answer these questions in order:

1. **它是什么**: skill identity, intended user, target agent/runtime, and activation purpose.
2. **它由什么组成**: `SKILL.md`, scripts, references, assets, templates, config, examples, and generated outputs.
3. **它如何串联**: trigger boundary, reading order, workflow steps, tool handoffs, fallback paths, and stop conditions.
4. **它如何实现**: important files, interfaces, scripts, prompt patterns, resource loading, and execution assumptions.
5. **它是否可信**: evidence map, direct vs inferred claims, reviewer findings, deterministic quality issues, and unsupported claims.
6. **它如何复用**: reusable patterns, adaptation checklist, minimal viable transplant, anti-patterns, and learning notes.

The report must not begin with raw JSON, score cards, or abstract methodology. Methodology appears after the reader understands the skill.

## Information Hierarchy

### Level 1: Executive Manual

Purpose: one-screen comprehension.

Required blocks:

- `Skill Card`: name, source repo, target agents, skill type, language/runtime, confidence.
- `One Sentence Anatomy`: one direct sentence describing what the skill helps an agent do.
- `Activation Boundary`: when to use / when not to use.
- `Composition Strip`: SKILL.md, scripts, references, assets, examples, external dependencies.
- `Workflow Preview`: 5-9 ordered steps with clear verbs.
- `Reader Actions`: open cinema, read full manual, inspect graph, export Obsidian/data.

### Level 2: Structural Manual

Purpose: show how the skill is built.

Required blocks:

- `Package Map`: source paths grouped by role.
- `Resource Role Matrix`: each resource's role, why it exists, and which workflow step uses it.
- `Implementation Decoder`: scripts/functions/commands/config contracts and their relationship to the skill instruction.
- `Dependency Notes`: local dependencies, external services, permissions, environment variables, network assumptions.

### Level 3: Workflow Manual

Purpose: show how a user or agent executes it.

Required blocks:

- `Trigger Boundary`: explicit cues, negative cues, ambiguity notes.
- `Workflow Chain`: step id, action, input, output, evidence, confidence.
- `Decision Points`: branch conditions and failure handling.
- `Tool Handoffs`: where scripts, browser, shell, file IO, or APIs are used.
- `Stop Conditions`: when the skill is done, what artifact proves completion.

### Level 4: Evidence & Quality Manual

Purpose: keep the report rigorous.

Required blocks:

- `Evidence Ledger`: source path, quote/line/block, evidence type, claim id.
- `Inference Register`: claims that are not directly stated but derived from structure.
- `Reviewer Findings`: unsupported claims, missing evidence, risk notes, approval state.
- `Deterministic Quality`: schema, quote length, missing source paths, invalid references.
- `Confidence Policy`: why a claim is high/medium/low.

### Level 5: Learning & Reuse Manual

Purpose: turn the decomposition into reusable assets.

Required blocks:

- `What To Copy`: composable skill patterns with exact source references.
- `What To Avoid`: anti-patterns, ambiguous boundaries, over-broad instructions, brittle scripts.
- `Adaptation Recipe`: steps to build a similar skill in another domain.
- `Obsidian Links`: concept note, pattern note, workflow note, evidence note.
- `Reusable Pack`: checklist, prompt skeleton, resource layout, validation rubric.

## Section Ordering

Recommended order for generated report pages:

1. Hero / skill card
2. Reader guide
3. Composition overview
4. Workflow trace
5. Implementation decoder
6. Resource roles
7. Evidence and quality
8. Reuse assets
9. Method layer
10. Artifacts and appendix

Reasoning:

- Users first need a readable explanation.
- Methodology is important, but should not block comprehension.
- Raw artifacts belong at the end or behind links.

## De-Duplication Rules

Reports often become repetitive when the same model output appears under several headings. Use these rules:

- `identity` appears once in the hero and may be referenced later, but not restated as full prose.
- `workflow_step.summary` appears in the workflow trace; implementation sections should explain files/tools, not repeat the same summary.
- `resource_roles` owns file-role explanations; evidence sections cite files only to support claims.
- `reviewer` owns quality issues; report narrative should link to issues rather than duplicating them.
- `reuse_assets` owns copy/adapt instructions; pattern summaries should not repeat the full adaptation recipe.
- If two sections must mention the same fact, the second mention should use a one-line cross-reference.

## Evidence Display Rules

Every visible claim category has a different evidence requirement:

| Claim Type | Evidence Requirement | Display Style |
| --- | --- | --- |
| File exists | deterministic path | inline path chip |
| Instruction says X | quote or block id | quote preview + source |
| Workflow step | source signal or model inference | step card with confidence |
| Tool/API behavior | script/config/source reference | implementation chip |
| Reuse pattern | at least one source and rationale | pattern card |
| Risk/failure | source or reviewer rationale | review card |
| Unsupported insight | no direct support | quarantined issue card |

Unsupported claims must not be silently rewritten into confident prose.

## Navigation Behavior

The report should support fast scanning:

- top nav uses stable anchors and does not hide section headings under sticky bars
- right-bottom `Top` action returns to hero
- cards link to graph/data/vault artifacts when available
- Cinema should link into report anchors after each stage
- report should link back to Cinema and home without losing context

Anchor offset should be handled with CSS `scroll-margin-top` rather than per-click JavaScript hacks.

## Bilingual Behavior

Default Chinese copy should be professional and concise. English copy should be semantic, not word-for-word machine translation.

Rules:

- Keep technical labels stable: `Workflow Trace`, `Evidence Audit`, `Reuse Asset`.
- Chinese explanation uses natural product language: `如何组成`, `如何串联`, `如何复用`.
- Do not mix long bilingual paragraphs in the same visible block; use toggle state.
- Raw source names, paths, model ids, and schema keys stay unchanged.

## Acceptance Checklist

A report passes the manual standard when:

- a non-expert can explain what the skill does after the first screen
- an expert can identify the trigger, resources, workflow, and implementation contract within three minutes
- every important claim has evidence, confidence, or explicit inference status
- reusable assets are concrete enough to copy into another skill project
- Obsidian/data/graph exports point to the same underlying claim/evidence model
- the page still feels like the same product as Cinema and Repo surfaces
