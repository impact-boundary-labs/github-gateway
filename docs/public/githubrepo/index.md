# Public Documentation

This is the public documentation layer for **GitHub Gateway by Impact Boundary
Labs**.

Public technical documentation lives here:

- [GitHub Gateway docs](01-overview.md): product documentation for
  Self-hosted GitHub Gateway v1.3, including setup, credentials, policy, intents, Guard
  Results, security model, limitations, troubleshooting, and validation
  guidance.

## Current Public Path

Self-hosted GitHub Gateway v1.3 is the current public path. It is a local
Gateway for evaluating controlled repository impact from coding agents on a
test repository.

The core public message is:

```text
Let coding agents open pull requests without GitHub write access.
```

Agents can read repository state and propose structured changes. GitHub Gateway
decides whether those changes may become pull request impact. GitHub writes
happen through the configured GitHub App after admission.

## Documentation Boundaries

Use `docs/public/githubrepo/` as the Self-hosted GitHub Gateway v1.3 contract.

Older or deeper documents outside `docs/public/githubrepo/` may contain internal notes,
working names, implementation details, or historical context. They are not the
public documentation set.

Website-facing overview documentation lives separately under
`docs/public/homepage/`. The technical setup and protocol reference stay under
`docs/public/githubrepo/`.

## Safety Of This Documentation Layer

Public docs must not contain real tokens, private keys, Runner Keys, read
tokens, local private paths, private repository names, raw payloads, raw
responses, or private logs. Use placeholders such as `OWNER/REPO`,
`TARGET_BRANCH`, `<runner-key>`, and `<github-read-token>` in public examples.
