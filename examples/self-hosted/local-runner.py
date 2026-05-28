#!/usr/bin/env python3
"""Small local runner for submitting a prepared intent to GitHub Gateway.

This runner is intentionally thin: it reads one JSON intent file, sends it to
the existing submit endpoint, and prints only safe decision fields. It does not
retry, mutate intents, read GitHub, or perform repository writes directly.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request
from typing import Any

EXIT_OK = 0
EXIT_LOCAL_ERROR = 1
EXIT_GATEWAY_ERROR = 2
EXIT_DECISION_NO_IMPACT = 3

DEFAULT_GATEWAY_URL = "http://127.0.0.1:18080"
REDACTED = "<redacted>"

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from agent_env import load_agent_env  # noqa: E402

LOADED_AGENT_ENV = load_agent_env(__file__, required_keys=("INTENT_GATEWAY_API_KEY",))


class RunnerError(RuntimeError):
    def __init__(self, message: str, exit_code: int = EXIT_LOCAL_ERROR):
        super().__init__(message)
        self.exit_code = exit_code


def normalize_submit_url(raw: str) -> str:
    value = (raw or "").strip() or DEFAULT_GATEWAY_URL
    if value.endswith("/api/v1/submit"):
        return value
    return value.rstrip("/") + "/api/v1/submit"


def redact(text: object, api_key: str = "") -> str:
    value = str(text)
    for secret in {api_key, os.environ.get("INTENT_GATEWAY_API_KEY", "").strip()}:
        if secret:
            value = value.replace(secret, REDACTED)
    value = re.sub(r"igw_live_[A-Za-z0-9_-]+_[A-Za-z0-9_-]+", "igw_live_<redacted>", value)
    value = re.sub(r"Bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer <redacted>", value)
    value = re.sub(r"github_pat_[A-Za-z0-9_]+", "github_pat_<redacted>", value)
    value = re.sub(r"gh[pousr]_[A-Za-z0-9_]+", "gh_<redacted>", value)
    return value


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit a prepared intent JSON file to a local Self-hosted GitHub Gateway v1.3.",
    )
    parser.add_argument("intent_file", help="Path to the intent JSON file to submit.")
    parser.add_argument(
        "--gateway-url",
        default=os.environ.get("INTENT_GATEWAY_URL", os.environ.get("GATEWAY_URL", DEFAULT_GATEWAY_URL)),
        help="Gateway root URL or /api/v1/submit URL. Defaults to INTENT_GATEWAY_URL, legacy GATEWAY_URL fallback, or http://127.0.0.1:18080.",
    )
    parser.add_argument(
        "--idempotency-key",
        default=os.environ.get("INTENT_GATEWAY_IDEMPOTENCY_KEY", "").strip(),
        help="Optional X-Idempotency-Key value. Defaults to INTENT_GATEWAY_IDEMPOTENCY_KEY when set.",
    )
    return parser.parse_args(argv)


def load_api_key() -> str:
    api_key = os.environ.get("INTENT_GATEWAY_API_KEY", "").strip()
    if not api_key:
        raise RunnerError("INTENT_GATEWAY_API_KEY is required")
    return api_key


def load_intent_file(path: str) -> bytes:
    try:
        with open(path, "rb") as handle:
            body = handle.read()
    except OSError as exc:
        raise RunnerError(f"could not read intent file: {redact(exc)}") from exc

    try:
        decoded = json.loads(body.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise RunnerError("intent file must be UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise RunnerError(f"invalid JSON intent file at line {exc.lineno}, column {exc.colno}") from exc

    if not isinstance(decoded, dict):
        raise RunnerError("intent file must contain a JSON object")
    return json.dumps(decoded, separators=(",", ":")).encode("utf-8")


def submit_intent(submit_url: str, api_key: str, body: bytes, idempotency_key: str) -> tuple[int, dict[str, Any]]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        "User-Agent": "intent-gateway-local-runner",
    }
    if idempotency_key:
        headers["X-Idempotency-Key"] = idempotency_key

    request = urllib.request.Request(submit_url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            response_body = response.read()
            return response.status, parse_gateway_response(response_body)
    except urllib.error.HTTPError as exc:
        response_body = exc.read()
        return exc.code, parse_gateway_response(response_body)
    except urllib.error.URLError as exc:
        raise RunnerError(f"gateway network error: {redact(exc.reason, api_key)}", EXIT_GATEWAY_ERROR) from exc
    except OSError as exc:
        raise RunnerError(f"gateway request failed: {redact(exc, api_key)}", EXIT_GATEWAY_ERROR) from exc


def parse_gateway_response(response_body: bytes) -> dict[str, Any]:
    if not response_body:
        return {}
    try:
        decoded = json.loads(response_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return {}
    return decoded if isinstance(decoded, dict) else {}


def safe_field(data: dict[str, Any], field: str, api_key: str = "") -> str:
    value = data.get(field)
    if value in (None, ""):
        return ""
    return redact(value, api_key)


def repository_impact(data: dict[str, Any]) -> str:
    decision = safe_field(data, "decision").lower()
    request_status = safe_field(data, "request_status").lower()
    reused = data.get("reused_existing_pr") is True or safe_field(data, "replay_status").lower() == "reused"

    if decision == "admitted" and request_status == "followup_completed":
        return "same_pr_updated"
    if decision == "admitted":
        return "reviewable_pr"
    if decision == "reused" or reused:
        return "existing_pr"
    return "none"


def exit_code_for_decision(data: dict[str, Any], http_status: int) -> int:
    decision = safe_field(data, "decision").lower()
    if decision in {"admitted", "reused"}:
        return EXIT_OK
    if decision in {"blocked", "conflict"}:
        return EXIT_DECISION_NO_IMPACT
    if http_status >= 500 or decision == "error":
        return EXIT_GATEWAY_ERROR
    return EXIT_DECISION_NO_IMPACT


def print_safe_decision(http_status: int, data: dict[str, Any], api_key: str) -> None:
    print("Intent submitted to GitHub Gateway.")
    print()
    print(f"HTTP status: {http_status}")
    print(f"Decision: {safe_field(data, 'decision', api_key).lower() or 'unknown'}")
    print(f"Repository impact: {repository_impact(data)}")

    next_action = safe_field(data, "required_next_action", api_key) or "none"
    print(f"Required next action: {next_action}")

    for label, field in (
        ("Request status", "request_status"),
        ("Reject stage", "reject_stage"),
        ("Reason", "reason"),
    ):
        value = safe_field(data, field, api_key)
        if value:
            print(f"{label}: {value}")

    pr_number = data.get("pull_request_number")
    if isinstance(pr_number, int) and pr_number > 0:
        print(f"Pull request: #{pr_number}")

    pr_url = safe_field(data, "pr_url", api_key)
    if pr_url:
        print(f"Pull request URL: {pr_url}")

    created_branch = safe_field(data, "created_branch", api_key)
    if created_branch:
        print(f"Branch: {created_branch}")


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        api_key = load_api_key()
        submit_url = normalize_submit_url(args.gateway_url)
        body = load_intent_file(args.intent_file)
        http_status, data = submit_intent(submit_url, api_key, body, args.idempotency_key)
        print_safe_decision(http_status, data, api_key)
        return exit_code_for_decision(data, http_status)
    except RunnerError as exc:
        print(f"error: {redact(exc)}", file=sys.stderr)
        return exc.exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
