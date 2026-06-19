from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from .anchor_exporter import export_anchors
from .collectors.inventory import collect_inventory
from .composition_planner import plan_anchor_composition
from .config import load_config, load_sources
from .data_exporter import export_data
from .errors import write_error_artifact
from .evidence_repair import repair_run_evidence
from .jsonio import write_json
from .planner import plan_run
from .quality.report import quality_report_for_run
from .review_summary import summarize_run_reviews
from .report_exporter import export_report
from .release_packager import package_letuen_skill_pack
from .runtime import resume_harness, run_harness
from .vault_exporter import export_vault
from .validator import validate_run


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="asa", description="Agent Skill Anatomy CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Run the full analysis harness.")
    run_parser.add_argument("--config", default="anatomy.config.example.yaml", help="Path to anatomy config YAML.")
    run_parser.add_argument("--provider", default=None, help="Provider override, currently only mock is implemented.")
    run_parser.add_argument("--limit-skills", type=int, default=None, help="Analyze at most N discovered skill packages.")

    collect_parser = subparsers.add_parser("collect", help="Collect inventory from a source.")
    collect_parser.add_argument("--source", required=True, help="GitHub URL or local directory.")
    collect_parser.add_argument("--ref", default=None, help="Git branch, tag, or commit-ish.")
    collect_parser.add_argument("--output", required=True, help="Output inventory JSON path.")
    collect_parser.add_argument("--cache-root", default=".cache/sources", help="Cache directory for GitHub clones.")

    validate_parser = subparsers.add_parser("validate", help="Validate artifacts in a run directory.")
    validate_parser.add_argument("--run", required=True, help="Run directory to validate.")

    resume_parser = subparsers.add_parser("resume", help="Resume a previous run and reuse valid artifacts.")
    resume_parser.add_argument("--run", required=True, help="Run directory to resume.")
    resume_parser.add_argument("--provider", default=None, help="Provider override.")
    resume_parser.add_argument("--limit-skills", type=int, default=None, help="Analyze at most N discovered skill packages.")

    smoke_parser = subparsers.add_parser("smoke-github", help="Run collector-only smoke checks for sources.")
    smoke_parser.add_argument("--sources", default="sources.smoke.github.yaml", help="Sources YAML path.")
    smoke_parser.add_argument("--output", default="runs/github-smoke", help="Output directory for inventories.")

    plan_parser = subparsers.add_parser("plan-run", help="Plan a run without calling model agents.")
    plan_parser.add_argument("--config", default="anatomy.config.example.yaml", help="Path to anatomy config YAML.")
    plan_parser.add_argument("--limit-skills", type=int, default=None, help="Plan at most N discovered skill packages.")
    plan_parser.add_argument("--output", default=None, help="Optional output JSON path.")

    anchor_export_parser = subparsers.add_parser("export-anchors", help="Export LetUen anchors from a run directory.")
    anchor_export_parser.add_argument("--run", required=True, help="Run directory to export anchors from.")
    anchor_export_parser.add_argument("--output", required=True, help="Output anchors JSON path.")
    composition_parser = subparsers.add_parser("plan-composition", help="Plan a lightweight anchor composition without calling model agents.")
    composition_parser.add_argument("--anchors", required=True, help="Input anchors JSON path.")
    composition_parser.add_argument("--request", required=True, help="Composition request JSON/YAML path.")
    composition_parser.add_argument("--output", default=None, help="Optional output composition plan JSON path.")
    review_parser = subparsers.add_parser("review-run", help="Summarize reviewer outputs for a run.")
    review_parser.add_argument("--run", required=True, help="Run directory to summarize.")
    review_parser.add_argument("--output", default=None, help="Optional output JSON path.")


    repair_parser = subparsers.add_parser("repair-evidence", help="Repair evidence quotes against source files for a run.")
    repair_parser.add_argument("--run", required=True, help="Run directory to repair.")
    repair_parser.add_argument("--threshold", type=float, default=0.58, help="Fuzzy match threshold for quote repair.")

    quality_parser = subparsers.add_parser("quality-run", help="Run programmatic quality checks for a run.")
    quality_parser.add_argument("--run", required=True, help="Run directory to check.")
    quality_parser.add_argument("--output", default=None, help="Optional output JSON path.")

    export_parser = subparsers.add_parser("export-report", help="Export a static browsable report for a run.")
    export_parser.add_argument("--run", required=True, help="Run directory to export.")
    export_parser.add_argument("--output", required=True, help="Output directory for the static report.")

    vault_parser = subparsers.add_parser("export-vault", help="Export an Obsidian-ready Markdown vault for a run.")
    vault_parser.add_argument("--run", required=True, help="Run directory to export.")
    vault_parser.add_argument("--output", required=True, help="Output directory for the Obsidian vault.")

    data_parser = subparsers.add_parser("export-data", help="Export flattened JSONL/CSV datasets for a run.")
    data_parser.add_argument("--run", required=True, help="Run directory to export.")
    data_parser.add_argument("--output", required=True, help="Output directory for data exports.")

    eval_parser = subparsers.add_parser("init-evaluation", help="Create a LetUen capability evaluation folder.")
    eval_parser.add_argument("--name", required=True, help="Evaluation source name.")
    eval_parser.add_argument("--source", required=True, help="Source URL or local path being evaluated.")
    eval_parser.add_argument("--output", default="evaluations", help="Evaluation root directory.")
    eval_parser.add_argument("--model", default="unknown", help="Model or route name for the evaluation note.")
    letuen_parser = subparsers.add_parser("export-letuen", help="Export report, vault, data, anchors, and optional composition plan.")
    letuen_parser.add_argument("--run", required=True, help="Run directory to export.")
    letuen_parser.add_argument("--output", required=True, help="Output directory for all LetUen assets.")
    letuen_parser.add_argument("--composition-request", default=None, help="Optional composition request JSON/YAML path.")
    package_parser = subparsers.add_parser("package-letuen-skill", help="Package the LetUen skill anchor pack for release.")
    package_parser.add_argument("--output", default="releases", help="Output directory for the release package.")
    package_parser.add_argument("--version", default="v0.2.0-dev", help="Release version label.")

    all_parser = subparsers.add_parser("export-all", help="Export report, vault, and data outputs for a run.")
    all_parser.add_argument("--run", required=True, help="Run directory to export.")
    all_parser.add_argument("--output", required=True, help="Output directory for all exported assets.")

    args = parser.parse_args(argv)
    if args.command == "run":
        config = load_config(Path(args.config))
        run_dir = run_harness(config, args.provider, limit_skills=args.limit_skills)
        print(f"Completed run: {run_dir}")
        return 0
    if args.command == "collect":
        inventory = collect_inventory(args.source, args.ref, Path(args.cache_root))
        write_json(Path(args.output), inventory)
        print(f"Wrote inventory for {len(inventory['skill_packages'])} skill package(s): {args.output}")
        return 0
    if args.command == "validate":
        result = validate_run(Path(args.run))
        for checked in result["checked"]:
            print(f"valid {checked}")
        for issue in result["issues"]:
            print(f"invalid {issue['path']}: {issue['error']}")
        return 0 if result["valid"] else 1
    if args.command == "resume":
        run_dir = resume_harness(Path(args.run), args.provider, limit_skills=args.limit_skills)
        print(f"Resumed run: {run_dir}")
        return 0
    if args.command == "smoke-github":
        output_dir = Path(args.output)
        total_packages = 0
        failures = 0
        for source in load_sources(Path(args.sources)):
            source_value = source.get("url") or source.get("path")
            if not source_value:
                continue
            source_name = source.get("name") or str(source_value).rstrip("/").split("/")[-1]
            try:
                inventory = collect_inventory(str(source_value), source.get("ref"), Path(".cache/sources"))
                output_path = output_dir / f"{inventory['source']['name']}.inventory.json"
                write_json(output_path, inventory)
                package_count = len(inventory["skill_packages"])
                total_packages += package_count
                print(
                    f"{inventory['source']['name']}: {package_count} package(s), "
                    f"method={inventory['source'].get('acquisition_method')}"
                )
            except Exception as exc:
                failures += 1
                write_error_artifact(
                    output_dir / f"{source_name}.error.json",
                    code="GITHUB_SMOKE_FAILED",
                    stage="smoke_github",
                    message=str(exc),
                    recoverable=True,
                    context={"source": source},
                )
                print(f"{source_name}: failed ({exc})")
        print(f"Total packages: {total_packages}")
        if total_packages > 0:
            return 0
        return 2 if failures else 1
    if args.command == "plan-run":
        plan = plan_run(load_config(Path(args.config)), limit_skills=args.limit_skills)
        if args.output:
            write_json(Path(args.output), plan)
        else:
            import json

            print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0
    if args.command == "export-anchors":
        document = export_anchors(Path(args.run), Path(args.output))
        print(f"Exported anchors: {args.output}")
        print(f"Anchor count: {document['anchor_count']}")
        return 0
    if args.command == "plan-composition":
        plan = plan_anchor_composition(Path(args.anchors), Path(args.request), Path(args.output) if args.output else None)
        if not args.output:
            import json

            print(json.dumps(plan, ensure_ascii=False, indent=2))
        else:
            print(f"Wrote composition plan: {args.output}")
        return 0
    if args.command == "review-run":
        summary = summarize_run_reviews(Path(args.run))
        if args.output:
            write_json(Path(args.output), summary)
        print_review_summary(summary)
        return 0 if summary["reviewed_skill_count"] else 1
    if args.command == "repair-evidence":
        report = repair_run_evidence(Path(args.run), threshold=args.threshold)
        print(f"Repaired artifacts: {report['artifact_count']}")
        print(f"Evidence repair changes: {report['change_count']}")
        print(f"Report: {Path(args.run) / 'evidence_repair_report.json'}")
        return 0
    if args.command == "quality-run":
        report = quality_report_for_run(Path(args.run))
        if args.output:
            write_json(Path(args.output), report)
        print(f"Checked skills: {report['checked_skill_count']}")
        print(f"Issues: {report['issue_count']}")
        print(f"Severity counts: {report['severity_counts']}")
        print(f"Publishable by rules: {report['publishable_by_rules']}")
        return 0 if report["publishable_by_rules"] else 2
    if args.command == "export-report":
        result = export_report(Path(args.run), Path(args.output))
        print(f"Exported report: {result['index']}")
        print(f"Skill pages: {len(result['skill_pages'])}")
        return 0
    if args.command == "export-vault":
        result = export_vault(Path(args.run), Path(args.output))
        print(f"Exported vault: {result['output_dir']}")
        print(f"Vault notes: {len(result['notes'])}")
        return 0
    if args.command == "export-data":
        result = export_data(Path(args.run), Path(args.output))
        print(f"Exported data: {Path(args.output).resolve()}")
        print(f"Data rows: {result['row_counts']}")
        return 0
    if args.command == "init-evaluation":
        result = init_evaluation_folder(args.name, args.source, Path(args.output), args.model)
        print(f"Initialized evaluation: {result['evaluation_dir']}")
        print(f"Composition request: {result['composition_request']}")
        print(f"Review note: {result['review_note']}")
        return 0
    if args.command == "export-letuen":
        result = export_letuen_bundle(Path(args.run), Path(args.output), Path(args.composition_request) if args.composition_request else None)
        print(f"Exported LetUen bundle: {result['output_dir']}")
        print(f"Exported report: {result['report_index']}")
        print(f"Exported vault: {result['vault_dir']}")
        print(f"Exported data: {result['data_dir']}")
        print(f"Exported anchors: {result['anchors_path']} count={result['anchor_count']}")
        if result.get("composition_plan_path"):
            print(f"Exported composition plan: {result['composition_plan_path']}")
        return 0
    if args.command == "package-letuen-skill":
        manifest = package_letuen_skill_pack(Path(args.output), version=args.version)
        print(f"Packaged LetUen skill anchor pack: {Path(args.output) / 'letuen-skill-anchor-pack'}")
        print(f"Version: {manifest['version']}")
        print(f"Method skills: {manifest['skill_count']}")
        print(f"Archive: {Path(args.output) / ('letuen-skill-anchor-pack-' + args.version + '.zip')}")
        return 0
    if args.command == "export-all":
        output_dir = Path(args.output)
        export_site_shell(output_dir)
        vault = export_vault(Path(args.run), output_dir / "vault")
        data = export_data(Path(args.run), output_dir / "data")
        report = export_report(Path(args.run), output_dir / "report")
        print(f"Exported report: {report['index']}")
        print(f"Exported vault: {vault['output_dir']}")
        print(f"Exported data: {output_dir / 'data'} rows={data['row_counts']}")
        return 0
    return 1




def init_evaluation_folder(name: str, source: str, output_root: Path, model: str = "unknown") -> dict:
    safe_name = _safe_eval_name(name)
    evaluation_dir = output_root / safe_name
    evaluation_dir.mkdir(parents=True, exist_ok=True)
    request_path = evaluation_dir / "composition_request.yaml"
    review_path = evaluation_dir / "evaluation.md"
    sources_path = evaluation_dir / "source.yaml"
    request_text = f"""schema_version: 1
goal:
  type: temporary_composition
  description: Evaluate whether LetUen can select useful workflow, validation, evidence, risk, and reuse anchors for {name}.
constraints:
  avoid_full_workflow: true
  preserve_existing_skill_structure: true
  target_agent: codex
  target_project_path: null
  allowed_side_effects:
    - none
    - reads_files
  require_dry_run: false
selected_anchor_types:
  - workflow_anchor
  - validation_anchor
  - evidence_anchor
  - risk_anchor
  - reuse_anchor
selected_source_skills: []
excluded_source_skills: []
preferred_outputs:
  - markdown
  - json
"""
    source_text = f"""source_name: {name}
source_url_or_path: {source}
commit_or_ref: unknown
skill_count: unknown
model_provider: unknown
model_name: {model}
run_id: pending
evaluator: pending
notes: pending
"""
    review_text = f"""# LetUen Evaluation: {name}

## Summary
- Source: `{source}`
- Model: `{model}`
- Run: pending
- Overall score: pending

## Commands

```powershell
$env:PYTHONPATH='src'
python -m asa run --config anatomy.config.yaml --limit-skills 3
python -m asa export-letuen `
  --run runs\\<run-id> `
  --output {evaluation_dir.as_posix()}/letuen `
  --composition-request {request_path.as_posix()}
```

## Scores
| Dimension | Score | Notes |
|---|---:|---|
| Decomposition completeness | | |
| Anchor usefulness | | |
| Composition quality | | |
| Report readability | | |
| Obsidian learning value | | |
| Non-destructive safety | | |

## Best Findings

## Missing Or Weak Areas

## Unsafe Or Overstated Claims

## Recommended Improvements

## Keep / Change / Drop Decision
"""
    if not request_path.exists():
        request_path.write_text(request_text, encoding="utf-8")
    if not sources_path.exists():
        sources_path.write_text(source_text, encoding="utf-8")
    if not review_path.exists():
        review_path.write_text(review_text, encoding="utf-8")
    return {
        "evaluation_dir": str(evaluation_dir),
        "composition_request": str(request_path),
        "source_note": str(sources_path),
        "review_note": str(review_path),
    }


def _safe_eval_name(name: str) -> str:
    safe = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    while "--" in safe:
        safe = safe.replace("--", "-")
    return safe or "evaluation"

def export_letuen_bundle(run_dir: Path, output_dir: Path, composition_request: Path | None = None) -> dict:
    export_site_shell(output_dir)
    anchors_path = output_dir / "anchors" / "anchors.json"
    anchors = export_anchors(run_dir, anchors_path)
    composition_plan_path = None
    if composition_request:
        composition_plan_path = output_dir / "anchors" / "composition_plan.json"
        plan_anchor_composition(anchors_path, composition_request, composition_plan_path)
    vault = export_vault(run_dir, output_dir / "vault")
    data = export_data(run_dir, output_dir / "data")
    report = export_report(run_dir, output_dir / "report")
    manifest = {
        "schema_version": 1,
        "output_dir": str(output_dir),
        "report_index": str(report["index"]),
        "vault_dir": str(vault["output_dir"]),
        "data_dir": str(output_dir / "data"),
        "anchors_path": str(anchors_path),
        "anchor_count": anchors["anchor_count"],
        "composition_plan_path": str(composition_plan_path) if composition_plan_path else None,
        "data_rows": data["row_counts"],
        "vault_notes": len(vault["notes"]),
        "report_skill_pages": len(report["skill_pages"]),
    }
    write_json(output_dir / "letuen_manifest.json", manifest)
    return manifest

def export_site_shell(output_dir: Path) -> None:
    source_dir = Path(__file__).resolve().parents[2] / "site"
    output_dir.mkdir(parents=True, exist_ok=True)
    for file_name in ["index.html", "styles.css", "script.js"]:
        source_file = source_dir / file_name
        if source_file.exists():
            destination = output_dir / file_name
            if source_file.resolve() != destination.resolve():
                shutil.copyfile(source_file, destination)
    for directory_name in ["cinema", "repo", "data", "graph", "models"]:
        source_child = source_dir / directory_name
        target_child = output_dir / directory_name
        if not source_child.exists():
            continue
        if source_child.resolve() == target_child.resolve():
            continue
        if target_child.exists():
            shutil.rmtree(target_child)
        shutil.copytree(source_child, target_child)


def print_review_summary(summary: dict) -> None:
    print(f"Reviewed skills: {summary['reviewed_skill_count']}")
    print(f"Status counts: {summary['status_counts']}")
    print(f"Average scores: {summary['average_scores']}")
    print(f"Totals: {summary['totals']}")
    for skill in summary["skills"]:
        print(
            f"- {skill['skill_id']}: {skill['status']}, "
            f"approved={skill['approved_for_publish']}, issues={skill['issue_count']}"
        )
