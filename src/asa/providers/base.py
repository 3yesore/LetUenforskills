from __future__ import annotations

from typing import Any, Protocol


class ModelProvider(Protocol):
    def generate_json(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
        model: str = "mock",
        temperature: float = 0,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        ...

