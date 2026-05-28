# GitHub Gateway

GitHub Gateway is a write boundary for coding agents. It gives engineering
teams a way to let agents propose repository changes without handing those
agents direct GitHub write access.

That is the product in plain terms. The agent can still read the repository and
prepare a change. What it does not get by default is the right to create
branches or open pull requests directly. Instead, the agent submits a
structured request to GitHub Gateway. The Gateway checks that request and, if
it is admitted, the configured GitHub App creates the reviewable GitHub impact.

## The Product Job

GitHub Gateway exists to answer one narrow question well: when a coding agent
wants to create repository impact, what stands between that request and a real
GitHub write?

Many systems answer that question with "the agent has a token, so it writes."
GitHub Gateway answers it with a boundary. The request becomes explicit,
structured, and inspectable before it becomes a branch or a pull request.

This is why the product is framed as a write boundary rather than as a generic
assistant shell. The value is not that the agent can edit text. The value is
that write impact is mediated instead of ambient.

## What the Product Actually Changes

GitHub Gateway changes the trust model for repository automation.

In a direct-write setup, the same agent process may read repository state and
write to GitHub with one broad credential. In a Gateway setup, the read path
and the write path are separate. The agent can still inspect state and decide
what it wants to do, but the GitHub App private key stays behind the Gateway.

That means the agent can submit a request without being the thing that pushes a
branch or opens a pull request.

For teams evaluating coding agents, this is a meaningful operational
difference. It reduces the need to give every agent runtime direct write power
and makes repository impact easier to reason about.

## What GitHub Gateway Checks

Before any admitted GitHub write exists, GitHub Gateway checks whether the
request is in the allowed repository scope, whether it matches the Runner Key
scope, whether the target paths are allowed by repository policy, whether the
declared source state still matches GitHub, and whether the request passes the
current content constraints.

Those checks matter because they happen before repository impact exists. They do
not attempt to prove that the resulting code is perfect. They determine whether
this request may become reviewable repository impact at all.

That is the right level of responsibility for a boundary like this. It is
closer to admission control than to semantic review.

## What an Admitted Request Produces

When a request is admitted, GitHub Gateway creates a reviewable pull request
through the configured GitHub App. In some cases, the Gateway may reuse an
existing Gateway-created pull request for the same effect instead of creating a
new one. In controlled follow-up scenarios, it may update the same
Gateway-created pull request after validating the parent head and current file
state.

From the outside, this means the review surface stays legible. A reviewer sees
a pull request with a compact Guard Result and, if provided, an Agent Message
for context. The reviewer does not see raw payloads, tokens, PEM files, or a
dump of internal policy machinery.

That is an important distinction. The system is designed to make the admitted
effect visible, not to expose internal secret or runtime material.

## What a Non-Admitted Request Produces

When a request is blocked or conflicted, there is no branch, no commit, and no
pull request. That sounds simple, but it is central to the product claim.

The value of a boundary is often clearest when something goes wrong. If the
agent targeted the wrong path, relied on stale state, or sent a request outside
its allowed scope, the system should fail before GitHub impact exists. GitHub
Gateway makes those decisions visible through its activity and decision model
without turning every mistake into repository clutter.

This is why the product language emphasizes reviewable impact, not just
automation speed. The difference between "the request failed" and "the request
failed without creating GitHub artifacts" matters in practice.

## Why the GitHub App Belongs to the Gateway

The GitHub App private key is the write identity for admitted work. It should
belong to the Gateway, not to the agent.

That separation is not cosmetic. If the agent holds the write identity, the
boundary is bypassed in the most important place. The agent can still write
even if the Gateway would have blocked the request. By keeping the GitHub App
private key on the Gateway side, the system makes admission a real precondition
for GitHub impact.

The agent may still hold read-only state access. It may also hold a Runner Key
for submission to the Gateway. Those are different credentials with different
jobs.

## What the Product Is For

GitHub Gateway is for teams evaluating coding agents on real repositories who
do not want the default answer to be "give the agent a GitHub write token."

It is useful for platform and infrastructure teams that want a narrower
repository write path. It is useful for operators who want reviewable pull
request impact instead of direct pushes. It is useful for experimentation on
test repositories where the team wants to observe how the agent behaves without
letting every attempt become a raw GitHub write.

It is not trying to be every possible agent tool. It is specifically concerned
with how repository write impact is admitted and materialized.

## What the Product Does Not Claim

GitHub Gateway does not prove semantic correctness. It does not replace code
review. It does not replace CI. It does not auto-merge. It does not claim to
prevent every malicious or unsafe action an agent could attempt elsewhere. It
does not claim to make coding agents "safe" in a broad marketing sense.

Those are not accidental omissions. They are deliberate limits on the claim.

The product claim is narrower: GitHub Gateway controls how structured agent
write requests become repository impact in GitHub.

## How To Evaluate It

The best way to evaluate GitHub Gateway is to look at the outcomes:

- can the agent propose work without holding GitHub write access?
- does allowed work become a reviewable pull request?
- do repeated equivalent requests reuse an existing Gateway-created pull
  request?
- can a validated follow-up update the same pull request?
- do blocked or stale requests create no repository impact?

Those questions tie the product story to observable behavior rather than to
abstract promises.

## Read More

If you want the product story in technical detail, continue with:

- [Technical overview](../githubrepo/01-overview.md)
- [Quickstart](../githubrepo/02-quickstart.md)
- [Security model](../githubrepo/12-security-model.md)
- [Guard Result and PR body](../githubrepo/11-guard-result.md)
