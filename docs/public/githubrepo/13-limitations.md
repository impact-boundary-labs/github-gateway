# Limitations

This page lists known limitations for Self-hosted GitHub Gateway v1.3.

Self-hosted GitHub Gateway v1.3 is useful for evaluating the write-boundary model on test
repositories. It is not a guarantee about future hosted product behavior,
arbitrary repositories, or semantic correctness.

## Self-hosted Scope

Self-hosted GitHub Gateway v1.3 is a controlled self-hosted release for
evaluating the write-boundary model.

Use it first with:

- a test repository
- small reviewable full-file changes
- explicit policy scope
- a read-only agent environment
- human review before merge

Do not use it as a first step on broad repository sets or high-risk production
repositories.

## Self-hosted Setup

Docker Desktop is required for Self-hosted GitHub Gateway v1.3.

The current setup recommends dashboard manifest setup first, with manual PEM
wiring as fallback.

- create or configure a GitHub App
- store the private key locally for the Gateway
- install the app only on selected repositories
- configure `INTENT_GATEWAY_ALLOWED_REPOS`
- restart the Gateway after `.env` changes

## Intent Protocol

Self-hosted GitHub Gateway v1.3 uses structured JSON intents.

Limitations:

- no native patch parser
- no ergonomic SDK yet
- no full CLI workflow as the primary public interface yet
- full-file payloads only
- raw intent protocol is still visible to advanced users

Local helpers are convenience tools. They are not separate security boundaries.

## Review And Merge

GitHub Gateway does not:

- auto-merge
- replace human review
- replace CI
- replace branch protection
- prove semantic correctness
- prove business correctness
- guarantee runtime behavior

Admitted means the Gateway admitted repository impact under configured checks.
It does not mean the change is correct or should be merged.

## Repository Scope

The first Self-hosted GitHub Gateway v1.3 run flow is designed for small, reviewable repository changes.

It is not intended for:

- binaries
- generated assets
- huge refactors
- broad repository migrations
- large dependency rewrites
- arbitrary human-created PR updates
- general Git hosting

Follow-up support in 1.3 is intended for Gateway-created write-set PRs that are
still known to the same local Gateway state. It is not a generic updater for
single-file `write` PRs, arbitrary human-created PRs, or PRs whose local parent
record is unavailable.

## Policy Scope

Policy controls repository paths. It does not understand business semantics.

Example:

```yaml
allowed_paths:
  - config/*
blocked_paths:
  - security/*
  - .github/*
```

`config/*` means direct files under `config/`, not nested paths.

## Content Sanity Scope

Content sanity is intentionally narrow. It blocks executable headers, binary or
non-UTF-8 content in guarded modes, and invalid YAML/JSON for those file types.

It is not:

- a semantic correctness check
- a secret scanner
- a data loss prevention system
- a guarantee that an allowed file contains no sensitive value

Use repository policy, isolated agent credentials, human review, and normal
secret-handling controls to keep secrets out of allowed paths.

## Agent Isolation

The agent must not have GitHub write credentials.

If this command succeeds from the agent environment, the demo is not isolated:

```powershell
git -c credential.helper= push --dry-run origin HEAD:refs/heads/ggw-readonly-push-test
```

The Runner Key does not grant GitHub write access. A successful push means some
other credential is present in the environment.

## Data And Telemetry

Self-hosted Gateway runtime state stays local to the user's environment.

The runtime does not send telemetry to Impact Boundary Labs. GitHub API calls
still go to GitHub through configured credentials.

Website analytics, if used for a public site, are separate from Gateway runtime
telemetry and should be disclosed separately.

## Current And Later

Now:

- Self-hosted GitHub Gateway v1.3
- Runner Key
- Guarded PR creation
- same-effect PR reuse
- same-PR follow-up
- story demo
- local dashboard Activity

Later directions may include:

- better docs and installation media
- more polished Guard Result presentation
- review feedback helpers
- read-state helper tooling
- hosted/cloud product path
- additional adapters

Future directions should not be treated as current availability.
