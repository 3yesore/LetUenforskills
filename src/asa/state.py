from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from .jsonio import write_json


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_run_id() -> str:
    return utc_now().replace(":", "").replace("-", "")


class RunState:
    def __init__(self, run_dir: Path, run_id: str) -> None:
        self.run_dir = run_dir
        self.data = {
            "run_id": run_id,
            "status": "CREATED",
            "stages": {},
            "skills": {},
            "updated_at": utc_now(),
        }

    def set_stage(self, stage: str, status: str) -> None:
        self.data["stages"][stage] = status
        self.data["updated_at"] = utc_now()
        self.write()

    def set_status(self, status: str) -> None:
        self.data["status"] = status
        self.data["updated_at"] = utc_now()
        self.write()

    def set_skill_stage(self, skill_id: str, stage: str, status: str) -> None:
        self.data["skills"].setdefault(skill_id, {})[stage] = status
        self.data["updated_at"] = utc_now()
        self.write()

    def write(self) -> None:
        write_json(self.run_dir / "state.json", self.data)

