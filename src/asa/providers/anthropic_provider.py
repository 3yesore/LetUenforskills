from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


class AnthropicProvider:
    """Anthropic Messages API adapter for schema-guided JSON agent calls."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.anthropic.com/v1",
        api_key_env: str = "ANTHROPIC_API_KEY",
        anthropic_version: str = "2023-06-01",
    ) -> None:
        self.api_key_env = api_key_env
        self.api_key = api_key or os.environ.get(api_key_env)
        self.base_url = base_url.rstrip("/")
        self.anthropic_version = anthropic_version
        if not self.api_key:
            raise ValueError(f"{api_key_env} is required for the Anthropic provider.")

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
        model: str = "claude-sonnet-4-5-20250929",
        temperature: float = 0,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        schema_text = json.dumps(schema, ensure_ascii=False, indent=2)
        payload_text = json.dumps(user_payload, ensure_ascii=False, indent=2)
        request_body: dict[str, Any] = {
            "model": model,
            "max_tokens": max_output_tokens or 8192,
            "temperature": temperature,
            "system": system_prompt
            + "\n\nReturn only valid JSON matching this JSON Schema. Do not wrap it in Markdown.\n"
            + schema_text,
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": payload_text}],
                }
            ],
        }
        raw_response = self._post_json("/messages", request_body)
        output_text = extract_output_text(raw_response)
        try:
            return json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Anthropic response was not valid JSON: {exc}\n{output_text[:1000]}") from exc

    def _post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": self.anthropic_version,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Anthropic API error {exc.code}: {error_body}") from exc


def extract_output_text(response: dict[str, Any]) -> str:
    chunks: list[str] = []
    for item in response.get("content", []):
        if item.get("type") == "text" and isinstance(item.get("text"), str):
            chunks.append(item["text"])
    if chunks:
        return "".join(chunks).strip()
    raise ValueError(f"Could not extract output text from Anthropic response: {response.keys()}")