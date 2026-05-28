# Intent JSON Reference

Agents submit structured JSON intents to GitHub Gateway. The Gateway validates
the intent before any GitHub write impact is attempted.

This reference covers the Self-hosted GitHub Gateway v1.3 intent shapes:

- `write`
- `write_set`
- `update_gateway_pr_write_set`

All writes are full-file writes in Self-hosted GitHub Gateway v1.3. There is no native patch parser
in Self-hosted GitHub Gateway v1.3.

## Common Top-Level Fields

| Field | Required | Description |
| --- | --- | --- |
| `operation` | yes | `write`, `write_set`, or `update_gateway_pr_write_set`. |
| `target_repo` | yes | Repository in `OWNER/REPO` form. |
| `target_branch` | for fresh writes | Branch/base scope for `write` and `write_set`. |
| `snapshot_hash` | for fresh writes | Branch head commit read before submit. |
| `agent_message` | optional | Short PR-public review context. |

For follow-up:

| Field | Required | Description |
| --- | --- | --- |
| `parent_pr_number` | yes | Existing Gateway-created PR number. |
| `expected_parent_head_commit` | yes | Current parent PR head commit read before submit. |

## Common Change Fields

| Field | Required | Description |
| --- | --- | --- |
| `file_path` | yes | Repository-relative path. |
| `source_state` | yes | `present` for existing files, `absent` for new files. |
| `read_blob_sha` | when `present` | Git blob SHA for the file at the read state. |
| `payload` | yes | Standard base64 full-file content. |

Do not use local SHA-256 file hashes as `read_blob_sha`. Use the Git blob SHA
from GitHub.

## Path Rules

Paths are repository-relative.

Invalid examples:

- absolute paths
- Windows drive paths
- paths with backslashes
- paths with `.` or `..` segments
- paths with control characters
- paths outside policy scope

Policy decides whether a syntactically valid path is allowed.

## write: New File

Use `source_state: "absent"` and omit `read_blob_sha`.

```json
{
  "operation": "write",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "file_path": "config/new-file.yaml",
  "source_state": "absent",
  "payload": "bmFtZTogbmV3LWZpbGUK",
  "agent_message": "Context:\nAdd a small demo config file.\n\nProposed changes:\n- Create config/new-file.yaml.\n\nValidation:\n- Branch head was read before submit.\n\nSafety note:\nNo known sensitive areas."
}
```

## write: Existing File

Use `source_state: "present"` and include `read_blob_sha`.

```json
{
  "operation": "write",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "file_path": "config/existing.yaml",
  "source_state": "present",
  "read_blob_sha": "READ_BLOB_SHA",
  "payload": "bmFtZTogdXBkYXRlZAo=",
  "agent_message": "Context:\nUpdate a demo config file.\n\nProposed changes:\n- Replace config/existing.yaml with updated full-file content.\n\nValidation:\n- Blob SHA was read from GitHub before submit.\n\nSafety note:\nNo known sensitive areas."
}
```

## write_set

Use `write_set` for grouped multi-file changes. Each item in `changes[]` is a
full-file write. Do not include per-item `operation` fields.

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
  "agent_message": "Context:\nUpdate related demo config files.\n\nProposed changes:\n- Add config/service.yaml.\n- Update config/settings.yaml.\n\nValidation:\n- Branch head and existing blob state were read before submit.\n\nSafety note:\nNo known sensitive areas."
}
```

## update_gateway_pr_write_set

Use follow-up intents only for controlled updates to an existing Gateway-created
PR.

Required follow-up state:

- `parent_pr_number`
- `expected_parent_head_commit`

The agent must re-read the parent PR head immediately before building the
follow-up.

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
  "agent_message": "Context:\nFollow up on the Gateway-created PR.\n\nProposed changes:\n- Update config/service.yaml.\n\nValidation:\n- Parent PR head was re-read before submit.\n\nSafety note:\nNo known sensitive areas."
}
```

## Valid Response Shape

Responses vary by outcome, but public-safe fields commonly include:

```json
{
  "decision": "Admitted",
  "request_status": "admitted",
  "required_next_action": "review_pull_request",
  "pull_request_url": "<pull-request-url>"
}
```

Example blocked response:

```json
{
  "decision": "Blocked",
  "request_status": "blocked",
  "reject_stage": "policy_scope",
  "required_next_action": "choose_allowed_path"
}
```

Example conflict response:

```json
{
  "decision": "Conflict",
  "request_status": "conflict",
  "reject_stage": "read_state_validation",
  "required_next_action": "re_read_target_file"
}
```

## Common Invalid Examples

Do not submit nested paths if policy only allows direct `config/*`:

```json
{
  "operation": "write",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "file_path": "config/nested/file.yaml",
  "source_state": "absent",
  "payload": "bmFtZTogaW52YWxpZAo="
}
```

Do not invent `read_blob_sha`:

```json
{
  "operation": "write",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "file_path": "config/existing.yaml",
  "source_state": "present",
  "read_blob_sha": "INVENTED_SHA",
  "payload": "bmFtZTogaW52YWxpZAo="
}
```

Do not put raw file text in `payload`:

```json
{
  "operation": "write",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "file_path": "config/example.yaml",
  "source_state": "absent",
  "payload": "name: not-base64"
}
```

## Agent Message Rules

`agent_message` is optional, bounded, sanitized, and PR-public when admitted.

Use it for review context. Do not include:

- secrets
- tokens
- private keys
- `.env` values
- full payload dumps
- raw request JSON
- large diffs
- private local paths

Recommended structure:

```text
Context:
Why this change is needed.

Proposed changes:
- High-level bullets.

Validation:
What state was read and what checks were run.

Safety note:
No known sensitive areas.
```
