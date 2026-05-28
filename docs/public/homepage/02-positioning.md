# Why Agent Writes Need a Boundary

GitHub Gateway is easiest to understand if you start with the failure mode it
is trying to avoid. Most coding-agent setups give one process both visibility
into repository state and the ability to write directly to GitHub. The agent
can read files, inspect pull requests, push branches, and open new pull
requests with the same credential.

That is convenient, but it is also a blunt trust model. It means stale reads,
bad retries, wrong file targets, and malformed requests can turn into real
repository impact immediately. The system may still catch some of those changes
later through review or CI, but by then the branch, pull request, and GitHub
noise already exist.

Impact Boundary Labs takes a narrower view of the problem. The question is not
whether an agent should be allowed to think, plan, or inspect repository state.
The question is whether every agent process should also be trusted to
materialize repository writes directly.

## The Positioning in One Sentence

GitHub Gateway lets coding agents open reviewable pull requests without giving
the agent GitHub write access.

That sentence matters because it is concrete. It does not promise to solve all
security or correctness problems. It describes a specific change to the write
path: the agent can still propose work, but the write identity is kept behind a
boundary.

## The Problem With Direct Write Credentials

When an agent holds a broad GitHub write token or equivalent ambient write
access, the system effectively treats every proposed change as already halfway
materialized. The write step becomes an implementation detail of the agent
runtime rather than a separate decision point.

That creates several practical issues.

The first is state drift. An agent may read a file or a pull request head, plan
a change, and then act on stale state. If direct push is available, the stale
result can still become a new branch or pull request.

The second is policy ambiguity. Repository policies are often enforced by
convention, helper code, or prompt discipline. Those mechanisms are useful, but
they do not create a hard distinction between "proposal" and "external effect."

The third is operational cost. Bad attempts create GitHub objects, CI load,
review noise, and cleanup work even when they never should have reached review
in the first place.

GitHub Gateway addresses these problems by separating the agent request from
the GitHub write identity that can materialize it.

## The Boundary Model

The public model is simple:

```text
Agent proposes intent.
GitHub Gateway decides admission.
GitHub App creates pull request impact.
```

The agent submits a structured intent. The Gateway checks repository scope,
policy, state binding, and content constraints. If the request is admitted, the
configured GitHub App creates or updates a reviewable pull request. If the
request is blocked or conflicted, there is no branch, no commit, and no pull
request.

This changes the meaning of failure. A bad or stale request is no longer just a
bad GitHub write that must be cleaned up later. It becomes a visible Gateway
decision with no repository impact.

## Why GitHub Is the First Product Surface

GitHub is a useful first domain because the boundary outcome is easy to inspect.
Either a pull request exists or it does not. Either the same Gateway-created
pull request was reused or a new one was blocked. Either a follow-up updated
the existing guarded pull request or the request was stopped because the parent
head changed.

That clarity makes GitHub a good first product surface for Impact Boundary
Labs. The boundary is not an abstract theory. It becomes visible in pull
request creation, pull request reuse, and blocked write attempts that never
materialize.

## What Changes for the Operator

With GitHub Gateway, the operator is no longer forced to choose between two
equally unsatisfying modes: "the agent cannot write anything useful" or "the
agent has a token that can write directly to GitHub."

The operator can let the agent inspect repository state, prepare structured
change requests, and work quickly. At the same time, the operator can keep the
GitHub App write identity inside the Gateway boundary and inspect decisions
through the Dashboard Activity feed and the resulting pull requests.

That is a practical improvement in control. It does not remove the need for
review, but it reduces the number of places where direct write power has to be
trusted.

## What Reviewers and Teams Get

This model produces better review objects than direct agent pushes.

An admitted request becomes a reviewable pull request with a compact Guard
Result and, when provided, an Agent Message for context. An equivalent repeat
request can reuse the same Gateway-created pull request instead of creating
duplicates. A validated follow-up can update that same pull request instead of
splitting the work across uncontrolled branches.

Just as important, blocked or conflicted attempts do not create review debris.
The decision is still visible in Gateway Activity, but it does not become
repository impact.

## What This Positioning Does Not Claim

This is not a claim that GitHub Gateway makes agents trustworthy by itself. It
does not prove semantic correctness. It does not replace code review, CI, or
normal repository protections. It does not claim to stop every malicious action
an agent could attempt elsewhere.

The claim is narrower and more defensible: GitHub Gateway controls how
structured agent write requests become GitHub repository impact.

That is enough to be useful, and specific enough to evaluate honestly.

## Where To Go Next

If this explanation makes sense, the next pages are:

- [How GitHub Gateway works](03-how-it-works.md)
- [GitHub Gateway](04-github-gateway-page.md)
- [Security and boundary model](07-security-page.md)
- [Technical GitHub Gateway docs](../githubrepo/index.md)
