# Validation Checklist

This page is a public validation checklist for Self-hosted GitHub Gateway v1.3.
Use it to record or review a completed self-hosted smoke run without exposing
private data.

It intentionally does not publish private PR URLs, private repository names,
tokens, Runner Keys, PEM contents, logs, payloads, raw responses, local paths,
or internal test matrices.

## What To Validate

Check these behaviors on a test repository:

- source-free self-hosted ZIP starts with Docker
- `/livez` reports HTTP liveness
- dashboard loads locally
- GitHub App write identity can be configured
- GitHub App can be installed on one selected test repository
- Runner Key can be created from the dashboard
- Runner Key is shown only once
- local `data/agents.env` can hold agent runtime values
- GitHub Read Token guidance is read-only
- agent environment can be checked for no direct `git push`
- allowed config change can create a reviewable PR
- blocked path creates no repository impact
- content sanity block for an implemented format check creates no repository
  impact
- stale read-state creates conflict before impact
- same-effect request can reuse an existing Gateway PR
- follow-up can update the same locally known Gateway-created write-set PR
- dashboard Activity shows recognized structured Gateway decisions

For content sanity validation, use a fixture that matches the implemented
checks: executable `MZ`/ELF headers, binary or non-UTF-8 content in guarded
modes, or invalid YAML/JSON for those file types. Do not treat synthetic
key-like or token-like text in an otherwise valid allowed file as a content
sanity scanner test. GitHub Gateway Self-hosted v1.3 does not include semantic
analysis or a secret scanner.

## Story Demo Expected Outcomes

The story demo should produce these public-safe outcomes:

| Scenario | Expected decision | Expected repository impact |
| --- | --- | --- |
| blocked policy path | Blocked | no branch, no commit, no PR |
| allowed config change | Admitted | reviewable PR |
| same effect | Reused | existing Gateway PR reused |
| follow-up | Admitted | same Gateway write-set PR updated |
| stale parent PR head | Conflict | no new impact |

The dashboard Activity log should show sanitized rows for these decisions.

## Guard Result Validation

Gateway-created PRs should contain a compact Guard Result with:

- decision
- request status
- applies-to commit
- warning or review note
- optional Agent Message

PR bodies should not publish:

- full intent JSON
- full payloads
- base64 content
- tokens
- headers
- PEM files
- private keys
- full diffs
- full policy dumps
- internal database state

## Source-Free ZIP Smoke

The source-free self-hosted package should include:

- `github-gateway-self-hosted.tar`
- `docker-compose.yml`
- `.env`
- `README.md`
- start/stop/log helper scripts
- `docs/`
- `user-guide/`
- `examples/`
- `test-repo-template/`
- empty local `data/` and `secrets/` folders

It should not include:

- `.git`
- source directories required for building the binary
- real PEM files
- real `.env` secrets
- `state.db`
- Runner Keys
- GitHub tokens
- logs
- raw payloads
- raw responses

## Public Status Framing

Passing the Self-hosted GitHub Gateway v1.3 smoke and story demo means the flow
worked in that environment. It does not prove semantic correctness, future
production suitability, or that a PR should be merged.

Human review remains required.

## What To Record Publicly

Public validation notes may record:

- package version
- high-level outcome names
- sanitized decision/status names
- whether dashboard and demo flow passed
- whether source-free package contents looked correct

Public validation notes should not record:

- private repository names
- real PR URLs
- logs with private content
- tokens or credentials
- local private paths
- payload content
- raw request or response bodies
