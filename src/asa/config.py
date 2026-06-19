from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if value in {"true", "false"}:
        return value == "true"
    if value in {"null", "~"}:
        return None
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1]
    if value.startswith("'") and value.endswith("'"):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        return value


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml  # type: ignore
    except ImportError:
        yaml = None
    if yaml is not None:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        return loaded or {}

    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    pending_key: tuple[int, dict[str, Any], str] | None = None

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        line = raw_line.strip()

        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]

        if line.startswith("- "):
            item_text = line[2:].strip()
            if not isinstance(parent, list):
                if pending_key is None:
                    raise ValueError(f"List item without list parent in {path}: {raw_line}")
                pending_indent, pending_parent, key = pending_key
                if indent <= pending_indent:
                    raise ValueError(f"Invalid list indentation in {path}: {raw_line}")
                new_list: list[Any] = []
                pending_parent[key] = new_list
                stack.append((indent - 1, new_list))
                parent = new_list
            if ":" in item_text:
                key, value = item_text.split(":", 1)
                item: dict[str, Any] = {key.strip(): parse_scalar(value) if value.strip() else {}}
                parent.append(item)
                stack.append((indent, item))
                if not value.strip():
                    pending_key = (indent, item, key.strip())
            else:
                parent.append(parse_scalar(item_text))
            continue

        if ":" not in line:
            raise ValueError(f"Unsupported YAML line in {path}: {raw_line}")
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if not isinstance(parent, dict):
            raise ValueError(f"Mapping entry without mapping parent in {path}: {raw_line}")
        if value:
            parent[key] = parse_scalar(value)
            pending_key = None
        else:
            parent[key] = {}
            pending_key = (indent, parent, key)
            stack.append((indent, parent[key]))
    return root


@dataclass(frozen=True)
class RuntimeConfig:
    path: Path
    data: dict[str, Any]

    @property
    def language(self) -> str:
        return self.data.get("project", {}).get("language", "bilingual")

    @property
    def sources_file(self) -> Path:
        raw_path = self.data.get("sources_file", "sources.yaml")
        resolved = (self.path.parent / raw_path).resolve()
        if resolved.exists():
            return resolved
        example = resolved.with_name(resolved.stem + ".example" + resolved.suffix)
        if example.exists():
            return example
        return resolved

    @property
    def vault_path(self) -> Path:
        raw_path = self.data.get("obsidian", {}).get("vault_path", "./vault")
        return (self.path.parent / raw_path).resolve()

    @property
    def default_provider(self) -> str:
        return self.data.get("providers", {}).get("default", {}).get("type", "mock")

    @property
    def default_model(self) -> str:
        return self.data.get("providers", {}).get("default", {}).get("model", "mock")

    def provider_settings(self, provider_name: str = "default") -> dict[str, Any]:
        return self.data.get("providers", {}).get(provider_name, {})


def load_config(path: Path) -> RuntimeConfig:
    return RuntimeConfig(path=path.resolve(), data=parse_simple_yaml(path))


def load_sources(path: Path) -> list[dict[str, Any]]:
    data = parse_simple_yaml(path)
    sources = data.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("sources file must contain a top-level sources list")
    return sources
