#!/usr/bin/env python3
"""Small Cloud/HTTP helper for Intent Gateway live tests.

This file is intentionally independent of the old CLI/Docker harness.
It sends exactly the JSON a test gives it. It does not inject request_id,
idempotency_key, headers, or legacy CLI compatibility fields.
"""

from __future__ import annotations

import base64
import fnmatch
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


def normalize_gateway_submit_url(raw: str) -> str:
    value = (raw or "").strip() or "http://127.0.0.1:18080"
    if value.endswith("/api/v1/submit"):
        return value
    return value.rstrip("/") + "/api/v1/submit"


GATEWAY_URL = normalize_gateway_submit_url(
    os.environ.get("INTENT_GATEWAY_URL", os.environ.get("GATEWAY_URL", "http://127.0.0.1:18080"))
)
GITHUB_API_URL = os.environ.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
GITHUB_TOKEN = os.environ.get("GITHUB_READ_TOKEN", os.environ.get("GITHUB_TOKEN", "")).strip()
GATEWAY_API_KEY = os.environ.get("INTENT_GATEWAY_API_KEY", os.environ.get("CLOUD_API_KEY", "")).strip()
POLICY_PATH = os.environ.get("INTENT_GATEWAY_POLICY_PATH", ".github/intent-gateway.yaml").strip()
MAX_COMMIT_WALK = int(os.environ.get("CLOUD_MAX_COMMIT_WALK", "30"))


@dataclass
class GatewayResult:
    status_code: int | None
    stdout: str
    stderr: str
    elapsed_seconds: float = 0.0

    @property
    def response_body(self) -> str:
        return self.stdout

    @property
    def exit_code(self) -> int:
        return 0 if self.status_code == 200 else 1

    @property
    def returncode(self) -> int:
        return self.exit_code

    @property
    def status(self) -> int | None:
        return self.status_code

    def parse_json(self) -> dict[str, Any]:
        if not self.stdout:
            return {}
        try:
            return json.loads(self.stdout)
        except json.JSONDecodeError:
            return {}

    def __iter__(self):
        yield self.exit_code
        yield self.stdout
        yield self.stderr


def encode_payload_text(text: str) -> str:
    return encode_payload_bytes(text.encode("utf-8"))


def encode_payload_bytes(data: bytes) -> str:
    return base64.b64encode(data).decode("ascii")


def _post_bytes(url: str, body: bytes, timeout: int, headers: dict[str, str]) -> GatewayResult:
    started = time.monotonic()
    request = urllib.request.Request(url, data=body, method="POST", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            return GatewayResult(response.status, response_body, "", time.monotonic() - started)
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        return GatewayResult(exc.code, response_body, "", time.monotonic() - started)
    except Exception as exc:
        return GatewayResult(None, "", f"cloud connection error: {exc}", time.monotonic() - started)


def submit_json(intent: dict[str, Any], timeout: int = 60, headers: dict[str, str] | None = None) -> GatewayResult:
    request_headers = {"Content-Type": "application/json"}
    if GATEWAY_API_KEY:
        request_headers["Authorization"] = f"Bearer {GATEWAY_API_KEY}"
    if headers:
        request_headers.update(headers)
    body = json.dumps(intent, separators=(",", ":")).encode("utf-8")
    return _post_bytes(GATEWAY_URL, body, timeout, request_headers)


def submit_raw(raw_bytes: bytes, timeout: int = 60, content_type: str = "application/json") -> GatewayResult:
    request_headers = {"Content-Type": content_type}
    if GATEWAY_API_KEY:
        request_headers["Authorization"] = f"Bearer {GATEWAY_API_KEY}"
    return _post_bytes(GATEWAY_URL, raw_bytes, timeout, request_headers)


def gateway_health_url() -> str:
    parsed = urllib.parse.urlparse(GATEWAY_URL)
    scheme = parsed.scheme or "http"
    netloc = parsed.netloc or "localhost:8080"
    return urllib.parse.urlunparse((scheme, netloc, "/healthz", "", "", ""))


def wait_for_gateway_http(timeout: int = 30) -> bool:
    health_url = gateway_health_url()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(health_url, timeout=2) as response:
                if response.status == 200:
                    body = response.read().decode("utf-8", errors="replace").strip().lower()
                    if body == "ok":
                        return True
        except (OSError, urllib.error.URLError, urllib.error.HTTPError):
            time.sleep(0.5)
    return False


def print_write_set_flag_notice(suite_name: str, expected_server_value: str) -> None:
    runner_value = os.environ.get("ENABLE_WRITE_SET_MATERIALIZATION", "<unset>").strip() or "<unset>"
    print(
        f"{suite_name}: expected gateway server ENABLE_WRITE_SET_MATERIALIZATION={expected_server_value}; "
        f"runner_env_ENABLE_WRITE_SET_MATERIALIZATION={runner_value}. "
        "Runner env is informational only; restart the gateway with the expected server environment.",
        flush=True,
    )


def require_github_environment(target_repo: str) -> tuple[str, str]:
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is required for live test setup and cleanup")
    parts = target_repo.split("/", 1)
    if len(parts) != 2 or not parts[0].strip() or not parts[1].strip():
        raise RuntimeError("target repo must use owner/repo format")
    return parts[0].strip(), parts[1].strip()


class GitHubAPIError(Exception):
    def __init__(self, status: int, body: str, path: str):
        self.status = status
        self.body = body
        self.path = path
        super().__init__(f"GitHub API error status={status} path={path} body={body}")


def github_api_request(method: str, path: str, data: dict[str, Any] | None = None, timeout: int = 20):
    if not GITHUB_TOKEN:
        raise RuntimeError("GITHUB_TOKEN is required")
    url = path if path.startswith(("http://", "https://")) else GITHUB_API_URL + path
    body = json.dumps(data).encode("utf-8") if data is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "intent-gateway-cloud-test",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            response_body = response.read().decode("utf-8", errors="replace")
            if not response_body:
                return None
            return json.loads(response_body)
    except urllib.error.HTTPError as exc:
        response_body = exc.read().decode("utf-8", errors="replace")
        raise GitHubAPIError(exc.code, response_body, path) from exc


def get_branch_head_sha(owner: str, repo: str, branch: str) -> str:
    encoded_branch = urllib.parse.quote(branch, safe="")
    data = github_api_request("GET", f"/repos/{owner}/{repo}/branches/{encoded_branch}")
    try:
        return data["commit"]["sha"]
    except (TypeError, KeyError) as exc:
        raise RuntimeError(f"branch response did not contain commit sha for {owner}/{repo}@{branch}") from exc


def get_commit_tree_sha(owner: str, repo: str, sha: str) -> str:
    encoded_sha = urllib.parse.quote(sha, safe="")
    data = github_api_request("GET", f"/repos/{owner}/{repo}/git/commits/{encoded_sha}")
    tree = data.get("tree", {}) if isinstance(data, dict) else {}
    tree_sha = str(tree.get("sha", "")).strip()
    if not tree_sha:
        raise RuntimeError(f"git commit {sha} did not contain a tree sha")
    return tree_sha


def get_tree_entries(owner: str, repo: str, tree_sha: str) -> list[dict[str, Any]]:
    encoded_tree_sha = urllib.parse.quote(tree_sha, safe="")
    data = github_api_request("GET", f"/repos/{owner}/{repo}/git/trees/{encoded_tree_sha}")
    if not isinstance(data, dict):
        raise RuntimeError(f"git tree {tree_sha} did not return a JSON object")
    if data.get("truncated") is True:
        raise RuntimeError(f"git tree {tree_sha} was truncated; refusing to guess source-state metadata")
    entries = data.get("tree", []) if isinstance(data, dict) else []
    if not isinstance(entries, list):
        raise RuntimeError(f"git tree {tree_sha} did not contain a tree listing")
    return [entry for entry in entries if isinstance(entry, dict)]


def read_path_state(owner: str, repo: str, ref: str, file_path: str) -> dict[str, Any]:
    parts = [part for part in file_path.split("/") if part]
    if not parts:
        raise RuntimeError("file_path must not be empty")

    tree_sha = get_commit_tree_sha(owner, repo, ref)
    for index, part in enumerate(parts):
        entry = next((item for item in get_tree_entries(owner, repo, tree_sha) if item.get("path") == part), None)
        if entry is None:
            return {"exists": False, "object_type": "", "blob_sha": "", "source_state": "absent"}

        entry_type = str(entry.get("type", "")).strip()
        entry_sha = str(entry.get("sha", "")).strip()
        is_last = index == len(parts) - 1
        if is_last:
            return {
                "exists": True,
                "object_type": entry_type,
                "blob_sha": entry_sha,
                "source_state": "present",
            }
        if entry_type != "tree" or not entry_sha:
            return {"exists": False, "object_type": "", "blob_sha": "", "source_state": "absent"}
        tree_sha = entry_sha

    return {"exists": False, "object_type": "", "blob_sha": "", "source_state": "absent"}


def bind_write_source_state(intent: dict[str, Any]) -> dict[str, Any]:
    if intent.get("operation") != "write":
        return intent

    target_repo = str(intent.get("target_repo", "")).strip()
    snapshot_hash = str(intent.get("snapshot_hash", "")).strip()
    file_path = str(intent.get("file_path", "")).strip()
    owner, repo = require_github_environment(target_repo)
    state = read_path_state(owner, repo, snapshot_hash, file_path)

    if state["exists"]:
        if state["object_type"] != "blob" or not state["blob_sha"]:
            raise RuntimeError(f"{file_path} exists at {snapshot_hash} as {state['object_type']!r}, not a blob")
        intent["source_state"] = "present"
        intent["read_blob_sha"] = state["blob_sha"]
    else:
        intent["source_state"] = "absent"
        intent.pop("read_blob_sha", None)
    return intent


def bind_write_set_source_state(intent: dict[str, Any]) -> dict[str, Any]:
    if intent.get("operation") != "write_set":
        return intent

    target_repo = str(intent.get("target_repo", "")).strip()
    snapshot_hash = str(intent.get("snapshot_hash", "")).strip()
    changes = intent.get("changes")
    if not isinstance(changes, list):
        raise RuntimeError("write_set changes must be a list before source-state binding")

    owner, repo = require_github_environment(target_repo)
    bound_changes: list[dict[str, Any]] = []
    for index, raw_change in enumerate(changes):
        if not isinstance(raw_change, dict):
            raise RuntimeError(f"write_set change {index} is not a JSON object")
        change = dict(raw_change)
        file_path = str(change.get("file_path", "")).strip()
        if not file_path:
            raise RuntimeError(f"write_set change {index} is missing file_path before source-state binding")

        state = read_path_state(owner, repo, snapshot_hash, file_path)
        if state["exists"]:
            if state["object_type"] != "blob" or not state["blob_sha"]:
                raise RuntimeError(f"{file_path} exists at {snapshot_hash} as {state['object_type']!r}, not a blob")
            change["source_state"] = "present"
            change["read_blob_sha"] = state["blob_sha"]
        else:
            change["source_state"] = "absent"
            change.pop("read_blob_sha", None)
        bound_changes.append(change)

    intent["changes"] = bound_changes
    return intent


def get_commit_parent_sha(owner: str, repo: str, sha: str) -> str:
    encoded_sha = urllib.parse.quote(sha, safe="")
    data = github_api_request("GET", f"/repos/{owner}/{repo}/commits/{encoded_sha}")
    parents = data.get("parents", []) if isinstance(data, dict) else []
    if not parents:
        raise RuntimeError(f"commit {sha} has no parent")
    parent = parents[0].get("sha")
    if not parent:
        raise RuntimeError(f"commit {sha} first parent has no sha")
    return parent


def get_policy_content_at_ref(owner: str, repo: str, ref: str) -> str | None:
    encoded_ref = urllib.parse.quote(ref, safe="")
    encoded_path = urllib.parse.quote(POLICY_PATH, safe="/")
    try:
        data = github_api_request("GET", f"/repos/{owner}/{repo}/contents/{encoded_path}?ref={encoded_ref}")
    except GitHubAPIError as exc:
        if exc.status == 404:
            return None
        raise
    if not isinstance(data, dict) or data.get("type") != "file":
        raise RuntimeError(f"{POLICY_PATH} at {ref} is not a file")
    if data.get("encoding") != "base64" or "content" not in data:
        raise RuntimeError(f"{POLICY_PATH} at {ref} is not base64 content")
    encoded_content = "".join(str(data["content"]).split())
    return base64.b64decode(encoded_content).decode("utf-8")


def normalize_policy_mode(value: str) -> str:
    cleaned = value.strip().strip("'\"").lower()
    return cleaned or "guarded"


def parse_repo_policy(policy_text: str) -> dict[str, Any]:
    policy = {"mode": "guarded", "allowed_paths": [], "blocked_paths": []}
    current_key = None
    for raw_line in policy_text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("mode:"):
            policy["mode"] = normalize_policy_mode(stripped.split(":", 1)[1])
            continue
        if stripped in {"allowed_paths:", "blocked_paths:"}:
            current_key = stripped[:-1]
            continue
        if stripped.startswith("- ") and current_key in policy:
            value = stripped[2:].strip().strip("'\"")
            if value:
                policy[current_key].append(value)
    return policy


def path_match(pattern: str, value: str) -> bool:
    pattern_parts = pattern.split("/")
    value_parts = value.split("/")
    if len(pattern_parts) != len(value_parts):
        return False
    return all(fnmatch.fnmatchcase(v, p) for p, v in zip(pattern_parts, value_parts))


def repo_policy_allows_path(policy: dict[str, Any], file_path: str) -> bool:
    for pattern in policy.get("blocked_paths", []):
        if path_match(pattern, file_path):
            return False
    return any(path_match(pattern, file_path) for pattern in policy.get("allowed_paths", []))


def find_drift_ancestor_with_allowed_policy(owner: str, repo: str, head_sha: str, file_path: str) -> str:
    current = head_sha
    for _ in range(MAX_COMMIT_WALK):
        parent = get_commit_parent_sha(owner, repo, current)
        policy_text = get_policy_content_at_ref(owner, repo, parent)
        if policy_text is not None:
            policy = parse_repo_policy(policy_text)
            if repo_policy_allows_path(policy, file_path):
                return parent
        current = parent
    raise RuntimeError(f"no drift ancestor with policy allowing {file_path!r} within {MAX_COMMIT_WALK} commits")


def get_pr_head_branch(owner: str, repo: str, number: int) -> str | None:
    pr = github_api_request("GET", f"/repos/{owner}/{repo}/pulls/{number}")
    head = pr.get("head", {}) if isinstance(pr, dict) else {}
    return head.get("ref")


def get_pr_body(owner: str, repo: str, number: int) -> str:
    pr = github_api_request("GET", f"/repos/{owner}/{repo}/pulls/{number}")
    if not isinstance(pr, dict):
        raise RuntimeError(f"pull request #{number} did not return a JSON object")
    body = pr.get("body")
    if body is None:
        return ""
    return str(body)


def close_pull_request(owner: str, repo: str, number: int) -> None:
    try:
        github_api_request("PATCH", f"/repos/{owner}/{repo}/pulls/{number}", data={"state": "closed"})
        print(f"Cleanup: closed PR #{number}", flush=True)
    except GitHubAPIError as exc:
        if exc.status == 404:
            print(f"Cleanup: PR #{number} already gone", flush=True)
            return
        print(f"Cleanup: failed to close PR #{number}: {exc}", flush=True)
    except Exception as exc:
        print(f"Cleanup: failed to close PR #{number}: {exc}", flush=True)


def delete_branch(owner: str, repo: str, branch: str) -> None:
    encoded_ref = urllib.parse.quote("heads/" + branch, safe="/")
    try:
        github_api_request("DELETE", f"/repos/{owner}/{repo}/git/refs/{encoded_ref}")
        print(f"Cleanup: deleted branch {branch}", flush=True)
    except GitHubAPIError as exc:
        if exc.status == 404 or (exc.status == 422 and "Reference does not exist" in exc.body):
            print(f"Cleanup: branch {branch} already gone", flush=True)
            return
        print(f"Cleanup: failed to delete branch {branch}: {exc}", flush=True)
    except Exception as exc:
        print(f"Cleanup: failed to delete branch {branch}: {exc}", flush=True)
