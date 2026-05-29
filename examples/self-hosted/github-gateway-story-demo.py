#!/usr/bin/env python3
"""Screen-recording-friendly live demo for the self-hosted GitHub Gateway 1.3 flow.

This is a story script, not an engineering matrix. It submits the same
Gateway intents as the live test helpers, but prints a short operator story
instead of raw responses or payload details.
"""

from __future__ import annotations

import os
import re
import secrets
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from agent_env import detect_allowlisted_repo, load_agent_env  # noqa: E402


LOADED_AGENT_ENV = load_agent_env(
    __file__,
    required_keys=("INTENT_GATEWAY_API_KEY", "GITHUB_READ_TOKEN", "TEST_REPO", "TEST_BRANCH"),
)


def _normalize_submit_url(raw: str) -> str:
    value = (raw or "").strip() or "http://127.0.0.1:18080"
    if value.endswith("/api/v1/submit"):
        return value
    return value.rstrip("/") + "/api/v1/submit"


os.environ["GATEWAY_URL"] = _normalize_submit_url(
    os.environ.get("INTENT_GATEWAY_URL", os.environ.get("GATEWAY_URL", "http://127.0.0.1:18080"))
)

# gateway_cloud is shared with older live-test helpers and still reads
# GITHUB_TOKEN at import time. Self-hosted GitHub Gateway v1.3 contract uses the
# narrower GITHUB_READ_TOKEN name for the agent credential.
GITHUB_READ_TOKEN = os.environ.get("GITHUB_READ_TOKEN", "").strip()
if GITHUB_READ_TOKEN and not os.environ.get("GITHUB_TOKEN", "").strip():
    os.environ["GITHUB_TOKEN"] = GITHUB_READ_TOKEN

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import gateway_cloud as gw  # noqa: E402


RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + "-story-" + secrets.token_hex(3)
TARGET_REPO = os.environ.get(
    "TEST_REPO",
    "",
).strip()
TARGET_BRANCH = os.environ.get(
    "TEST_BRANCH",
    "",
).strip()
DEMO_FILE_PATH = os.environ.get(
    "DEMO_FILE_PATH",
    f"config/live-demo-pass-{RUN_ID}.yaml",
).strip()
BLOCKED_FILE_PATH = os.environ.get(
    "DEMO_BLOCKED_FILE_PATH",
    f"security/live-demo-blocked-{RUN_ID}.yaml",
).strip()


class DemoFailure(RuntimeError):
    pass


STATE: dict[str, Any] = {
    "pr_number": None,
    "pr_url": "",
    "branch": "",
    "first_head": "",
    "followup_head": "",
    "stale_decision": "",
}


def sanitize(value: object) -> str:
    text = str(value)
    for secret_value in {
        gw.GATEWAY_API_KEY,
        gw.GITHUB_TOKEN,
        GITHUB_READ_TOKEN,
        os.environ.get("CLOUD_API_KEY", "").strip(),
    }:
        if secret_value:
            text = text.replace(secret_value, "<redacted>")
    text = re.sub(r"igw_live_[A-Za-z0-9_-]+_[A-Za-z0-9_-]+", "igw_live_<redacted>", text)
    text = re.sub(r"github_pat_[A-Za-z0-9_]+", "github_pat_<redacted>", text)
    text = re.sub(r"gh[pousr]_[A-Za-z0-9_]+", "gh_<redacted>", text)
    text = re.sub(r"Bearer\s+[A-Za-z0-9._~+/=-]+", "Bearer <redacted>", text)
    return text


def short_sha(value: object) -> str:
    text = str(value or "").strip()
    if len(text) > 12:
        return text[:12] + "..."
    return text


def section(number: int, title: str) -> None:
    line = "-" * 48
    print()
    print(line, flush=True)
    print(f"{number}. {title}", flush=True)
    print(line, flush=True)


def block(label: str, lines: list[str]) -> None:
    print(f"{label}:", flush=True)
    for line in lines:
        print(f"  {line}", flush=True)
    print(flush=True)


def response_field(data: dict[str, Any], field: str) -> str:
    value = data.get(field)
    if value in (None, ""):
        return ""
    return sanitize(value)


def gateway_summary(result: gw.GatewayResult, data: dict[str, Any]) -> list[str]:
    fields = [
        f"http={result.status_code}",
        f"decision={response_field(data, 'decision') or '<missing>'}",
    ]
    for field in ("request_status", "reject_stage", "required_next_action"):
        value = response_field(data, field)
        if value:
            fields.append(f"{field}={value}")
    return fields


def require(condition: bool, message: str, result: gw.GatewayResult | None = None, data: dict[str, Any] | None = None) -> None:
    if condition:
        return
    details: list[str] = [message]
    if result is not None and data is not None:
        details.extend(gateway_summary(result, data))
    if result is not None and result.stderr.strip():
        details.append(f"stderr={sanitize(result.stderr.strip())}")
    raise DemoFailure("; ".join(details))


def parse_response(result: gw.GatewayResult) -> dict[str, Any]:
    parsed = result.parse_json()
    return parsed if isinstance(parsed, dict) else {}


def submit(intent: dict[str, Any], idempotency_suffix: str) -> tuple[gw.GatewayResult, dict[str, Any]]:
    result = gw.submit_json(
        intent,
        timeout=120,
        headers={"X-Idempotency-Key": f"story-demo-{RUN_ID}-{idempotency_suffix}"},
    )
    return result, parse_response(result)


def require_environment() -> tuple[str, str]:
    missing: list[str] = []
    if not gw.GATEWAY_API_KEY:
        missing.append("INTENT_GATEWAY_API_KEY")
    if not gw.GITHUB_TOKEN:
        missing.append("GITHUB_READ_TOKEN")
    if not TARGET_REPO:
        raise DemoFailure("TEST_REPO is required. Set it in data/agents.env or your shell.")
    if TARGET_REPO.strip().lower() == "owner/repo":
        raise DemoFailure("TEST_REPO still looks like OWNER/REPO. Set it in data/agents.env or your shell.")
    if not TARGET_BRANCH:
        missing.append("TEST_BRANCH")
    if missing:
        raise DemoFailure("missing required environment: " + ", ".join(missing))
    return gw.require_github_environment(TARGET_REPO)


def validate_local_allowlist() -> None:
    allowlisted_repo, placeholder, allowlist_path = detect_allowlisted_repo(__file__)
    if placeholder:
        raise DemoFailure(
            f"INTENT_GATEWAY_ALLOWED_REPOS still looks like OWNER/REPO in {allowlist_path or '.env'}. "
            "Edit .env in the extracted self-hosted folder, set it to your test repository, restart the Gateway, "
            "and do not put this setting in data/agents.env."
        )
    if allowlisted_repo and allowlisted_repo != TARGET_REPO.lower():
        raise DemoFailure(
            f"TEST_REPO={TARGET_REPO} does not match INTENT_GATEWAY_ALLOWED_REPOS={allowlisted_repo}. "
            "Update data/agents.env for the demo values, and update .env if the Gateway allowlist is wrong."
        )


def preflight_policy(owner: str, repo: str, base_head: str) -> None:
    policy_text = gw.get_policy_content_at_ref(owner, repo, base_head)
    if policy_text is None:
        raise DemoFailure(
            f"{TARGET_BRANCH} has no {gw.POLICY_PATH}. Commit the bundled "
            "test-repo-template/.github/intent-gateway.yaml to the target repo first. "
            "You can check this with: python examples/self-hosted/check-test-repo.py"
        )
    policy = gw.parse_repo_policy(policy_text)
    good_allowed = gw.repo_policy_allows_path(policy, DEMO_FILE_PATH)
    blocked_allowed = gw.repo_policy_allows_path(policy, BLOCKED_FILE_PATH)
    if not good_allowed:
        raise DemoFailure(
            f"demo path {DEMO_FILE_PATH} is not allowed by the repo policy; "
            "for Self-hosted GitHub Gateway v1.3 config/* policy, use a direct file such as "
            "config/live-demo-pass-<timestamp>.yaml, not a nested path such as "
            "config/demo/file.yaml"
        )
    if blocked_allowed:
        raise DemoFailure(
            f"blocked demo path {BLOCKED_FILE_PATH} is allowed by the repo policy; "
            "set DEMO_BLOCKED_FILE_PATH to a denied test path"
        )
    print("Policy preflight: demo path allowed, blocked path denied.", flush=True)


def payload_text(scenario: str, version: int) -> str:
    return "\n".join(
        [
            "intent_gateway_story_demo: true",
            f"run_id: {RUN_ID}",
            f"scenario: {scenario}",
            f"version: {version}",
            "",
        ]
    )


def agent_message(scenario: str) -> str:
    return "\n".join(
        [
            "Context:",
            f"This change supports the GitHub Gateway 1.3 story demo scenario `{scenario}`.",
            "",
            "Proposed changes:",
            "- Update only the guarded demo configuration path.",
            "- Keep the repository impact reviewable in a Gateway-created PR.",
            "",
            "Validation:",
            "- Read the target branch or parent PR head before submitting.",
            "- Bound every changed file to its current Git source state.",
            "",
            "Safety note:",
            "No known API, auth, migration, or secret-handling changes.",
        ]
    )


def make_write_set_intent(base_head: str, file_path: str, scenario: str, version: int) -> dict[str, Any]:
    return gw.bind_write_set_source_state(
        {
            "target_repo": TARGET_REPO,
            "target_branch": TARGET_BRANCH,
            "snapshot_hash": base_head,
            "operation": "write_set",
            "agent_message": agent_message(scenario),
            "changes": [
                {
                    "file_path": file_path,
                    "payload": gw.encode_payload_text(payload_text(scenario, version)),
                }
            ],
        }
    )


def make_followup_intent(parent_pr_number: int, expected_head: str, read_blob_sha: str, version: int) -> dict[str, Any]:
    return {
        "target_repo": TARGET_REPO,
        "operation": "update_gateway_pr_write_set",
        "parent_pr_number": parent_pr_number,
        "expected_parent_head_commit": expected_head,
        "agent_message": agent_message("same-pr-follow-up"),
        "changes": [
            {
                "file_path": DEMO_FILE_PATH,
                "source_state": "present",
                "read_blob_sha": read_blob_sha,
                "payload": gw.encode_payload_text(payload_text("same-pr-follow-up", version)),
            }
        ],
    }


def pull_request_url(data: dict[str, Any]) -> str:
    pr_url = str(data.get("pr_url", "")).strip()
    if pr_url:
        return pr_url
    legacy_url = str(data.get("pull_request_url", "")).strip()
    if legacy_url:
        return legacy_url
    number = data.get("pull_request_number")
    if isinstance(number, int) and number > 0:
        return f"https://github.com/{TARGET_REPO}/pull/{number}"
    return ""


def is_same_effect_reuse(data: dict[str, Any], expected_pr_number: int, expected_pr_url: str) -> bool:
    reused = (
        data.get("reused_existing_pr") is True
        or data.get("reused_existing_result") is True
        or data.get("replay_status") == "reused"
        or data.get("decision") == "Reused"
    )
    same_number = data.get("pull_request_number") == expected_pr_number
    same_url = pull_request_url(data) == expected_pr_url
    return reused and same_number and same_url


def run_bad_intent(base_head: str) -> None:
    section(1, "Bad intent blocked before impact")
    block("Agent tries", [f"Change a file outside the expected repository scope: {BLOCKED_FILE_PATH}"])
    block("Gateway checks", ["Repository policy scope, path rules, and source-state binding."])

    intent = make_write_set_intent(base_head, BLOCKED_FILE_PATH, "blocked-before-impact", 1)
    result, data = submit(intent, "blocked")

    decision = response_field(data, "decision") or "<missing>"
    print("Decision:", flush=True)
    print(f"  {decision.upper()}", flush=True)
    print(flush=True)

    no_pr = not data.get("pull_request_number") and not pull_request_url(data) and not data.get("created_branch")
    require(data.get("decision") == "Blocked", "expected a Blocked decision for the bad intent", result, data)
    require(no_pr, "expected blocked intent to create no branch, commit, or PR", result, data)

    block("Repository impact", ["No branch.", "No commit.", "No pull request."])
    block("Why it matters", ["A bad agent attempt does not create GitHub noise or CI cost."])
    print("PASS", flush=True)


def run_good_intent(base_head: str) -> dict[str, Any]:
    section(2, "Good intent creates reviewable PR")
    block("Agent tries", [f"Propose a small allowed config change: {DEMO_FILE_PATH}"])
    block("Gateway checks", ["Repo grant, branch grant, policy scope, and file read-state."])

    intent = make_write_set_intent(base_head, DEMO_FILE_PATH, "reviewable-pr", 1)
    result, data = submit(intent, "good")

    require(result.status_code == 200, "expected accepted HTTP response for good intent", result, data)
    require(data.get("decision") == "Admitted", "expected good intent to be admitted", result, data)

    pr_number = data.get("pull_request_number")
    pr_url = pull_request_url(data)
    branch = str(data.get("created_branch", "")).strip()
    first_head = str(data.get("head_sha", "")).strip()
    require(isinstance(pr_number, int) and pr_number > 0, "expected PR number", result, data)
    require(bool(pr_url), "expected PR URL", result, data)
    require(bool(branch), "expected created branch", result, data)
    require(bool(first_head), "expected PR head commit", result, data)

    STATE.update({"pr_number": pr_number, "pr_url": pr_url, "branch": branch, "first_head": first_head})

    print("Decision:", flush=True)
    print("  ADMITTED", flush=True)
    print(flush=True)
    block(
        "Repository impact",
        [
            f"GitHub App created PR #{pr_number}.",
            f"PR URL: {pr_url}",
            f"Branch: {branch}",
            f"Head: {short_sha(first_head)}",
        ],
    )
    block(
        "Why it matters",
        [
            "The agent did not receive a GitHub write token.",
            "The GitHub App created a reviewable PR.",
            "Human review is still required before merge.",
        ],
    )
    print("PASS", flush=True)
    return intent


def run_same_effect_reuse(intent: dict[str, Any]) -> None:
    section(3, "Same effect reused")
    block("Agent tries", ["Submit the same desired change again with a new idempotency key."])
    block("Gateway checks", ["Existing verified Gateway PR for the same requested effect."])

    result, data = submit(intent, "same-effect")
    expected_pr = int(STATE["pr_number"])
    expected_url = str(STATE["pr_url"])

    require(result.status_code == 200, "expected accepted HTTP response for same effect reuse", result, data)
    require(is_same_effect_reuse(data, expected_pr, expected_url), "expected existing PR reuse for same effect", result, data)

    print("Decision:", flush=True)
    print("  REUSED", flush=True)
    print(flush=True)
    block(
        "Repository impact",
        [
            f"Existing PR returned: #{expected_pr}.",
            f"PR URL: {expected_url}",
            "No duplicate PR spam.",
        ],
    )
    block("Why it matters", ["Repeated agent attempts converge on the same review object."])
    print("PASS", flush=True)


def run_same_pr_followup(owner: str, repo: str) -> None:
    section(4, "Same-PR follow-up")
    block("Agent tries", ["Fix review or CI feedback on the existing Gateway PR."])
    block("Gateway checks", ["Parent PR ownership, parent head, and file read-state."])

    pr_number = int(STATE["pr_number"])
    first_head = str(STATE["first_head"])
    first_state = gw.read_path_state(owner, repo, first_head, DEMO_FILE_PATH)
    require(first_state.get("exists") is True, f"expected {DEMO_FILE_PATH} to exist at first PR head")
    read_blob_sha = str(first_state.get("blob_sha", "")).strip()
    require(bool(read_blob_sha), f"expected read_blob_sha for {DEMO_FILE_PATH} at first PR head")

    intent = make_followup_intent(pr_number, first_head, read_blob_sha, 2)
    result, data = submit(intent, "followup")

    followup_head = str(data.get("head_sha", "")).strip()
    require(result.status_code == 200, "expected accepted HTTP response for follow-up", result, data)
    require(data.get("decision") == "Admitted", "expected follow-up to be admitted", result, data)
    require(data.get("request_status") == "followup_completed", "expected follow-up completion status", result, data)
    require(data.get("pull_request_number") == pr_number, "expected same PR number", result, data)
    require(pull_request_url(data) == STATE["pr_url"], "expected same PR URL", result, data)
    require(str(data.get("created_branch", "")).strip() == STATE["branch"], "expected same PR branch", result, data)
    require(followup_head and followup_head != first_head, "expected new follow-up head", result, data)

    STATE["followup_head"] = followup_head

    print("Decision:", flush=True)
    print("  ADMITTED", flush=True)
    print(flush=True)
    block(
        "Repository impact",
        [
            f"Same PR updated: #{pr_number}.",
            f"First head: {short_sha(first_head)}",
            f"Follow-up head: {short_sha(followup_head)}",
            "No new PR was created.",
        ],
    )
    block("Why it matters", ["Review feedback can be handled without abandoning the guarded PR."])
    print("PASS", flush=True)


def run_stale_followup(owner: str, repo: str) -> None:
    section(5, "Stale follow-up blocked")
    block("Agent tries", ["Update the PR using the old parent PR head."])
    block("Gateway checks", ["Current parent PR head before creating any new commit."])

    pr_number = int(STATE["pr_number"])
    first_head = str(STATE["first_head"])
    followup_head = str(STATE["followup_head"])
    stale_state = gw.read_path_state(owner, repo, followup_head, DEMO_FILE_PATH)
    require(stale_state.get("exists") is True, f"expected {DEMO_FILE_PATH} to exist at current PR head")
    stale_blob_sha = str(stale_state.get("blob_sha", "")).strip()
    require(bool(stale_blob_sha), f"expected read_blob_sha for {DEMO_FILE_PATH} at current PR head")

    intent = make_followup_intent(pr_number, first_head, stale_blob_sha, 3)
    result, data = submit(intent, "stale")
    STATE["stale_decision"] = str(data.get("decision", "")).strip()

    require(result.status_code == 409, "expected stale follow-up conflict response", result, data)
    require(data.get("decision") == "Conflict", "expected stale follow-up Conflict decision", result, data)
    require(
        str(data.get("required_next_action", "")).strip() == "re_read_parent_pr",
        "expected required_next_action=re_read_parent_pr",
        result,
        data,
    )

    print("Decision:", flush=True)
    print("  CONFLICT", flush=True)
    print(flush=True)
    block(
        "Repository impact",
        [
            "No commit created.",
            f"Current PR head stays: {short_sha(followup_head)}",
            "Required next action: re_read_parent_pr.",
        ],
    )
    block("Why it matters", ["Stale agent state is stopped before repository write impact."])
    print("PASS", flush=True)


def print_final_summary() -> None:
    print()
    print("Demo complete", flush=True)
    print()
    print("What you saw:", flush=True)
    print("- Bad intent: no PR", flush=True)
    print("- Good intent: reviewable PR", flush=True)
    print("- Same effect: existing PR reused", flush=True)
    print("- Follow-up: same PR updated", flush=True)
    print("- Stale state: blocked before write", flush=True)
    print()
    print("The agent can move fast.", flush=True)
    print("The repository only changes through the guard.", flush=True)
    print()
    print("Technical values:", flush=True)
    print(f"- PR number: {STATE['pr_number']}", flush=True)
    print(f"- PR URL: {STATE['pr_url']}", flush=True)
    print(f"- Branch: {STATE['branch']}", flush=True)
    print(f"- First head: {short_sha(STATE['first_head'])}", flush=True)
    print(f"- Follow-up head: {short_sha(STATE['followup_head'])}", flush=True)
    print(f"- Stale decision: {STATE['stale_decision']}", flush=True)


def main() -> int:
    try:
        owner, repo = require_environment()
        validate_local_allowlist()

        print("GitHub Gateway 1.3 Story Demo", flush=True)
        print(f"Gateway submit URL: {gw.GATEWAY_URL}", flush=True)
        print(f"Target repo: {TARGET_REPO}", flush=True)
        print(f"Target branch/base scope: {TARGET_BRANCH}", flush=True)
        if LOADED_AGENT_ENV:
            print(f"Loaded local agent settings from: {LOADED_AGENT_ENV}", flush=True)
        print(f"Demo file: {DEMO_FILE_PATH}", flush=True)
        print(f"Blocked file: {BLOCKED_FILE_PATH}", flush=True)
        print("Use test repositories only. This demo may create a test PR.", flush=True)

        if not gw.wait_for_gateway_http(timeout=15):
            raise DemoFailure("gateway health check failed; expected /healthz to return ok")

        base_head = gw.get_branch_head_sha(owner, repo, TARGET_BRANCH)
        print(f"Base branch head: {short_sha(base_head)}", flush=True)
        preflight_policy(owner, repo, base_head)

        run_bad_intent(base_head)
        good_intent = run_good_intent(base_head)
        run_same_effect_reuse(good_intent)
        run_same_pr_followup(owner, repo)
        run_stale_followup(owner, repo)
        print_final_summary()
        return 0
    except DemoFailure as exc:
        print()
        print("Demo stopped", flush=True)
        print(sanitize(exc), flush=True)
        return 1
    except Exception as exc:  # pragma: no cover - live demo safety net
        print()
        print("Demo stopped", flush=True)
        print(sanitize(f"{type(exc).__name__}: {exc}"), flush=True)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
