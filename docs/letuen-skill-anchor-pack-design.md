# LetUen Skill Anchor Pack Design

LetUen is an anchor-based skill decomposition and recomposition method pack. Its purpose is not only to explain a skill, and not only to solidify a new workflow. LetUen decomposes skills into reusable anchors that can be selected, combined, temporarily borrowed, embedded into existing projects, or solidified into new workflows or skills when the user chooses that path.

LetUen 是一个基于锚点的 Skill 拆解与重组方法包。它不只解释 skill，也不默认把所有拆解结果固化成工作流。LetUen 的目标是把 skill 拆成可定位、可评估、可拼接、可迁移的 anchors，让用户按需求选择临时组合、嵌入现有项目、生成规则补丁、沉淀 Obsidian 笔记，或进一步固化成 workflow / new skill。


## 0. Lightweight Design Constraint

LetUen must remain a thin method layer, not a heavy replacement framework. The default experience should produce small anchor cards and optional composition plans. Project apply, workflow solidification, and new skill generation are enhanced modes, not the default path.

See `docs/letuen-lightweight-profile.md` for the L1/L2/L3 operating levels.

## 1. Problem Statement

Many users cannot fully benefit from existing skills because:

- Skill activation rules are unclear or conflict with existing user skills.
- Valuable capability fragments are hidden inside a large `SKILL.md` or resource tree.
- Users want only part of a skill, not a full workflow.
- Combining multiple skills often breaks context loading, tool assumptions, output contracts, or quality checks.
- Solidified workflows are useful for some users, but too heavy for others.

LetUen solves this by extracting stable anchors, evaluating portability and compatibility, then composing selected anchors into a chosen reuse form.

## 2. Core Concept: Skill Anchor

A Skill Anchor is a reusable, evidence-backed capability fragment extracted from one or more skills.

An anchor may be small or large:

- a trigger rule
- a boundary condition
- a resource loading rule
- a prompt fragment
- a workflow step
- a template or script dependency
- a validation check
- an output shape
- a risk warning
- a reuse pattern

Anchors can be decomposed further or composed into larger units. This gives LetUen high playability: users can split large skills into small anchors, or combine small anchors into larger task-specific compositions.

## 3. Anchor Types

| Type | Purpose | Example |
|---|---|---|
| `trigger_anchor` | When the skill should activate | User asks for algorithmic art |
| `boundary_anchor` | When not to activate or where scope ends | Do not replace scientific simulation |
| `resource_anchor` | Required files, templates, references, assets | Must read `templates/viewer.html` first |
| `instruction_anchor` | Stable instruction or prompt structure | Generate concept before implementation |
| `workflow_anchor` | Ordered execution unit | trigger → load template → generate → verify |
| `tool_anchor` | Script/tool/API command unit | Run formatter or generator script |
| `template_anchor` | Portable template or scaffold | HTML viewer template |
| `evidence_anchor` | Source-grounded claim support | Source path and quote |
| `validation_anchor` | Quality or safety gate | Check self-contained output |
| `output_anchor` | Result format or artifact shape | HTML artifact, markdown note, schema JSON |
| `reuse_anchor` | Higher-level transferable pattern | Concept → Template → Artifact |
| `risk_anchor` | Reuse or composition risk | Template copied without validation |

## 4. Reuse Modes

LetUen must not assume that every composition becomes a full workflow. Every anchor can declare supported reuse modes:

```yaml
reuse_modes:
  - reference_only
  - temporary_composition
  - prompt_fragment
  - agent_rule_patch
  - embedded_in_existing_workflow
  - workflow_step
  - tool_adapter
  - template_pack
  - quality_gate
  - learning_note
  - full_workflow
  - new_skill
```

## 5. Composition Forms

A composition form is the shape selected by the user or harness after anchor selection.

| Form | Description | Solidifies Workflow? |
|---|---|---:|
| `reference_only` | Read and learn from anchors only | No |
| `temporary_composition` | Borrow anchors for one task/session | No |
| `prompt_patch` | Turn anchors into prompt/instruction fragments | No |
| `agent_rule_patch` | Add anchors to Codex/Cursor/Claude rules | Optional |
| `workflow_insert` | Insert selected anchors into an existing workflow | Optional |
| `tool_adapter` | Wrap a tool/script anchor for use elsewhere | Optional |
| `template_pack` | Export templates/assets/references | No |
| `quality_gate` | Reuse only validation/audit anchors | No |
| `learning_note` | Export Obsidian/tutorial notes | No |
| `full_workflow_blueprint` | Build a complete workflow blueprint | Yes |
| `new_skill_spec` | Repackage selected anchors as a new skill | Yes |

## 6. Harness Role

The harness is the compatibility layer that makes anchor composition safe. It must:

1. preserve user skill structure;
2. detect trigger conflicts;
3. avoid silently overriding existing user skills;
4. pass selected anchors through explicit input/output contracts;
5. keep evidence and confidence attached to every anchor;
6. distinguish temporary composition from workflow solidification;
7. export reversible patches instead of destructive edits.

A LetUen-composed skill or workflow is valid only if the harness can explain:

- why each anchor was selected;
- which source skill it came from;
- what evidence supports it;
- what assumptions it carries;
- what it requires from adjacent anchors;
- how it should be invoked without breaking existing skills.

## 7. Non-Destructive Design Principle

LetUen must never mutate a user's existing skills by default.

Default output should be one of:

- a composition plan;
- a prompt patch;
- a sidecar rule file;
- an optional new skill directory;
- an Obsidian note;
- a dry-run diff;
- a reversible patch bundle.

When triggers overlap with user skills, LetUen should generate a dispatch policy instead of overwriting triggers.

## 8. Built-In Meta-Skills

The current internal skills become anchor-aware method skills:

1. `asa-skill-identity-decomposer` → identity/value/output anchors
2. `asa-trigger-boundary-mapper` → trigger/boundary/handoff anchors
3. `asa-resource-role-analyzer` → resource/dependency/template anchors
4. `asa-workflow-trace-builder` → workflow/handoff/replaceable-step anchors
5. `asa-evidence-grounding-auditor` → evidence/risk/confidence anchors
6. `asa-reuse-pattern-miner` → reuse/composition/anti-pattern anchors
7. `asa-reader-layer-writer` → anchor cards and reuse-form guides
8. `asa-model-comparison-judge` → model agreement and best-model-per-anchor-type

A future ninth skill should coordinate anchor composition:

`asa-anchor-composition-planner`

## 9. Default Flow

```text
Collect skills
  → Decompose identity / triggers / resources / workflow
  → Extract anchors
  → Audit evidence and risks
  → Score portability and compatibility
  → Select anchors for a user goal
  → Compose chosen reuse form
  → Export reversible assets
```

## 10. Design Goal

LetUen should let users do all of the following:

- decompose a large skill into smaller anchors;
- compose several anchors into a temporary capability;
- merge compatible anchors into an existing workflow;
- export a prompt/rule/template patch;
- build a new skill only when desired;
- keep the original user skills intact;
- use Obsidian Graph View to understand relationships naturally.



