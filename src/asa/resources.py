from __future__ import annotations

from .jsonio import read_json, read_text
from .paths import project_path


def load_prompt(name: str) -> str:
    return read_text(project_path("prompts", name))


def load_schema(name: str) -> dict:
    return read_json(project_path("schemas", name))

