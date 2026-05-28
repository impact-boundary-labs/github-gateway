# Agent Instructions

This is the public agent contract for GitHub Gateway by Impact Boundary Labs.

Core rule:

```text
Read repository state. Submit repository impact through GitHub Gateway.
```

The agent may read GitHub with read-only access. The agent must not push,
create pull requests directly, or call GitHub write APIs. Repository impact
should happen only through admitted Gateway intents.

## Required Environment

The agent or runner needs:

```dotenv
INTENT_GATEWAY_URL=http://127.0.0.1:18080
INTENT_GATEWAY_API_KEY=<runner-key>
GITHUB_READ_TOKEN=<github-read-token>
TEST_REPO=OWNER/REPO
TEST_BRANCH=TARGET_BRANCH
```

`INTENT_GATEWAY_API_KEY` is the Runner Key.

`GITHUB_READ_TOKEN` is the primary read credential name. `GITHUB_TOKEN` may be
supported by some helper code as a legacy fallback, but public setup should use
`GITHUB_READ_TOKEN`.

`INTENT_GATEWAY_URL` is primary. `GATEWAY_URL` may exist as a legacy fallback in
some local helpers, but public setup should use `INTENT_GATEWAY_URL`.

## Prohibited Agent Actions

The agent must not run:

- `git push`
- `gh pr create`
- GitHub REST or GraphQL write mutations
- GitHub POST, PUT, PATCH, or DELETE repository-impact APIs

The agent must not directly create, update, or delete:

- branches
- commits
- tags
- releases
- pull requests
- GitHub Actions workflows
- repository settings
- repository secrets
- branch protection rules
- collaborators or team access

## Ambient Write Credential Check

Run this from the agent or demo environment in a local clone of the test
repository:

```powershell
git -c credential.helper= push --dry-run origin HEAD:refs/heads/ggw-readonly-push-test
```

Expected:

```text
The push must fail.
```

If it succeeds, the environment still has ambient GitHub write credentials.
Common sources are Git Credential Manager, `gh auth`, SSH keys, classic PATs, or
other stored credentials. That write access does not come from the Runner Key.

## Submission Endpoint

Submit structured intents to:

```text
<INTENT_GATEWAY_URL>/api/v1/submit
```

Use a Bearer authorization header whose value is the Runner Key. Do not log the
header value.

## Intent Type: write

Use `operation: "write"` for one full-file write.

New file example:

```json
{
  "operation": "write",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "file_path": "config/example.yaml",
  "source_state": "absent",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "payload": "bmFtZTogZXhhbXBsZQo=",
  "agent_message": "Context:\nAdd a small demo config file.\n\nProposed changes:\n- Create config/example.yaml.\n\nValidation:\n- Built from the current branch head.\n\nSafety note:\nNo known sensitive areas."
}
```

Existing file example:

```json
{
  "operation": "write",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "file_path": "config/example.yaml",
  "source_state": "present",
  "read_blob_sha": "READ_BLOB_SHA",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "payload": "bmFtZTogZXhhbXBsZS11cGRhdGVkCg==",
  "agent_message": "Context:\nUpdate an existing demo config.\n\nProposed changes:\n- Replace config/example.yaml with updated full-file content.\n\nValidation:\n- The read blob SHA was read from GitHub before submit.\n\nSafety note:\nNo known sensitive areas."
}
```

## Intent Type: write_set

Use `operation: "write_set"` for grouped multi-file changes that should be
reviewed as one Gateway PR.

```json
{
  "operation": "write_set",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "changes": [
    {
      "file_path": "config/service.yaml",
      "source_state": "absent",
      "payload": "c2VydmljZTogZXhhbXBsZQo="
    },
    {
      "file_path": "config/settings.yaml",
      "source_state": "present",
      "read_blob_sha": "READ_BLOB_SHA",
      "payload": "c2V0dGluZzogdXBkYXRlZAo="
    }
  ],
  "agent_message": "Context:\nUpdate related demo config files together.\n\nProposed changes:\n- Add config/service.yaml.\n- Update config/settings.yaml.\n\nValidation:\n- State was read before submit.\n\nSafety note:\nNo known sensitive areas."
}
```

Do not include per-item `operation` fields inside `changes[]`.

## Intent Type: update_gateway_pr_write_set

Use `operation: "update_gateway_pr_write_set"` only for a controlled follow-up
on an existing Gateway-created `write_set` PR that is still known to this local
Gateway state. Do not use it for single-file `write` PRs.

The agent must re-read the parent PR and use the current PR head as
`expected_parent_head_commit`.

```json
{
  "operation": "update_gateway_pr_write_set",
  "target_repo": "OWNER/REPO",
  "parent_pr_number": 123,
  "expected_parent_head_commit": "EXPECTED_PARENT_HEAD_SHA",
  "changes": [
    {
      "file_path": "config/service.yaml",
      "source_state": "present",
      "read_blob_sha": "READ_BLOB_SHA",
      "payload": "c2VydmljZTogZm9sbG93LXVwCg=="
    }
  ],
  "agent_message": "Context:\nFollow up on the Gateway-created PR after review.\n\nProposed changes:\n- Update config/service.yaml in the same PR.\n\nValidation:\n- Parent PR head was re-read before submit.\n\nSafety note:\nNo known sensitive areas."
}
```

Do not use follow-up intents for arbitrary human-created PRs.

## State Binding Rules

For existing files:

- set `source_state` to `present`
- include `read_blob_sha`
- use the Git blob SHA from GitHub, not a local file hash

For new files:

- set `source_state` to `absent`
- omit `read_blob_sha`

For fresh write and write-set intents:

- set `snapshot_hash` to the branch head read before submit

For follow-up intents:

- set `expected_parent_head_commit` to the current parent PR head

Do not invent SHAs. Do not reuse stale branch heads or stale PR heads.

## Handling required_next_action

The Gateway response is the source of truth.

Common responses:

| Decision/status | What the agent should do |
| --- | --- |
| Admitted | Report the PR link for review. Do not merge. |
| Reused | Report the existing PR link. Do not duplicate the change. |
| Blocked / policy_scope | Stop. Change path or ask for policy change. |
| Blocked / content_sanity | Stop. Fix payload. Do not retry blindly. |
| Conflict / read_state_validation | Re-read current file state once and resubmit if appropriate. |
| Conflict / parent_head_revalidation | Re-read parent PR head and build a new follow-up intent. |
| Error / verification_required | Stop and surface to operator. |

If `required_next_action` is present, follow it. Do not retry blocked or
conflicted requests without the required fresh read or human/operator action.

## Agent Message

Use `agent_message` to give reviewers concise context.

Recommended structure:

```text
Context:
Why this change is needed.

Proposed changes:
- High-level bullets only.

Validation:
What state was read and what local checks were done.

Safety note:
No known sensitive areas.
```

`agent_message` is PR-public when an intent is admitted. Do not include secrets,
tokens, private keys, `.env` values, raw payloads, full diffs, private paths, or
hidden tracking links.

## Agent Checklist

Before submitting:

- target repo matches `TEST_REPO`
- target branch matches `TEST_BRANCH`
- path is allowed by policy
- state was read from GitHub or a trusted local checkout
- existing files include `read_blob_sha`
- new files omit `read_blob_sha`
- payload is full-file base64
- `agent_message` is short and public-safe
- no direct GitHub write is attempted
