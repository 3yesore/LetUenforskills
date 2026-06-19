# LetUen Non-Destructive Skill Invocation Policy

This document defines how LetUen compositions should coexist with user skills. The goal is to let users experiment with anchor composition without breaking existing trigger behavior or skill structure.

## 1. Core Rule

Existing user skills win by default.

LetUen may recommend, simulate, or generate sidecar assets, but it must not silently override:

- user skill trigger wording;
- skill directory names;
- `SKILL.md` frontmatter;
- scripts, assets, references, or templates;
- user-defined dispatch priority.

## 2. Skill Structure Preservation

LetUen outputs must be sidecar-first:

```text
project/
  skills/
    existing-user-skill/
      SKILL.md
  .letuen/
    compositions/
      <composition-id>/
        composition_plan.json
        dispatch_policy.json
        dry_run_diff.md
        generated/
```

If a new skill is requested, generate it as a separate directory:

```text
skills/
  letuen-composed-<name>/
    SKILL.md
    references/
    scripts/
```

Never merge it into an existing skill unless the user approves a patch.

## 3. Trigger Overlap Handling

When a LetUen composition has a trigger similar to an existing user skill, create a dispatch policy.

Example:

```yaml
conflict_id: trigger.frontend-design.visual-ui
existing_skill: frontend-design
letuen_composition: letuen-composed-ui-review
overlap_type: semantic_overlap
default_policy: prefer_existing_skill
resolution_options:
  - ask_user
  - route_by_anchor_type
  - run_both_then_compare
  - disable_letuen_auto_trigger
```

## 4. Invocation Modes

LetUen compositions can be invoked in several modes:

| Mode | Description | Auto-trigger? |
|---|---|---:|
| `manual_only` | User explicitly calls the composition | No |
| `ask_on_overlap` | Ask when trigger conflicts with user skill | Conditional |
| `route_by_scope` | Dispatch based on narrow scope rules | Conditional |
| `shadow_mode` | Run LetUen analysis but do not affect output | No |
| `benchmark_mode` | Compare existing skill and composition | No |
| `active_composition` | LetUen composition can respond directly | Yes, only with approval |

Default mode is `manual_only` for generated compositions.

## 5. Anchor-Level Dispatch

Dispatch does not need to select an entire skill. It can select anchor-level behavior.

Example:

- Existing skill handles final output.
- LetUen composition contributes only a validation anchor.
- Another skill contributes a resource loading anchor.

This makes partial composition possible without replacing the whole skill.

## 6. Collision Safety

LetUen must detect and report:

- trigger collisions;
- output file collisions;
- resource path collisions;
- tool command collisions;
- environment variable collisions;
- incompatible runtime assumptions;
- contradictory constraints.

## 7. User-Facing Choices

When overlap exists, show choices like:

```text
A. Keep existing skill as primary, use LetUen only as reference.
B. Use LetUen anchors manually for this task.
C. Insert selected anchors into existing workflow as a sidecar patch.
D. Create a separate composed skill.
E. Compare both outputs before deciding.
```

## 8. Rollback Requirement

Any persistent composition must generate rollback instructions:

```yaml
rollback:
  files_created:
    - path
  files_modified:
    - path
  restore_steps:
    - string
```

## 9. Default Safety Profile

```yaml
preserve_existing_skill_structure: true
default_invocation_mode: manual_only
default_dispatch_policy: prefer_existing_skill
require_user_approval_for:
  - trigger_changes
  - existing_file_modification
  - command_execution
  - network_access
  - persistent_workflow_activation
```
