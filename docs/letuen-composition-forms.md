# LetUen Composition Forms

LetUen supports multiple composition forms because users do not always want a full workflow or a new skill. The harness must preserve this choice throughout planning, generation, export, and UI display.

## 1. Form Catalogue

| Form | User Intent | Output | Destructive? |
|---|---|---|---:|
| `reference_only` | Learn from anchors without using them directly | Markdown / Obsidian notes | No |
| `temporary_composition` | Use selected anchors for a single task | Session plan / prompt bundle | No |
| `prompt_patch` | Borrow instruction fragments | Markdown prompt patch | No |
| `agent_rule_patch` | Add behavior to Codex/Cursor/Claude rules | Sidecar rule file or patch | No by default |
| `workflow_insert` | Insert anchors into existing workflow | Dry-run diff / insert spec | No by default |
| `tool_adapter` | Wrap a tool/script anchor | Adapter spec / script scaffold | Optional |
| `template_pack` | Reuse templates, assets, examples | File bundle | No |
| `quality_gate` | Reuse only validation checks | Checklist / gate spec | No |
| `learning_note` | Study and teach the skill | Obsidian note / tutorial | No |
| `full_workflow_blueprint` | Build a complete process | Workflow blueprint | No unless applied |
| `new_skill_spec` | Repackage anchors as a new skill | New skill directory | No to existing skills |

## 2. Lightweight Harness Behavior

For every composition form, the harness should record the lightest useful set first. Full records are required only when the user persists or applies a composition:

- user goal;
- selected anchors;
- rejected anchors;
- evidence confidence;
- portability score;
- risk score;
- compatibility matrix when anchors interact or conflict;
- dispatch policy when triggers overlap;
- output paths;
- whether the result is temporary or persistent.

## 3. Optional Solidification

Solidification is a final optional step, not the default composition behavior.

A composition may become solidified only when:

1. the user selects `full_workflow_blueprint` or `new_skill_spec`;
2. trigger conflicts have a dispatch policy;
3. required resources are available or adapted;
4. validation anchors are included or explicitly waived;
5. the output is generated as a new artifact, not by overwriting existing skills.

## 4. Playability Model

LetUen should support three directions:

- **Split down**: decompose a large skill into small anchors.
- **Build across**: combine anchors from several skills into a temporary or embedded capability.
- **Build up**: optionally solidify selected anchors into a larger workflow or new skill.

This lets users experiment without committing to a permanent workflow too early.

