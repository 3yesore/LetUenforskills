# Agent Skill Anatomy Internal Meta-Skills

This directory contains internal LetUen / Agent Skill Anatomy method skills. They are not target skills for normal repository analysis.

这些 skill 是 LetUen / Agent Skill Anatomy 自己用于指导拆解、锚点选择与组合规划的内部 meta-skills。默认情况下，它们不应该作为被分析对象进入普通 source discovery。

## Current Method Skill Set

- `asa-anchor-composition-planner`: planner-only skill for selecting anchors into lightweight reuse forms without forcing workflow solidification.
- `asa-skill-identity-decomposer`: identify what a skill is before workflow analysis.
- `asa-trigger-boundary-mapper`: map activation signals, boundaries, and false positives.
- `asa-resource-role-analyzer`: explain file/resource responsibilities and emit resource/template/tool/dependency anchors.
- `asa-workflow-trace-builder`: reconstruct user-intent-to-output workflow traces and emit workflow/handoff/validation/output-transition anchors.
- `asa-evidence-grounding-auditor`: audit evidence grounding, over-inference, publishability, and emit evidence/risk/confidence anchors.
- `asa-reuse-pattern-miner`: extract reusable patterns, templates, checklists, anti-patterns, composition candidates, and solidification templates.
- `asa-reader-layer-writer`: turn structured decomposition into beginner/expert learning surfaces, anchor cards, learning notes, and operator guides.
- `asa-model-comparison-judge`: compare multiple model outputs on the same skill decomposition task and emit consensus/disagreement/best-model-per-anchor-type anchors for development testing.

## Guardrail

Internal meta-skills should be excluded from normal skill source analysis unless an explicit test, benchmark, or LetUen anchor-pack development task enables them.


