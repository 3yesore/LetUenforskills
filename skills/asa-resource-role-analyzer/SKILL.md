---
name: asa-resource-role-analyzer
description: Use when explaining what each file, script, reference, asset, or template does inside a skill package.
internal_meta_skill: true
asa_role: structure_analyst
output_contract: structure_analysis.resource_roles
---

# ASA Resource Role Analyzer

Use this internal meta-skill when a model must explain what each important file or resource does in a skill package.

This skill fixes the failure mode where analysis lists files but does not explain whether they are instructions, templates, executable tools, references, examples, assets, tests, configs, schemas, or compliance material.

## Inputs

- Deterministic file inventory for one skill package.
- `SKILL.md` content and package layout.
- Related files under `scripts`, `references`, `assets`, `examples`, `templates`, `tests`, and root files.
- Dependency index when available.

## Process

1. Classify each important resource by role.
2. Determine whether the resource is must-read, on-demand, optional, or ignorable for execution.
3. Map the resource to a workflow stage: activation, planning, context loading, execution, validation, delivery, learning, or compliance.
4. Identify reuse value: high, medium, low, or unknown.
5. Identify risk or brittleness, such as missing dependencies, external services, large context, or license constraints.
6. Distinguish execution resources from learning/reference resources.
7. Attach evidence from file layout, names, source text, or dependency extraction.

## Output Contract

Return resource role content suitable for `structure_analysis.json`:

```yaml
resource_roles:
  - path:
    role:
    stage:
    read_policy: must_read | on_demand | optional | ignore
    reuse_value: high | medium | low | unknown
    risk:
    evidence: []
```


## Anchor-Aware Output

In addition to resource role content, emit minimal anchor cards for resources that may affect reuse or composition. Keep this lightweight; do not copy files or decide whether to apply them to a user project.

Recommended anchor types:

- `resource_anchor`: an important file, directory, reference, asset, or config.
- `template_anchor`: a reusable scaffold, prompt template, UI template, document template, or schema.
- `tool_anchor`: a script, command, API helper, or executable utility.
- `dependency_anchor`: package, runtime, environment variable, service, or external requirement.
- `portable_resource_anchor`: a resource that can be copied or adapted safely.
- `non_portable_resource_anchor`: a resource that should stay reference-only or requires permission/adaptation.

Minimal anchor card shape:

```yaml
anchors:
  - id: anchor.<skill_id>.resource.<slug>
    source_skill_id:
    anchor_type: resource_anchor
    name:
    summary:
    evidence:
      path:
      quote:
    confidence: low | medium | high
    reuse_modes:
      - reference_only
      - template_pack
      - embedded_in_existing_workflow
    risks:
      - missing dependency, license risk, context size, or runtime assumption
```

Anchor rules:

- Emit anchors only for resources that influence execution, learning, reuse, validation, or composition.
- Mark templates and schemas as `template_anchor` when they shape downstream outputs.
- Mark executable scripts, commands, and API helpers as `tool_anchor` only when execution is supported by source evidence or dependency analysis.
- Mark packages, env vars, runtimes, and external services as `dependency_anchor`.
- Mark `portable_resource_anchor` only when copying/adapting appears safe and useful.
- Mark `non_portable_resource_anchor` when a resource is license-bound, context-bound, environment-bound, secret-bearing, or too coupled to the original skill.
- Do not copy or adapt resources here; pass anchors to `asa-anchor-composition-planner`.

## Evidence Rules

- Use `structural` evidence for file path and layout claims.
- Use `explicit` evidence when `SKILL.md` says to read or use a file.
- Use `inferred` evidence when assigning likely stage from filename or package convention.
- Do not claim a script executes unless source instructions or code usage supports it.

## Failure Modes

- Do not treat every related file as required.
- Do not ignore templates because they are not scripts.
- Do not classify license files as execution resources.
- Do not hide missing or unresolved dependencies.

## Quality Rubric

A strong resource analysis lets a reader answer:

- Which files matter?
- Why do they matter?
- When are they read or used?
- Are they reusable?
- What risks do they introduce?



