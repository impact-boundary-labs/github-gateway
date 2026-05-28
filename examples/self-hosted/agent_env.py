from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable


def load_agent_env(script_path: str, required_keys: Iterable[str] = ()) -> str:
    missing = [key for key in required_keys if not os.environ.get(key, "").strip()]
    if not missing and not os.environ.get("AGENT_ENV_FILE", "").strip():
        return ""

    for candidate in agent_env_candidates(script_path):
        values = parse_simple_env_file(candidate)
        if not values:
            continue
        changed = False
        meaningful_change = False
        for key, value in values.items():
            if os.environ.get(key, "").strip():
                continue
            os.environ[key] = value
            changed = True
            if value.strip():
                meaningful_change = True
        if all(os.environ.get(key, "").strip() for key in required_keys):
            return str(candidate)
        if meaningful_change and not required_keys:
            return str(candidate)
    return ""


def detect_allowlisted_repo(script_path: str) -> tuple[str, bool, str]:
    for candidate in allowlist_env_candidates(script_path):
        values = parse_simple_env_file(candidate)
        raw = values.get("INTENT_GATEWAY_ALLOWED_REPOS", "").strip()
        if raw:
            repo, placeholder = normalize_single_allowlisted_repo(raw)
            return repo, placeholder, str(candidate)
    return "", False, ""


def agent_env_candidates(script_path: str) -> list[Path]:
    script_root = Path(script_path).resolve().parents[2]
    candidates: list[Path] = []
    explicit = os.environ.get("AGENT_ENV_FILE", "").strip()
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            Path.cwd() / "data" / "agents.env",
            script_root / "data" / "agents.env",
        ]
    )
    return unique_paths(candidates)


def allowlist_env_candidates(script_path: str) -> list[Path]:
    script_root = Path(script_path).resolve().parents[2]
    candidates: list[Path] = []
    explicit = os.environ.get("AGENT_ENV_FILE", "").strip()
    if explicit:
        candidates.append(Path(explicit))
    candidates.extend(
        [
            Path.cwd() / "data" / "agents.env",
            script_root / "data" / "agents.env",
            Path.cwd() / ".env.self-hosted",
            script_root / ".env.self-hosted",
            Path.cwd() / ".env",
            script_root / ".env",
            Path.cwd() / ".env.self-hosted.example",
            script_root / ".env.self-hosted.example",
            Path.cwd() / ".env.example",
            script_root / ".env.example",
        ]
    )
    return unique_paths(candidates)


def unique_paths(paths: Iterable[Path]) -> list[Path]:
    seen: set[str] = set()
    ordered: list[Path] = []
    for path in paths:
        key = str(path.resolve()) if path.is_absolute() else str(path)
        if key in seen:
            continue
        seen.add(key)
        ordered.append(path)
    return ordered


def parse_simple_env_file(path: Path) -> dict[str, str]:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError:
        return {}

    values: dict[str, str] = {}
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        if not key or " " in key or "\t" in key:
            continue
        values[key] = value.strip()
    return values


def normalize_single_allowlisted_repo(raw: str) -> tuple[str, bool]:
    entries = [entry.strip() for entry in raw.split(",") if entry.strip()]
    if len(entries) != 1:
        return "", False
    candidate = entries[0].strip().lower()
    if candidate == "owner/repo":
        return "", True
    if any(char in candidate for char in "*?[]"):
        return "", False
    owner, sep, repo = candidate.partition("/")
    if not sep or not owner.strip() or not repo.strip():
        return "", False
    return f"{owner.strip()}/{repo.strip()}", False
