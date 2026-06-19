from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def text_value(value: Any, language: str = "zh") -> str:
    if isinstance(value, dict):
        return str(value.get(language) or value.get("en") or value.get("zh") or value.get("name") or value.get("id") or "")
    if value is None:
        return ""
    return str(value)


def summarize_run(run_dir: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    patterns_path = run_dir / "patterns" / "patterns.json"
    patterns = read_json(patterns_path) if patterns_path.exists() else {"patterns": []}
    run_meta = read_json(run_dir / "run.json") if (run_dir / "run.json").exists() else {}
    for skill_dir in sorted((run_dir / "skills").glob("*")):
        if not skill_dir.is_dir():
            continue
        structure = read_json(skill_dir / "structure_analysis.json")
        workflow = read_json(skill_dir / "workflow_analysis.json")
        review = read_json(skill_dir / "review_report.json")
        scores = review.get("scores", {}) or {}
        rows.append({
            "run_id": run_dir.name,
            "provider": run_meta.get("provider", "unknown"),
            "model": run_meta.get("model") or run_meta.get("provider", "unknown"),
            "skill_id": skill_dir.name,
            "skill_name": structure.get("frontmatter", {}).get("name") or structure.get("skill_id") or skill_dir.name,
            "summary_zh": text_value(structure.get("summary", {})),
            "skill_type": structure.get("skill_type", {}).get("primary", "unknown"),
            "workflow_steps": len(workflow.get("workflow_steps", []) or []),
            "review_status": review.get("status", "unknown"),
            "review_issues": len(review.get("issues", []) or []),
            "patterns": len(patterns.get("patterns", []) or []),
            "evidence_score": scores.get("evidence_score"),
            "structure_score": scores.get("structure_score"),
            "workflow_score": scores.get("workflow_score"),
            "pattern_score": scores.get("pattern_score"),
            "bilingual_score": scores.get("bilingual_score"),
            "obsidian_score": scores.get("obsidian_score"),
        })
    return rows


def write_outputs(rows: list[dict[str, Any]], output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    (output / "model_compare.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (output / "model_compare.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")
    headers = ["run_id", "model", "skill_name", "workflow_steps", "review_status", "review_issues", "patterns", "evidence_score", "structure_score", "workflow_score", "pattern_score", "bilingual_score", "obsidian_score"]
    lines = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    (output / "model_compare.md").write_text("# Model Compare\n\n" + "\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare Agent Skill Anatomy runs.")
    parser.add_argument("runs", nargs="+", help="Run directories to compare.")
    parser.add_argument("--output", default="benchmark/model-compare", help="Output directory.")
    args = parser.parse_args()
    rows: list[dict[str, Any]] = []
    for run in args.runs:
        rows.extend(summarize_run(Path(run)))
    write_outputs(rows, Path(args.output))
    print(f"Compared {len(rows)} skill result(s): {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
