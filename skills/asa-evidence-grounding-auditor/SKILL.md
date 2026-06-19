---
name: asa-evidence-grounding-auditor
description: Use when auditing whether a skill decomposition is evidence-grounded, over-inference-safe, and publishable.
internal_meta_skill: true
asa_role: reviewer
output_contract: review_report.evidence_audit + letuen.evidence_anchors
---

# ASA Evidence Grounding Auditor

Use this internal meta-skill when a model must decide whether a skill analysis is trustworthy enough to publish or reuse.

This skill fixes the failure mode where a fluent report hides unsupported claims, weak evidence, copied passages, overconfident inference, or unsafe anchors selected for reuse.

## Inputs

- Deterministic inventory and source snapshot.
- Structure analysis and workflow analysis artifacts.
- Evidence objects attached to claims and workflow steps.
- Quality rule outputs when available.

## Process

1. List the major claims made by the analysis.
2. Classify each claim as `explicit`, `structural`, `inferred`, `unsupported`, or `conflicting`.
3. Check whether high-confidence claims have direct evidence.
4. Check whether inferred claims are marked as inferred and use cautious confidence.
5. Detect vague evidence, missing source paths, copied long passages, and quote overuse.
6. Identify claims that sound plausible but only come from model reasoning.
7. Convert reusable review findings into evidence, risk, confidence, and unsupported-claim anchors.
8. Rate publishability as `publishable`, `needs_revision`, or `blocked`.
9. Write concise remediation notes for every major or blocker issue.

## Output Contract

Return evidence audit content suitable for `review_report.json`:

```yaml
evidence_audit:
  supported_claims: []
  inferred_claims: []
  unsupported_claims: []
  missing_evidence: []
  conflicts: []
  publishable:
  rationale:
  anchors:
    evidence_anchor:
      - id:
        claim_id:
        evidence_kind: direct_quote | structural_inventory | workflow_order | resource_reference | test_output | model_inference
        source_path:
        quote:
        supports:
        limitations: []
        reusable_as: quality_gate | citation_pattern | review_note | learning_note
        confidence: high | medium | low | unknown
    risk_anchor:
      - id:
        risk_type: over_inference | missing_evidence | copied_passage | runtime_claim | trigger_conflict | unsafe_reuse | stale_context
        affected_claims: []
        severity: high | medium | low
        mitigation:
        blocks_reuse: true | false
        evidence: []
    confidence_anchor:
      - id:
        target_id:
        target_kind: claim | workflow_step | resource_role | reuse_asset | composition_candidate
        confidence: high | medium | low | unknown
        confidence_basis: direct | structural | inferred | conflicting | absent
        downgrade_reason:
        upgrade_requirements: []
        evidence: []
    unsupported_claim_anchor:
      - id:
        claim:
        why_unsupported:
        likely_source: model_reasoning | missing_source | ambiguous_text | contradicted_by_source | unknown
        recommended_action: remove | rewrite_as_inference | add_evidence | block_publish
        safe_reuse: true | false
        evidence: []
```


## Anchor Output Rules

Emit anchors that make the audit reusable as a quality layer for future decomposition or composition work.

- `evidence_anchor`: a reusable support object that ties one claim to source material and states its limitations.
- `risk_anchor`: a reusable warning about over-inference, missing evidence, copied passages, unsafe reuse, or stale context.
- `confidence_anchor`: a confidence decision that can downgrade or gate a claim, workflow step, resource role, reuse asset, or composition candidate.
- `unsupported_claim_anchor`: a claim that must be removed, rewritten as inference, backed with evidence, or blocked from publication.

Every anchor must state whether it is safe for reuse. Evidence anchors may support reuse; risk and unsupported-claim anchors may block or constrain reuse. Do not convert every minor note into an anchor; only anchor findings that affect trust, learning value, or composition safety.

## Evidence Rules

- Treat source files and deterministic inventory as stronger evidence than model summaries.
- Treat file existence as structural evidence, not proof of runtime behavior.
- Treat absent evidence as a review finding, not a reason to invent support.
- Keep direct quotes short and use source paths whenever possible.

## Failure Modes

- Do not accept polished prose as evidence.
- Do not let high confidence survive without direct or structural support.
- Do not hide unsupported claims because the overall report is useful.
- Do not mark a report publishable when important workflow steps are invented.

## Quality Rubric

A strong evidence audit answers:

- Which claims are truly supported?
- Which claims are only inferred?
- Which claims should be revised or removed?
- What would make the report safe to publish?


## Source-Aware Evidence Repair

Before a report or anchor pack is treated as publishable, run a source-aware evidence repair pass or require the host harness to provide an equivalent repaired evidence report.

The repair pass must:

1. Resolve each evidence object to the referenced source file.
2. Keep exact quotes only when they are true source substrings.
3. Replace paraphrased quotes with short exact source snippets when a reliable match exists.
4. Downgrade unrepairable explicit evidence to `inferred`, lower confidence, and record a note.
5. Repair deterministic inventory gaps, such as missing script manifests, only when source inventory proves the files exist.
6. Preserve an audit log of every repair.

Do not mark `publishable` if unrepaired explicit evidence quotes cannot be found in source files. A fluent summary is not a substitute for repaired evidence.

Compatible harness command in this repository:

```powershell
python -m asa repair-evidence --run <run-dir>
python -m asa quality-run --run <run-dir>
```
