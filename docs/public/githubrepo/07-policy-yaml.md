# Policy YAML

GitHub Gateway reads repository policy from:

```text
.github/intent-gateway.yaml
```

The policy is created by the human repository owner before the demo. After that,
test policy should block Gateway/agent writes to `.github/*`.

## Self-hosted Policy Goal

The first test policy should be small and explicit:

- allow simple config files
- block sensitive paths
- block later Gateway/agent writes to GitHub configuration
- keep the demo easy to inspect

## Example Policy

```yaml
mode: guarded
allowed_paths:
  - config/*
blocked_paths:
  - security/*
  - .github/*
```

This policy means:

- direct files under `config/` may be admitted if other checks pass
- files under `security/` are blocked
- files under `.github/` are blocked

## Direct Path Behavior

`config/*` means direct files under `config/`.

Allowed by `config/*`:

```text
config/app.yaml
config/live-demo-pass.yaml
```

Not allowed by `config/*`:

```text
config/nested/app.yaml
config/env/prod.yaml
```

If you want nested paths, policy must explicitly allow them. Keep the first
test simple and use direct files.

## allowed_paths

`allowed_paths` defines where the Gateway may consider writes.

An intent still must pass:

- Runner Key repo/branch scope
- path normalization
- blocked path checks
- state binding checks
- content sanity checks for executable headers, binary/text validity, and
  parseable YAML/JSON where applicable
- materialization verification

Being in an allowed path does not mean a PR is automatically correct or should
be merged.

## blocked_paths

`blocked_paths` defines paths that must not be written through the Gateway.

Use it for:

- security-sensitive files
- GitHub workflow and repository configuration
- secrets or credentials
- areas outside the first demo scope

For Self-hosted GitHub Gateway v1.3, keep `.github/*` blocked after initial human setup. The human
owner creates `.github/intent-gateway.yaml`; later agent/Gateway writes to that
area are blocked.

## Policy Modes

Self-hosted GitHub Gateway v1.3 uses `guarded` as the default mode.

| Mode | Public meaning |
| --- | --- |
| `fast` | Advanced mode for lighter checks. Do not use as the first self-hosted path. |
| `guarded` | Self-hosted default. Balanced policy, state, and reviewable PR checks. |
| `strict` | Advanced mode for stricter workflows. Use only when intentionally configured. |

Do not make `fast` or `strict` central in the first setup flow. Start with
`guarded`.

## Common Mistakes

### Mistake: expecting config/* to allow nested paths

If policy says:

```yaml
allowed_paths:
  - config/*
```

Then this path is not allowed:

```text
config/nested/file.yaml
```

Use a direct path such as:

```text
config/file.yaml
```

### Mistake: allowing .github/* for agent writes

Do not allow `.github/*` in the first test policy. That area controls
repository automation and policy. Keep it human-owned for initial setup.

### Mistake: putting secrets under allowed paths

Do not place secrets, private keys, or token files under allowed paths. GitHub
Gateway is not a data loss prevention system.

### Mistake: treating policy as code review

Policy controls whether a path is in scope for Gateway impact. It does not prove
semantic correctness, business correctness, runtime behavior, or code quality.

## First Policy Checklist

Before running the story demo:

- `.github/intent-gateway.yaml` exists on the target branch
- `mode` is `guarded`
- `allowed_paths` includes `config/*`
- `blocked_paths` includes `security/*`
- `blocked_paths` includes `.github/*`
- demo path uses a direct `config/<file>.yaml` path
- blocked demo path uses `security/<file>.yaml`
