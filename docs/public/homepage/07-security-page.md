# Security and Boundary Model

GitHub Gateway addresses a specific security and systems problem: too many
agent integrations hand direct GitHub write credentials to the same process
that reads repository state and decides what to change. That may be expedient,
but it means the agent is also the thing that can materialize branches and pull
requests directly.

Impact Boundary Labs takes a different approach. The agent can still read,
reason, and propose work. The write identity stays behind the Gateway.

## The Security Claim

The right security claim for GitHub Gateway is narrow and concrete.

GitHub Gateway reduces the need to give every coding agent GitHub write access.
It places a boundary before repository impact exists. It checks repository
scope, policy, and declared state before admitted work is materialized through
the configured GitHub App.

That is not the same as claiming that the system proves correctness or prevents
all malicious behavior. It does not. The value is in controlling write impact,
not in claiming universal safety.

## The Credential Split

The boundary depends on a real credential split.

The GitHub App private key belongs to the Gateway write identity. That key is
what allows admitted work to become a branch and a pull request in GitHub. The
agent should never hold that private key.

The Runner Key belongs to the submission path between agent and Gateway. It is
not a GitHub token. It authorizes the agent to submit structured intents to the
Gateway for a particular repository and branch or base-branch scope.

The GitHub Read Token, when used, belongs to the agent's read-only repository
state access. It helps the agent inspect branch heads, file state, and pull
request heads without giving it direct GitHub write authority.

Those credentials do different jobs. If they collapse into one broad write
credential, the boundary stops being meaningful.

## Why the GitHub App Private Key Stays With the Gateway

GitHub requires a real identity for write operations such as branch creation and
pull request creation. In GitHub Gateway, that identity belongs to the Gateway.

This matters because admission is supposed to be a precondition for write
impact. If the agent held the GitHub App private key or some equivalent GitHub
write credential, it could bypass the boundary. The system would still have a
dashboard and policy files, but the most important separation would be gone.

Keeping the GitHub App private key on the Gateway side is therefore not just a
deployment detail. It is part of the product contract.

## What the Boundary Checks Before Write Impact

GitHub Gateway does not accept a write request merely because an agent wants
one. It checks whether the repository is in scope, whether the branch scope is
allowed for that Runner Key, whether the path is allowed by the repository
policy, whether the agent's declared source state still matches GitHub, and
whether the request fits current content constraints.

These checks are important because they happen before repository impact exists.
They define the difference between "the system later noticed a bad change" and
"the system prevented that request from becoming a pull request at all."

That is the operational meaning of the boundary.

## What No-Impact Outcomes Mean

A blocked, conflicted, or otherwise non-admitted request should produce no
branch, no commit, and no pull request. This is one of the most important
security properties in Self-hosted GitHub Gateway v1.3 because it reduces cleanup work and
keeps bad or stale attempts from becoming review objects.

The request is still visible as a Gateway decision. That is useful for
operators and for debugging. But visibility is not the same as write impact.

This is how GitHub Gateway makes agent write activity more inspectable without
making every failed attempt a GitHub side effect.

## What the Product Does Not Prove

GitHub Gateway does not prove semantic correctness. It does not prove business
correctness. It does not replace code review. It does not replace CI. It does
not claim to perform full data-loss prevention. It does not prove that an agent
understood the code it modified.

These are not edge cases hidden in a footnote. They are part of the honest
boundary of responsibility. The product controls repository write impact from
structured proposals. It does not claim to judge the full meaning or quality of
the resulting code.

## Ambient Write Access Still Matters

Self-hosted GitHub Gateway v1.3 includes an isolation warning for a reason. If `git
push` still works from the agent environment because of an existing SSH key,
stored credential helper entry, or broad GitHub token, then the demonstration
is no longer clean. The agent can bypass the Gateway and write directly.

This is why a no-write check in the agent environment matters. The product is
strongest when the operator can say: the agent can read state and submit
structured requests, but it cannot materialize GitHub writes on its own.

## Telemetry and Data Boundaries

Self-hosted GitHub Gateway does not present itself as a telemetry-heavy control
plane. The runtime does not send prompts, repository data, tokens, payloads, or
usage analytics back to Impact Boundary Labs.

That does not mean nothing ever leaves the machine. GitHub API calls still go
to GitHub through the configured GitHub App and the user-controlled
credentials. That distinction matters because it avoids the false marketing
claim that the system is completely offline or self-contained in every sense.

Website analytics, if used on a public site, should be described separately
from Gateway runtime behavior. Website traffic measurement and Gateway runtime
telemetry are different subjects and should stay separate in public wording.

## How To Read the Security Story

The strongest reading of GitHub Gateway is not "this product makes agents safe."
The strongest reading is: it narrows the write path, keeps the GitHub write
identity on the Gateway side, and makes repository impact more explicit before
it exists.

That is a precise claim, and it is one teams can evaluate directly.

## Where To Go Next

For the technical version of this model, continue with:

- [Technical security model](../githubrepo/12-security-model.md)
- [Runner Key](../githubrepo/05-runner-key.md)
- [GitHub App setup](../githubrepo/04-github-app-setup.md)
- [Guard Result and PR body](../githubrepo/11-guard-result.md)
