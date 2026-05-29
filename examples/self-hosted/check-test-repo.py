#!/usr/bin/env python3
"""Preflight check for the self-hosted GitHub Gateway demo target repository."""

from __future__ import annotations

import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from agent_env import detect_allowlisted_repo, load_agent_env  # noqa: E402


LOADED_AGENT_ENV = load_agent_env(
    __file__,
    required_keys=("GITHUB_READ_TOKEN", "TEST_REPO", "TEST_BRANCH"),
)

GITHUB_READ_TOKEN = os.environ.get("GITHUB_READ_TOKEN", "").strip()
if GITHUB_READ_TOKEN and not os.environ.get("GITHUB_TOKEN", "").strip():
    os.environ["GITHUB_TOKEN"] = GITHUB_READ_TOKEN

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

import gateway_cloud as gw  # noqa: E402


DEMO_FILE_PATH = "config/live-demo-pass.yaml"
BLOCKED_FILE_PATH = "security/live-demo-blocked.yaml"


class CheckFailure(RuntimeError):
    pass


def local_template_policy_display_path() -> str:
    candidates = [
        (REPO_ROOT / "test-repo-template" / ".github" / "intent-gateway.yaml", "test-repo-template/.github/intent-gateway.yaml"),
        (
            REPO_ROOT / "preview" / "test-repo-template" / ".github" / "intent-gateway.yaml",
            "preview/test-repo-template/.github/intent-gateway.yaml",
        ),
    ]
    for candidate, display in candidates:
        if candidate.exists():
            return display
    return "test-repo-template/.github/intent-gateway.yaml"


def require_environment() -> tuple[str, str, str, str]:
    target_repo = os.environ.get("TEST_REPO", "").strip()
    target_branch = os.environ.get("TEST_BRANCH", "").strip()
    missing = []
    if not gw.GITHUB_TOKEN:
        missing.append("GITHUB_READ_TOKEN")
    if not target_repo:
        missing.append("TEST_REPO")
    if not target_branch:
        missing.append("TEST_BRANCH")
    if missing:
        raise CheckFailure("missing required environment: " + ", ".join(missing))
    if target_repo.lower() == "owner/repo":
        raise CheckFailure("TEST_REPO still looks like OWNER/REPO. Set it in data/agents.env or your shell.")
    owner, repo = gw.require_github_environment(target_repo)
    return owner, repo, target_repo, target_branch


def validate_local_allowlist(target_repo: str) -> None:
    allowlisted_repo, placeholder, allowlist_path = detect_allowlisted_repo(__file__)
    if placeholder:
        raise CheckFailure(
            f"INTENT_GATEWAY_ALLOWED_REPOS still looks like OWNER/REPO in {allowlist_path or '.env'}. "
            "Set it in the self-hosted .env file, restart the Gateway, then rerun this check."
        )
    if allowlisted_repo and allowlisted_repo != target_repo.lower():
        raise CheckFailure(
            f"TEST_REPO={target_repo} does not match INTENT_GATEWAY_ALLOWED_REPOS={allowlisted_repo}. "
            "Update data/agents.env or the Gateway .env so both point to the same test repo."
        )


def run_check() -> None:
    owner, repo, target_repo, target_branch = require_environment()
    validate_local_allowlist(target_repo)
    template_path = local_template_policy_display_path()

    print("Self-hosted GitHub Gateway demo target check")
    print(f"Target repo: {target_repo}")
    print(f"Target branch: {target_branch}")
    print(f"Template policy: {template_path}")
    print()

    base_head = gw.get_branch_head_sha(owner, repo, target_branch)
    policy_text = gw.get_policy_content_at_ref(owner, repo, base_head)
    if policy_text is None:
        raise CheckFailure(
            f"{target_repo}@{target_branch} has no {gw.POLICY_PATH}. "
            "Copy or push the bundled test-repo-template/ contents to the GitHub test repo first. "
            "The required local template file is test-repo-template/.github/intent-gateway.yaml."
        )

    policy = gw.parse_repo_policy(policy_text)
    if not gw.repo_policy_allows_path(policy, DEMO_FILE_PATH):
        raise CheckFailure(f"{gw.POLICY_PATH} does not allow {DEMO_FILE_PATH}. Use the bundled test policy.")
    if gw.repo_policy_allows_path(policy, BLOCKED_FILE_PATH):
        raise CheckFailure(f"{gw.POLICY_PATH} allows {BLOCKED_FILE_PATH}; the demo needs security/* blocked.")

    print("PASS")
    print(f"GitHub branch contains {gw.POLICY_PATH}.")
    print(f"Policy allows {DEMO_FILE_PATH} and blocks {BLOCKED_FILE_PATH}.")
    print("You can now run: python examples/self-hosted/github-gateway-story-demo.py")


def main() -> int:
    try:
        run_check()
        return 0
    except CheckFailure as exc:
        print()
        print("Check stopped")
        print(str(exc))
        return 1
    except gw.GitHubAPIError as exc:
        print()
        print("Check stopped")
        print(f"GitHub read failed: status={exc.status} path={exc.path}")
        print("Confirm GITHUB_READ_TOKEN can read the target repository and branch.")
        return 1
    except Exception as exc:
        print()
        print("Check stopped")
        print(str(exc))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
