from __future__ import annotations

from pathlib import Path
from typing import Any

from .jsonio import write_json
from .state import utc_now


def write_error_artifact(
    path: Path,
    *,
    code: str,
    stage: str,
    message: str,
    recoverable: bool,
    context: dict[str, Any] | None = None,
) -> None:
    write_json(
        path,
        {
            "code": code,
            "stage": stage,
            "message": message,
            "recoverable": recoverable,
            "context": context or {},
            "created_at": utc_now(),
        },
    )

