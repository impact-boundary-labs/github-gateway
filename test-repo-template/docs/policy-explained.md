# Preview Policy Explained

The preview test repository uses this policy:

```yaml
mode: guarded
allowed_paths:
  - config/*
blocked_paths:
  - security/*
  - .github/*
```

GitHub Gateway loads the policy from:

```text
.github/intent-gateway.yaml
```

The human repository owner creates and commits this file during initial test
repository setup. The Gateway then uses it as the policy source for submitted
intents.

## What It Allows

`config/*` allows direct files under `config/`, for example:

```text
config/live-demo-pass.yaml
config/self-hosted-preview-demo.yaml
config/gateway-load-test-20260520T091206Z-001.yaml
```

This gives the demo a small, reviewable place where admitted writes can create a
pull request.

## What It Blocks

`security/*` blocks direct files under `security/`, for example:

```text
security/live-demo-blocked.yaml
```

`.github/*` blocks direct files under `.github/`, for example:

```text
.github/intent-gateway.yaml
```

This means agents cannot modify the policy file through the Gateway after the
human owner has created it. Nested `.github/...` paths, such as workflow files,
are still denied because they are outside the allowed `config/*` scope.

These areas are blocked so the preview does not casually mutate security
configuration, workflow configuration, or the policy file through the Gateway.

## Direct Path Semantics

In this preview policy, `config/*` allows direct files under `config/`. It does
not allow nested paths such as:

```text
config/demo/file.yaml
config/gateway-load-test/run-20260520T091206Z/pr-001.yaml
```

Use direct demo paths instead:

```text
config/live-demo-pass.yaml
config/gateway-load-test-20260520T091206Z-001.yaml
```

## How This Supports The Demo

Admitted write under `config/`:
The agent submits a direct `config/<file>.yaml` write. Gateway admits it and
creates a reviewable pull request.

Blocked write under `security/`:
The agent submits `security/live-demo-blocked.yaml`. Gateway returns
`Blocked / policy_scope` and creates no repository impact.

Content-sanity failure under `config/`:
The path is allowed, but unsafe content can still be rejected by guarded content
sanity checks before any GitHub write.

Conflict on stale read state:
The agent submits an intent using an old branch head or old Git blob SHA.
Gateway returns a conflict and requires a fresh repository read.

Follow-up on the same PR:
The agent reads the current Gateway PR head and submits
`update_gateway_pr_write_set`. Gateway updates the existing Gateway-created PR
when parent PR ownership, parent head, policy, and read-state checks pass.
