# Local Runner And Helpers

GitHub Gateway includes local helpers for preview evaluation. They are
convenience tools, not trust boundaries.

## Helper Overview

Public helper paths:

```text
scripts/create-runner-key.sh
scripts/create-runner-key.ps1
scripts/runner-key-gui.py
examples/self-hosted/local-runner.py
examples/self-hosted/github-gateway-story-demo.py
examples/self-hosted/write.json
gateway_cloud.py (legacy/helper compatibility script)
```

## `local-runner.py`

`local-runner.py` submits exactly one prepared intent JSON file to
`/api/v1/submit`.

It should print only safe decision fields. It should not print payloads, diffs,
secrets, authorization headers, or full raw JSON responses.

Required environment:

```bash
export INTENT_GATEWAY_URL="http://127.0.0.1:18080"
export INTENT_GATEWAY_API_KEY="<runner-key>"
```

Run:

```bash
python examples/self-hosted/local-runner.py examples/self-hosted/write.json
```

`INTENT_GATEWAY_URL` is primary. `GATEWAY_URL` is only a legacy fallback.

## `write.json`

`write.json` is a template. Replace placeholders before use:

```json
{
  "operation": "write",
  "target_repo": "OWNER/REPO",
  "target_branch": "TARGET_BRANCH",
  "snapshot_hash": "BRANCH_HEAD_SHA",
  "file_path": "config/example.yaml",
  "source_state": "absent",
  "payload": "bmFtZTogZXhhbXBsZQo="
}
```

Do not put private payloads or secrets in reusable example files.

## Runner Key Helpers

Runner Keys can be created from the dashboard in the self-hosted preview.

Advanced/local helper options may include:

- PowerShell helper
- Bash helper
- Mini GUI helper

These helpers exist to reduce setup friction. They do not make security
decisions. The Gateway still enforces repo scope, branch scope, policy,
read-state validation, and materialization rules.

## Staged Builders

If a staged builder exists in the repo, treat it as convenience tooling only.
It can help build structured intents, but it is not a security boundary.

Security boundary:

```text
GitHub Gateway admission + GitHub App materialization
```
