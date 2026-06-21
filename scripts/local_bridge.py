from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import uuid
import time
import hashlib
import urllib.error
import urllib.parse
import urllib.request
import shlex
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

HOST = "127.0.0.1"
PORT = 8765

JOBS: dict[str, dict[str, Any]] = {}
JOBS_LOCK = threading.Lock()


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    origin = handler.headers.get("Origin") or "*"
    if origin.startswith("http://localhost:") or origin.startswith("http://127.0.0.1:"):
        handler.send_header("Access-Control-Allow-Origin", origin)
    else:
        handler.send_header("Access-Control-Allow-Origin", "http://localhost:4173")
    handler.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")
    handler.end_headers()
    handler.wfile.write(body)


def job_snapshot(job_id: str) -> dict[str, Any] | None:
    with JOBS_LOCK:
        job = JOBS.get(job_id)
        return dict(job) if job else None


def update_job(job_id: str, **updates: Any) -> None:
    with JOBS_LOCK:
        job = JOBS.setdefault(job_id, {"job_id": job_id})
        job.update(updates)


def append_job_log(job_id: str, stage: str, message: str) -> None:
    with JOBS_LOCK:
        job = JOBS.setdefault(job_id, {"job_id": job_id})
        logs = list(job.get("logs", []))
        logs.append({"stage": stage, "message": message})
        job["logs"] = logs[-80:]
        job["stage"] = stage
        job["message"] = message


def start_analysis_job(payload: dict[str, Any]) -> dict[str, Any]:
    job_id = uuid.uuid4().hex[:12]
    update_job(job_id, ok=True, status="queued", stage="queued", progress=0, logs=[])
    thread = threading.Thread(target=run_analysis_job, args=(job_id, payload), daemon=True)
    thread.start()
    return {"ok": True, "job_id": job_id, "status": "queued"}


def run_analysis_job(job_id: str, payload: dict[str, Any]) -> None:
    try:
        update_job(job_id, status="running", progress=5)
        append_job_log(job_id, "queued", "analysis worker started")
        result = run_local_analysis(payload, job_id=job_id)
        if result.get("ok"):
            update_job(job_id, **result, status="completed", progress=100)
            append_job_log(job_id, "ready", f"completed {result.get('run_id', 'run')}")
        else:
            update_job(job_id, **result, status="failed", progress=100)
            append_job_log(job_id, result.get("stage", "failed"), result.get("message", "analysis failed"))
    except Exception as exc:  # noqa: BLE001 - local bridge job surface
        update_job(job_id, ok=False, status="failed", stage="failed", progress=100, message=str(exc))
        append_job_log(job_id, "failed", str(exc))


def read_request_json(handler: BaseHTTPRequestHandler) -> dict[str, Any]:
    length = int(handler.headers.get("Content-Length", "0") or "0")
    if length <= 0:
        return {}
    raw = handler.rfile.read(length).decode("utf-8")
    return json.loads(raw or "{}")


def looks_like_api_key(value: str) -> bool:
    lowered = value.lower()
    return bool(value) and (lowered.startswith(("sk-", "sk_")) or len(value) >= 32 and not re.fullmatch(r"[A-Z_][A-Z0-9_]*", value))


def normalized_api_key_env(payload: dict[str, Any], provider: str | None = None) -> str:
    raw_env = str(payload.get("api_key_env") or "").strip()
    if raw_env and not looks_like_api_key(raw_env):
        return raw_env
    provider_name = (provider or str(payload.get("provider") or "openai")).strip().upper().replace("-", "_")
    if provider_name == "ANTHROPIC":
        return "ANTHROPIC_API_KEY"
    if "DEEPSEEK" in str(payload.get("model") or "").upper() or "DEEPSEEK" in str(payload.get("base_url") or "").upper():
        return "DEEPSEEK_API_KEY"
    return "LETUEN_API_KEY"


def resolve_api_key(payload: dict[str, Any]) -> str:
    api_key = str(payload.get("api_key") or "").strip()
    if api_key:
        return api_key
    raw_env = str(payload.get("api_key_env") or "").strip()
    if looks_like_api_key(raw_env):
        return raw_env
    api_key_env = normalized_api_key_env(payload)
    return os.environ.get(api_key_env, "")


GITHUB_URL_RE = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$")


def sanitize_config_file(value: str) -> str:
    config_file = value.strip() or "anatomy.config.example.yaml"
    if any(part in config_file for part in ["..", "/", "\\"]):
        raise ValueError("config_file must be a repository-local file name")
    if not config_file.endswith((".yaml", ".yml")):
        raise ValueError("config_file must be a YAML file")
    config_path = ROOT / config_file
    if not config_path.exists():
        raise FileNotFoundError(f"config file not found: {config_file}")
    return config_file


def sanitize_github_url(value: str) -> str:
    url = value.strip().rstrip("/")
    if not GITHUB_URL_RE.match(url):
        raise ValueError("Only https://github.com/<owner>/<repo> URLs are accepted by the local bridge")
    return url


def source_name_from_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    parts = [part for part in parsed.path.strip("/").split("/") if part]
    return "-".join(parts[:2]) if len(parts) >= 2 else "github-source"


def safe_local_path(value: str) -> Path:
    raw = str(value or "").strip()
    if not raw:
        raise ValueError("path is required")
    path = Path(raw).expanduser().resolve()
    allowed_roots = [ROOT.resolve(), (ROOT / "site").resolve(), (ROOT / "dist").resolve()]
    if not any(path == root or root in path.parents for root in allowed_roots):
        raise ValueError("path must be inside this project, site, or dist directory")
    if not path.exists():
        raise FileNotFoundError(f"path not found: {path}")
    return path


def obsidian_executable() -> Path | None:
    if not sys.platform.startswith("win"):
        return None
    try:
        import winreg  # type: ignore
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"obsidian\shell\open\command") as key:
            command, _ = winreg.QueryValueEx(key, None)
        parts = shlex.split(command, posix=False)
        if parts:
            exe = Path(parts[0].strip('"')).expanduser()
            return exe if exe.exists() else None
    except Exception:
        return None
    return None


def open_local_folder(path: Path) -> None:
    if sys.platform.startswith("win"):
        os.startfile(str(path))  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    else:
        subprocess.Popen(["xdg-open", str(path)])

def obsidian_state_file() -> Path | None:
    if sys.platform.startswith("win"):
        appdata = os.environ.get("APPDATA")
        return Path(appdata) / "obsidian" / "obsidian.json" if appdata else None
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "obsidian" / "obsidian.json"
    return Path.home() / ".config" / "obsidian" / "obsidian.json"


def register_obsidian_vault(vault_path: Path) -> dict[str, Any]:
    state_file = obsidian_state_file()
    if state_file is None:
        raise RuntimeError("Obsidian state file is unavailable on this platform")
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state: dict[str, Any] = {"vaults": {}}
    if state_file.exists():
        try:
            state = json.loads(state_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            backup = state_file.with_suffix(f".json.bak_{int(time.time())}")
            shutil.copy2(state_file, backup)
            state = {"vaults": {}}
    vaults = state.setdefault("vaults", {})
    resolved = str(vault_path.resolve())
    existing_id = None
    for vault_id, item in vaults.items():
        try:
            if Path(str(item.get("path", ""))).resolve() == vault_path.resolve():
                existing_id = vault_id
                break
        except Exception:
            continue
    vault_id = existing_id or hashlib.sha1(resolved.encode("utf-8")).hexdigest()[:16]
    vaults[vault_id] = {"path": resolved, "ts": int(time.time() * 1000), "open": True, "name": "Agent Skill Anatomy Vault"}
    for other_id, item in vaults.items():
        if other_id != vault_id and isinstance(item, dict):
            item["open"] = False
    backup_path = None
    if state_file.exists():
        backup_path = state_file.with_suffix(f".json.bak_asa_{int(time.time())}")
        shutil.copy2(state_file, backup_path)
    state_file.write_text(json.dumps(state, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    return {"vault_id": vault_id, "vault_name": "Agent Skill Anatomy Vault", "state_file": str(state_file), "backup": str(backup_path) if backup_path else None}


def open_uri(uri: str) -> None:
    if sys.platform.startswith("win"):
        os.startfile(uri)  # type: ignore[attr-defined]
    elif sys.platform == "darwin":
        subprocess.Popen(["open", uri])
    else:
        subprocess.Popen(["xdg-open", uri])


def stop_obsidian_processes() -> int:
    if not sys.platform.startswith("win"):
        return 0
    stopped = 0
    try:
        completed = subprocess.run(
            ["taskkill", "/IM", "Obsidian.exe", "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        stopped = 1 if completed.returncode == 0 else 0
        time.sleep(1.2)
    except Exception:
        stopped = 0
    return stopped


def launch_obsidian_uri(uri: str) -> str:
    exe = obsidian_executable()
    if exe and sys.platform.startswith("win"):
        subprocess.Popen([str(exe), uri], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return "executable-uri"
    open_uri(uri)
    return "protocol-uri"

def open_obsidian_target(payload: dict[str, Any]) -> dict[str, Any]:
    path = safe_local_path(str(payload.get("path") or ""))
    vault_path = path.parent if path.is_file() else path
    entry_path = path if path.is_file() else vault_path / "00 Maps" / "Agent Skill Anatomy MOC.md"
    if not entry_path.exists():
        entry_path = path
    vault_uri = "obsidian://open?path=" + urllib.parse.quote(str(vault_path).replace("\\", "/"), safe="")
    path_entry_uri = "obsidian://open?path=" + urllib.parse.quote(str(entry_path).replace("\\", "/"), safe="") + "&paneType=tab"
    try:
        relative_entry = entry_path.relative_to(vault_path).with_suffix("").as_posix() if entry_path.is_file() else "00 Maps/Agent Skill Anatomy MOC"
    except ValueError:
        relative_entry = "00 Maps/Agent Skill Anatomy MOC"
    mode = str(payload.get("mode") or "obsidian").strip().lower()
    if mode in {"folder", "local", "explorer"}:
        try:
            open_local_folder(vault_path)
            return {"ok": True, "message": "opened local vault folder", "path": str(path), "entry_path": str(entry_path), "vault_path": str(vault_path), "uri": vault_uri, "mode": "folder"}
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "message": f"open local folder failed: {exc}", "path": str(path), "entry_path": str(entry_path), "vault_path": str(vault_path), "uri": vault_uri, "mode": "folder"}
    try:
        registration = register_obsidian_vault(vault_path)
        vault_name = str(registration.get("vault_name") or "Agent Skill Anatomy Vault")
        vault_name_uri = "obsidian://open?vault=" + urllib.parse.quote(vault_name, safe="") + "&file=" + urllib.parse.quote(relative_entry, safe="") + "&paneType=tab"
        vault_id_uri = "obsidian://open?vault=" + urllib.parse.quote(str(registration["vault_id"]), safe="") + "&file=" + urllib.parse.quote(relative_entry, safe="") + "&paneType=tab"
        stopped = stop_obsidian_processes() if sys.platform.startswith("win") else 0
        launch_mode = launch_obsidian_uri(path_entry_uri)
        return {"ok": True, "message": "registered vault, restarted Obsidian, and sent note open request", "path": str(path), "entry_path": str(entry_path), "vault_path": str(vault_path), "uri": path_entry_uri, "vault_name_uri": vault_name_uri, "vault_id_uri": vault_id_uri, "mode": "obsidian", "launch_mode": launch_mode, "obsidian_restarted": bool(stopped), "vault_name": vault_name, **registration}
    except Exception as exc:  # noqa: BLE001
        try:
            open_local_folder(vault_path)
            return {"ok": False, "message": f"Obsidian open failed; opened local folder instead: {exc}", "path": str(path), "entry_path": str(entry_path), "vault_path": str(vault_path), "uri": path_entry_uri, "mode": "folder"}
        except Exception as folder_exc:  # noqa: BLE001
            return {"ok": False, "message": f"open failed: {folder_exc}", "path": str(path), "entry_path": str(entry_path), "vault_path": str(vault_path), "uri": path_entry_uri, "mode": "obsidian"}

def override_provider_config(base_config: str, payload: dict[str, Any]) -> str:
    provider = str(payload.get("provider") or "").strip()
    model = str(payload.get("model") or "").strip()
    base_url = str(payload.get("base_url") or "").strip().rstrip("/")
    api_key_env = normalized_api_key_env(payload, provider)
    api_mode = str(payload.get("api_mode") or "").strip()
    if not any([provider, model, base_url, api_key_env, api_mode]):
        return base_config
    provider_block = provider or "openai"
    model_block = model or "mock"
    lines = [
        "providers:",
        "  default:",
        f"    type: {provider_block}",
        f"    model: {model_block}",
    ]
    if base_url and base_url != "local":
        lines.append(f"    base_url: {base_url}")
    if api_key_env:
        lines.append(f"    api_key_env: {api_key_env}")
    if api_mode and api_mode not in {"messages"}:
        lines.append(f"    api_mode: {api_mode}")
    for role in ["reviewer", "translator"]:
        lines.extend([
            f"  {role}:",
            f"    type: {provider_block}",
            f"    model: {model_block}",
        ])
        if base_url and base_url != "local":
            lines.append(f"    base_url: {base_url}")
        if api_key_env:
            lines.append(f"    api_key_env: {api_key_env}")
        if api_mode and api_mode not in {"messages"}:
            lines.append(f"    api_mode: {api_mode}")
    replacement = "\n".join(lines)
    providers_re = r"(?ms)^providers:\n.*?(?=^github:|^sources_file:|^analysis:|^agents:|^obsidian:|\Z)"
    if re.search(providers_re, base_config):
        return re.sub(providers_re, replacement + "\n", base_config)
    return replacement + "\n" + base_config


def write_run_files(payload: dict[str, Any], work_dir: Path) -> tuple[Path, int]:
    github_url = sanitize_github_url(str(payload.get("github_url") or payload.get("url") or ""))
    config_file = sanitize_config_file(str(payload.get("config_file") or payload.get("config") or "anatomy.config.example.yaml"))
    limit_skills = int(payload.get("limit_skills") if payload.get("limit_skills") is not None else 1)
    limit_skills = max(0, min(limit_skills, 5))
    ref = str(payload.get("ref") or "").strip()

    local_root = ROOT / "tmp" / "local-bridge"
    local_root.mkdir(parents=True, exist_ok=True)
    source_yaml = local_root / "sources.local.yaml"
    source_lines = ["sources:", f"  - name: {source_name_from_url(github_url)}", f"    url: {github_url}"]
    if ref:
        source_lines.append(f"    ref: {ref}")
    source_yaml.write_text("\n".join(source_lines) + "\n", encoding="utf-8")

    base_config = (ROOT / config_file).read_text(encoding="utf-8")
    base_config = override_provider_config(base_config, payload)
    base_config = re.sub(r"(?m)^sources_file:\s*.*$", "sources_file: tmp/local-bridge/sources.local.yaml", base_config)
    config_path = ROOT / "anatomy.local-run.yaml"
    config_path.write_text(base_config, encoding="utf-8")
    return config_path, limit_skills


def run_local_analysis(payload: dict[str, Any], job_id: str | None = None) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="asa-local-run-") as tmp:
        work_dir = Path(tmp)
        append_job_log(job_id, "config", "writing local source/config") if job_id else None
        config_path, limit_skills = write_run_files(payload, work_dir)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        api_key = str(payload.get("api_key") or "").strip()
        api_key_env = normalized_api_key_env(payload)
        raw_api_key_env = str(payload.get("api_key_env") or "").strip()
        if api_key:
            env[api_key_env] = api_key
        elif looks_like_api_key(raw_api_key_env):
            env[api_key_env] = raw_api_key_env
        run_cmd = [sys.executable, "-m", "asa", "run", "--config", str(config_path), "--limit-skills", str(limit_skills)]
        model_label = str(payload.get("model") or "configured model")
        append_job_log(job_id, "model", f"using {model_label}") if job_id else None
        append_job_log(job_id, "run", "starting asa run") if job_id else None
        update_job(job_id, progress=20) if job_id else None
        run_proc = subprocess.run(run_cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=900)
        if run_proc.returncode != 0:
            message = (run_proc.stderr or run_proc.stdout)[-4000:]
            append_job_log(job_id, "failed", summarize_process_error(message)) if job_id else None
            return {"ok": False, "stage": "run", "message": message, "stdout": run_proc.stdout[-2000:]}
        run_dir = ""
        for line in run_proc.stdout.splitlines():
            if line.startswith("Completed run:"):
                run_dir = line.split(":", 1)[1].strip()
        if not run_dir:
            return {"ok": False, "stage": "run", "message": "run completed but run directory was not reported", "stdout": run_proc.stdout[-2000:]}
        append_job_log(job_id, "run", f"completed run {Path(run_dir).name}") if job_id else None
        update_job(job_id, progress=72) if job_id else None
        run_path = Path(run_dir)
        if not run_path.is_absolute():
            run_path = ROOT / run_path
        export_cmd = [sys.executable, "-m", "asa", "export-all", "--run", str(run_path), "--output", "site"]
        append_job_log(job_id, "export", "refreshing site surfaces") if job_id else None
        update_job(job_id, progress=84) if job_id else None
        export_proc = subprocess.run(export_cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=300)
        if export_proc.returncode != 0:
            message = (export_proc.stderr or export_proc.stdout)[-4000:]
            append_job_log(job_id, "failed", summarize_process_error(message)) if job_id else None
            return {"ok": False, "stage": "export", "run_dir": str(run_path), "message": message, "stdout": export_proc.stdout[-2000:]}
        shutil.copyfile(ROOT / "site" / "cinema" / "cinema-data.json", ROOT / "site" / "demo-data.latest.json") if (ROOT / "site" / "cinema" / "cinema-data.json").exists() else None
        append_job_log(job_id, "export", "site report / data / graph refreshed") if job_id else None
        return {
            "ok": True,
            "message": "analysis complete",
            "run_dir": str(run_path),
            "run_id": run_path.name,
            "limit_skills": limit_skills,
            "surfaces": {
                "demo": "cinema/",
                "repo": "repo/",
                "report": "report/",
                "data": "data/",
                "graph": "graph/",
            },
            "stdout": (run_proc.stdout + "\n" + export_proc.stdout)[-4000:],
        }


def plan_local_analysis(payload: dict[str, Any]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="asa-local-plan-") as tmp:
        work_dir = Path(tmp)
        config_path, limit_skills = write_run_files(payload, work_dir)
        env = os.environ.copy()
        env["PYTHONPATH"] = str(ROOT / "src")
        output_path = work_dir / "plan.json"
        cmd = [sys.executable, "-m", "asa", "plan-run", "--config", str(config_path), "--limit-skills", str(limit_skills), "--output", str(output_path)]
        proc = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=240)
        if proc.returncode != 0:
            return {"ok": False, "stage": "plan", "message": (proc.stderr or proc.stdout)[-4000:]}
        plan = json.loads(output_path.read_text(encoding="utf-8"))
        return {"ok": True, "message": "plan complete", "plan": plan}


def summarize_process_error(message: str) -> str:
    lines = [line.strip() for line in message.splitlines() if line.strip()]
    for line in reversed(lines):
        if "Error" in line or "Exception" in line or "required" in line or "HTTP" in line or "urlopen" in line:
            return line[:240]
    return (lines[-1] if lines else "process failed")[:240]


def test_openai_compatible(payload: dict[str, Any]) -> dict[str, Any]:
    base_url = str(payload.get("base_url") or "").rstrip("/")
    model = str(payload.get("model") or "").strip()
    api_key = resolve_api_key(payload)
    if not base_url or not model:
        return {"ok": False, "message": "base_url and model are required"}
    if not api_key:
        return {"ok": False, "message": "api_key or api_key_env is required"}

    body = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Return only the word ok."},
            {"role": "user", "content": "ping"},
        ],
        "temperature": 0,
        "max_tokens": 8,
    }
    request = urllib.request.Request(
        base_url + "/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        served_model = data.get("model") or model
        return {"ok": True, "message": f"model test passed: {served_model}", "served_model": served_model}
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "message": f"provider HTTP {exc.code}: {error_body[:500]}"}
    except Exception as exc:  # noqa: BLE001 - surfaced as local bridge JSON
        return {"ok": False, "message": f"provider request failed: {exc}"}


def test_anthropic(payload: dict[str, Any]) -> dict[str, Any]:
    base_url = str(payload.get("base_url") or "https://api.anthropic.com/v1").rstrip("/")
    model = str(payload.get("model") or "").strip()
    api_key = resolve_api_key(payload)
    if not model:
        return {"ok": False, "message": "model is required"}
    if not api_key:
        return {"ok": False, "message": "api_key or api_key_env is required"}

    body = {
        "model": model,
        "max_tokens": 8,
        "temperature": 0,
        "messages": [{"role": "user", "content": [{"type": "text", "text": "Return only the word ok."}]}],
    }
    request = urllib.request.Request(
        base_url + "/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
        return {"ok": True, "message": f"model test passed: {data.get('model', model)}", "served_model": data.get("model", model)}
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "message": f"provider HTTP {exc.code}: {error_body[:500]}"}
    except Exception as exc:  # noqa: BLE001 - surfaced as local bridge JSON
        return {"ok": False, "message": f"provider request failed: {exc}"}


class BridgeHandler(BaseHTTPRequestHandler):
    server_version = "ASA-LocalBridge/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[asa-bridge] " + fmt % args + "\n")

    def do_OPTIONS(self) -> None:  # noqa: N802
        json_response(self, 200, {"ok": True})

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            json_response(self, 200, {"ok": True, "service": "asa-local-bridge"})
            return
        if self.path.startswith("/api/analyze/jobs/"):
            job_id = self.path.rsplit("/", 1)[-1]
            job = job_snapshot(job_id)
            json_response(self, 200 if job else 404, job or {"ok": False, "message": "job not found"})
            return
        json_response(self, 404, {"ok": False, "message": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        try:
            payload = read_request_json(self)
        except json.JSONDecodeError as exc:
            json_response(self, 400, {"ok": False, "message": f"invalid JSON: {exc}"})
            return
        try:
            if self.path == "/api/models/test":
                provider = str(payload.get("provider") or "openai").strip().lower()
                result = test_anthropic(payload) if provider == "anthropic" else test_openai_compatible(payload)
                json_response(self, 200 if result.get("ok") else 502, result)
                return
            if self.path == "/api/analyze/plan":
                result = plan_local_analysis(payload)
                json_response(self, 200 if result.get("ok") else 400, result)
                return
            if self.path == "/api/analyze/jobs":
                result = start_analysis_job(payload)
                json_response(self, 202, result)
                return
            if self.path == "/api/analyze/run":
                result = run_local_analysis(payload)
                json_response(self, 200 if result.get("ok") else 500, result)
                return
            if self.path == "/api/obsidian/open":
                result = open_obsidian_target(payload)
                json_response(self, 200 if result.get("ok") else 400, result)
                return
        except Exception as exc:  # noqa: BLE001 - returned to local UI only
            json_response(self, 500, {"ok": False, "message": str(exc)})
            return
        json_response(self, 404, {"ok": False, "message": "not found"})


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), BridgeHandler)
    print(f"ASA local bridge listening on http://{HOST}:{PORT}")
    print("Endpoints: GET /health, POST /api/models/test, POST /api/analyze/plan, POST /api/analyze/jobs, POST /api/analyze/run, POST /api/obsidian/open")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping ASA local bridge")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())









