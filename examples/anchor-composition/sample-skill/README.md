# Sample Skill Anchor Composition

This example validates the LetUen lightweight anchor flow with the local `examples/sample-skill/SKILL.md` fixture.

It is intentionally small and evidence-grounded. The goal is not to demonstrate a full workflow generator; the goal is to show that anchors can be borrowed and composed without modifying existing user skills.

## Files

- `anchors.json`: L1 anchor notes extracted from the sample skill.
- `composition_request.temporary.yaml`: a user request that asks for temporary composition only.
- `composition_plan.temporary.json`: an L2 planner output that selects compatible anchors and rejects unnecessary ones.
- `temporary_prompt_bundle.md`: the lightest useful output for a one-off task.

## Validation Path

1. Read `anchors.json` and confirm every selected anchor has source evidence from `examples/sample-skill/SKILL.md`.
2. Read `composition_request.temporary.yaml` and confirm `avoid_full_workflow: true`.
3. Read `composition_plan.temporary.json` and confirm:
   - existing user skills remain primary by default;
   - no persistent workflow or new skill is generated;
   - selected anchors have high evidence confidence and low risk;
   - the identity anchor is rejected because it is useful context but unnecessary for the temporary composition.
4. Read `temporary_prompt_bundle.md` and confirm it is usable as a session-only prompt fragment.

## Expected Planner Behavior

The planner should select:

- `workflow_anchor`: progressive read then deliver;
- `boundary_anchor`: no destructive commands;
- `validation_anchor`: requested format check.

The planner should not select:

- `identity_anchor`: runtime skeleton test identity, because the request is for temporary response behavior rather than learning context or new-skill generation.

## Safety Notes

This example has no file writes, command execution, network calls, or persistent skill changes. It should remain valid for Codex, Claude, Cursor, Gemini, and generic agent harnesses.
