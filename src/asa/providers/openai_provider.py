from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.request
from typing import Any


class OpenAIProvider:
    """OpenAI-compatible adapter for schema-grounded JSON agent calls."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "https://api.openai.com/v1",
        api_key_env: str = "OPENAI_API_KEY",
        api_mode: str = "responses",
    ) -> None:
        self.api_key_env = api_key_env
        self.api_key = api_key or os.environ.get(api_key_env)
        self.base_url = base_url.rstrip("/")
        self.api_mode = api_mode
        if not self.api_key:
            raise ValueError(f"{api_key_env} is required for the OpenAI-compatible provider.")

    def generate_json(
        self,
        *,
        system_prompt: str,
        user_payload: dict[str, Any],
        schema: dict[str, Any],
        model: str = "gpt-5.2",
        temperature: float = 0,
        max_output_tokens: int | None = None,
    ) -> dict[str, Any]:
        if self.api_mode == "chat_completions":
            raw_response = self._post_json(
                "/chat/completions",
                chat_completion_body(system_prompt, user_payload, schema, model, temperature, max_output_tokens),
            )
        else:
            raw_response = self._post_json(
                "/responses",
                responses_body(system_prompt, user_payload, schema, model, temperature, max_output_tokens),
            )
        output_text = extract_output_text(raw_response)
        try:
            return json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise ValueError(f"OpenAI-compatible response was not valid JSON: {exc}\n{output_text[:1000]}") from exc

    def _post_json(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        request = urllib.request.Request(
            self.base_url + path,
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"OpenAI-compatible API error {exc.code}: {error_body}") from exc


def responses_body(
    system_prompt: str,
    user_payload: dict[str, Any],
    schema: dict[str, Any],
    model: str,
    temperature: float | None,
    max_output_tokens: int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": system_prompt + "\n\nReturn only valid JSON matching the provided schema. Do not wrap it in Markdown.",
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(user_payload, ensure_ascii=False, indent=2),
                    }
                ],
            },
        ],
        "text": {
            "format": {
                "type": "json_schema",
                "name": schema_name(schema),
                "schema": schema,
                "strict": False,
            }
        },
    }
    if max_output_tokens is not None:
        body["max_output_tokens"] = max_output_tokens
    if temperature is not None:
        body["temperature"] = temperature
    return body


def chat_completion_body(
    system_prompt: str,
    user_payload: dict[str, Any],
    schema: dict[str, Any],
    model: str,
    temperature: float | None,
    max_output_tokens: int | None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": system_prompt + "\n\nReturn only valid JSON matching this JSON Schema. Do not wrap it in Markdown.\n" + json.dumps(schema, ensure_ascii=False),
            },
            {
                "role": "user",
                "content": json.dumps(user_payload, ensure_ascii=False, indent=2),
            },
        ],
        "stream": False,
    }
    if max_output_tokens is not None:
        body["max_tokens"] = max_output_tokens
    if temperature is not None:
        body["temperature"] = temperature
    return body


def schema_name(schema: dict[str, Any]) -> str:
    title = schema.get("title", "asa_artifact")
    cleaned = "".join(character if character.isalnum() else "_" for character in title.lower())
    return cleaned[:64] or "asa_artifact"


def extract_output_text(response: dict[str, Any]) -> str:
    if isinstance(response.get("output_text"), str):
        return response["output_text"]
    choices = response.get("choices")
    if isinstance(choices, list) and choices:
        message = choices[0].get("message", {})
        if isinstance(message.get("content"), str) and message["content"].strip():
            return extract_json_candidate(message["content"])
        if isinstance(message.get("reasoning_content"), str):
            return extract_json_candidate(message["reasoning_content"])
    chunks: list[str] = []
    for item in response.get("output", []):
        for content in item.get("content", []):
            if isinstance(content.get("text"), str):
                chunks.append(content["text"])
    if chunks:
        return "".join(chunks)
    raise ValueError(f"Could not extract output text from OpenAI-compatible response: {response.keys()}")


def extract_json_candidate(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = re.sub(r"^```(?:json)?\s*", "", stripped, flags=re.IGNORECASE).strip()
        stripped = re.sub(r"\s*```$", "", stripped).strip()
    if stripped.startswith("{") or stripped.startswith("["):
        return stripped
    candidates = re.findall(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", stripped, flags=re.DOTALL)
    if candidates:
        return candidates[-1].strip()
    array_candidates = re.findall(r"\[[\s\S]*\]", stripped)
    if array_candidates:
        return array_candidates[-1].strip()
    return stripped
