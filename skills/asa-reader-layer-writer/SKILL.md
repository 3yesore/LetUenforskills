---
name: asa-reader-layer-writer
description: Use when turning structured skill decomposition artifacts into beginner, expert, report, or Obsidian reading layers.
internal_meta_skill: true
asa_role: report_exporter
output_contract: report.reader_layers + letuen.reader_anchors
---

# ASA Reader Layer Writer

Use this internal meta-skill when structured decomposition must become a readable report, Obsidian note, tutorial, or visual surface.

This skill fixes the failure mode where reports repeat the same summary, assume too much skill-design knowledge, bury implementation details without a reading path, or fail to expose reusable anchor cards for learning and operation.

## Inputs

- Inventory, structure analysis, workflow analysis, reviewer output, and patterns.
- Reader intent: beginner learning, expert implementation, reuse, comparison, or audit.
- Available surfaces: web report, cinema narrative, Obsidian vault, graph, and data files.

## Process

1. Start with a reader guide that explains how to read the report.
2. Write a beginner layer that explains concepts without jargon.
3. Write an expert layer that preserves implementation details, constraints, and evidence.
4. Put identity, trigger, workflow, resources, evidence, and reuse in a clear order.
5. Avoid repeating the same sentence in hero, snapshot, manual, and appendix.
6. Explain specialized terms such as trigger, boundary, context, evidence, and workflow.
7. Convert key concepts, learning notes, and operational guidance into reader anchors.
8. Keep Chinese as the default layer when project language is bilingual.
9. Preserve bilingual structure so English can mirror the same meaning.

## Output Contract

Return reader-layer guidance suitable for report and vault exporters:

```yaml
reader_layers:
  beginner:
  expert:
  glossary: []
  reading_order: []
  report_notes: []
  obsidian_notes: []
  anchors:
    anchor_card:
      - id:
        source_anchor_id:
        title:
          zh:
          en:
        one_sentence:
          zh:
          en:
        why_it_matters:
          zh:
          en:
        reader_level: beginner | intermediate | expert | operator
        source_section:
        evidence: []
    learning_note_anchor:
      - id:
        topic:
        explains:
          zh:
          en:
        prerequisites: []
        examples: []
        common_misreadings: []
        obsidian_links: []
        evidence: []
    operator_guide_anchor:
      - id:
        task:
        when_to_use:
        steps: []
        expected_inputs: []
        expected_outputs: []
        safety_checks: []
        reuse_modes: []
        evidence: []
```


## Anchor Output Rules

Emit reader anchors that make the decomposition understandable and reusable across surfaces.

- `anchor_card`: a compact visual/report card for one important anchor or concept.
- `learning_note_anchor`: an Obsidian-friendly explanation that helps non-experts understand terms, structure, and reuse logic.
- `operator_guide_anchor`: a practical guide for someone who wants to apply, borrow, or combine the analyzed skill behavior.

Reader anchors must preserve evidence boundaries. Beginner wording can simplify concepts, but it cannot hide uncertainty, convert inference into fact, or suggest unsafe reuse. Keep Chinese and English fields parallel so UI/report language switching remains possible.

## Evidence Rules

- Reader-friendly phrasing must not weaken evidence boundaries.
- Beginner explanations may simplify terms but must not add new claims.
- Expert notes should point to source paths, workflow steps, and review findings.
- Reuse guidance must distinguish confirmed mechanism from suggested adaptation.

## Failure Modes

- Do not write only for experts.
- Do not turn every section into a marketing summary.
- Do not repeat identical summaries across multiple report blocks.
- Do not hide uncertainty to make the page feel smoother.

## Quality Rubric

A strong reader layer answers:

- Can a newcomer understand what this skill is?
- Can an expert see how it is built and connected?
- Can a learner reuse the method safely?
- Can the report be read in a deliberate order without duplication?

