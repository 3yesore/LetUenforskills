from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from .artifact_normalizer import normalize_artifact
from .jsonio import read_json, write_json
from .providers import ModelProvider
from .resources import load_schema
from .schemas import SchemaValidationError, validate_named_schema
from .errors import write_error_artifact


def generate_validated_json(
    *,
    provider: ModelProvider,
    system_prompt: str,
    user_payload: dict[str, Any],
    schema_name: str,
    artifact_path: Path,
    model: str,
    max_attempts: int = 2,
) -> dict[str, Any]:
    schema = load_schema(schema_name)
    current_payload = deepcopy(user_payload)
    last_error: Exception | None = None

    for attempt in range(1, max_attempts + 1):
        output = provider.generate_json(
            system_prompt=system_prompt,
            user_payload=current_payload,
            schema=schema,
            model=model,
        )
        try:
            output, normalization_changes = normalize_artifact(schema_name, output)
            validate_named_schema(output, schema_name)
            if normalization_changes:
                write_json(artifact_path.with_name(artifact_path.stem + ".normalization.json"), {"changes": normalization_changes})
            write_json(artifact_path, output)
            return output
        except SchemaValidationError as exc:
            last_error = exc
            if attempt >= max_attempts:
                break
            current_payload = deepcopy(user_payload)
            current_payload["previous_invalid_output"] = output
            current_payload["previous_validation_error"] = str(exc)
            current_payload["retry_instruction"] = (
                "Your previous output failed schema validation. "
                "Return corrected JSON only, matching the schema exactly."
            )

    message = f"Provider output failed schema validation after {max_attempts} attempt(s): {last_error}"
    write_error_artifact(
        artifact_path.with_suffix(".error.json"),
        code="SCHEMA_VALIDATION_FAILED",
        stage=artifact_path.stem,
        message=message,
        recoverable=True,
        context={"schema_name": schema_name},
    )
    raise SchemaValidationError(message)


def generate_or_reuse_validated_json(
    *,
    provider: ModelProvider,
    system_prompt: str,
    user_payload: dict[str, Any],
    schema_name: str,
    artifact_path: Path,
    model: str,
    resume: bool,
    max_attempts: int = 2,
) -> dict[str, Any]:
    if resume and artifact_path.exists():
        existing = read_json(artifact_path)
        validate_named_schema(existing, schema_name)
        return existing
    return generate_validated_json(
        provider=provider,
        system_prompt=system_prompt,
        user_payload=user_payload,
        schema_name=schema_name,
        artifact_path=artifact_path,
        model=model,
        max_attempts=max_attempts,
    )
