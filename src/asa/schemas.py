from __future__ import annotations

from pathlib import Path
from typing import Any

from .jsonio import read_json
from .paths import project_path


class SchemaValidationError(ValueError):
    pass


def validate_json(data: Any, schema_path: Path) -> None:
    schema = read_json(schema_path)
    _validate(data, schema, "$", schema)


def validate_named_schema(data: Any, name: str) -> None:
    validate_json(data, project_path("schemas", name))


def _validate(data: Any, schema: dict[str, Any], path: str, root_schema: dict[str, Any]) -> None:
    if "$ref" in schema:
        schema = _resolve_ref(schema["$ref"], root_schema)

    if "const" in schema and data != schema["const"]:
        raise SchemaValidationError(f"{path} must equal {schema['const']!r}")
    if "enum" in schema and data not in schema["enum"]:
        raise SchemaValidationError(f"{path} must be one of {schema['enum']!r}")

    schema_type = schema.get("type")
    if schema_type is not None and not _matches_type(data, schema_type):
        raise SchemaValidationError(f"{path} must be {schema_type}, got {type(data).__name__}")

    if isinstance(data, dict):
        for key in schema.get("required", []):
            if key not in data:
                raise SchemaValidationError(f"{path}.{key} is required")
        properties = schema.get("properties", {})
        for key, value in data.items():
            if key in properties:
                _validate(value, properties[key], f"{path}.{key}", root_schema)

    if isinstance(data, list):
        item_schema = schema.get("items")
        if item_schema:
            for index, item in enumerate(data):
                _validate(item, item_schema, f"{path}[{index}]", root_schema)


def _resolve_ref(ref: str, root_schema: dict[str, Any]) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise SchemaValidationError(f"Only local refs are supported: {ref}")
    current: Any = root_schema
    for part in ref[2:].split("/"):
        current = current[part]
    return current


def _matches_type(data: Any, schema_type: str | list[str]) -> bool:
    if isinstance(schema_type, list):
        return any(_matches_type(data, item) for item in schema_type)
    if schema_type == "object":
        return isinstance(data, dict)
    if schema_type == "array":
        return isinstance(data, list)
    if schema_type == "string":
        return isinstance(data, str)
    if schema_type == "integer":
        return isinstance(data, int) and not isinstance(data, bool)
    if schema_type == "boolean":
        return isinstance(data, bool)
    if schema_type == "null":
        return data is None
    return True

