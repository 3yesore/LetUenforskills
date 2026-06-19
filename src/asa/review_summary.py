from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .jsonio import read_json


SCORE_KEYS = [
    "evidence_score",
    "structure_score",
    "workflow_score",
    "pattern_score",
    "bilingual_score",
    "obsidian_score",
]


def summarize_run_reviews(run_dir: Path) -> dict[str, Any]:
    review_paths = sorted((run_dir / "skills").glob("*/review_report.json")) if (run_dir / "skills").exists() else []
    status_counts: Counter[str] = Counter()
    score_totals: defaultdict[str, int] = defaultdict(int)
    totals = {
        "issues": 0,
        "unsupported_claims": 0,
        "missing_evidence": 0,
        "over_inference": 0,
    }
    skills: list[dict[str, Any]] = []

    for path in review_paths:
        review = read_json(path)
        skill_id = review.get("skill_id") or path.parent.name
        status = review.get("status", "unknown")
        scores = review.get("scores", {})
        status_counts[status] += 1
        for key in SCORE_KEYS:
            score_totals[key] += int(scores.get(key, 0))
        for key in totals:
            totals[key] += len(review.get(key, []))
        skills.append(
            {
                "skill_id": skill_id,
                "status": status,
                "scores": scores,
                "issue_count": len(review.get("issues", [])),
                "unsupported_claim_count": len(review.get("unsupported_claims", [])),
                "missing_evidence_count": len(review.get("missing_evidence", [])),
                "over_inference_count": len(review.get("over_inference", [])),
                "approved_for_publish": bool(review.get("approved_for_publish", {}).get("value", False)),
                "path": str(path.relative_to(run_dir)),
            }
        )

    reviewed_count = len(review_paths)
    average_scores = {
        key: (score_totals[key] / reviewed_count if reviewed_count else 0)
        for key in SCORE_KEYS
    }
    return {
        "run_dir": str(run_dir),
        "reviewed_skill_count": reviewed_count,
        "status_counts": dict(status_counts),
        "average_scores": average_scores,
        "totals": totals,
        "skills": skills,
    }

