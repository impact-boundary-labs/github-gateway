# GitHub Gateway by Impact Boundary Labs

GitHub Gateway by Impact Boundary Labs is a write boundary for coding agents.

It lets agents propose repository changes without giving the agent GitHub write
access. The Gateway validates structured intents against repository scope,
policy, declared state, and content sanity before any GitHub write is attempted.
Admitted intents become reviewable pull requests through the configured GitHub
App. Blocked or conflicted intents create no branch, no commit, and no pull
request.

## Who This Is For

Use GitHub Gateway when you want to evaluate coding agents without handing them
direct GitHub write credentials.

It is intended for:

- engineering teams testing agent-assisted repository changes
- platform and security reviewers evaluating credential separation
- agent builders who need a clear write boundary for GitHub impact
- operators who want reviewable pull requests rather than direct agent pushes

For the first evaluation, use a test repository. Do not start with production
repositories or broad repository installations.

## Current Preview Status

The current public path is **GitHub Gateway Self-hosted 1.3**.

It runs locally with Docker and provides:

- local dashboard
- GitHub App write identity
- scoped Runner Keys for agent-to-Gateway submit
- policy file checks
- state binding checks
- content sanity checks
- reviewable pull request creation
- same-effect PR reuse
- follow-up updates to the same Gateway-created PR
- sanitized Dashboard Activity rows
- compact Guard Result PR bodies
- story demo for the expected preview flow

This is a technical preview. It is not a production release, does not prove
semantic correctness, and does not auto-merge. Human review remains required.

## Core Model

```text
Agent reads repository state.
Agent submits structured intent.
GitHub Gateway decides admission.
GitHub App creates pull request impact, or nothing is written.
```

The agent should not have:

- GitHub write token
- GitHub App private key
- SSH key with write access
- stored Git Credential Manager write credential
- `gh auth` session with write access

The agent may use read-only repository state from a fine-grained GitHub Read
Token, a local checkout, or helper tooling. The Gateway validates declared
state against GitHub before writing.

## Outcomes

| Outcome | Meaning | Repository impact |
| --- | --- | --- |
| Admitted | The intent passed Gateway checks. | A reviewable PR is created or updated. |
| Reused | Equivalent admitted work already exists. | Existing Gateway PR is reused. |
| Follow-up | A validated update targets an existing Gateway PR. | Same PR is updated. |
| Blocked | Policy, scope, content, or request checks failed. | No branch, commit, or PR. |
| Conflict | Declared state was stale or could not be trusted. | No new impact. |
| Verification required | The Gateway could not safely verify final state. | Operator attention required. |

## Documentation Map

Start here:

- [Quickstart](02-quickstart.md)
- [Self-hosted preview](03-self-hosted-preview.md)
- [GitHub App setup](04-github-app-setup.md)
- [Runner Key](05-runner-key.md)
- [Agent instructions](06-agent-instructions.md)

Configuration and protocol:

- [Policy YAML](07-policy-yaml.md)
- [Intent JSON reference](08-intent-json-reference.md)
- [Local runner](09-local-runner.md)
- [Story demo](10-story-demo.md)

Review, security, and operations:

- [Guard Result and PR body](11-guard-result.md)
- [Security model](12-security-model.md)
- [Limitations](13-limitations.md)
- [Troubleshooting](14-troubleshooting.md)
- [Operations](15-operations.md)
- [Validation checklist](16-validation-checklist.md)

Website-facing overview documentation lives separately under
`docs/public/homepage/`.

## What GitHub Gateway Does Not Do

GitHub Gateway does not:

- prove semantic correctness
- review code quality
- run all possible tests
- auto-merge pull requests
- replace human review
- replace branch protection
- give the agent permission to write directly to GitHub

It controls repository impact from structured agent proposals.
