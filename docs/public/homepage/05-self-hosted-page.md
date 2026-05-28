# Self-hosted GitHub Gateway

Self-hosted GitHub Gateway is the current public evaluation path for the
product. It runs locally, keeps the main runtime state under operator control,
and demonstrates the boundary model on a test repository before a team decides
how far it wants to take the workflow.

Self-hosted GitHub Gateway v1.3 matters because it turns the product claim into
something a team can inspect directly. Instead of reading a promise about
controlled repository impact, you can start the Gateway, configure a test
repository, create a Runner Key, and watch the Dashboard Activity feed while
the story demo exercises admitted, reused, follow-up, blocked, and conflict
outcomes.

## What Self-hosted GitHub Gateway v1.3 Demonstrates

Self-hosted GitHub Gateway v1.3 demonstrates the core repository boundary in a local
environment. The agent proposes repository changes. The Gateway decides whether
those changes may become pull request impact. The configured GitHub App is the
write identity for admitted work.

This means the evaluation is not merely about UI setup. It is about observing
whether the claimed outcomes actually happen:

- allowed work becomes a reviewable pull request
- equivalent work can reuse an existing Gateway-created pull request
- validated follow-up can update the same pull request
- blocked or stale requests create no repository impact

That is the practical purpose of Self-hosted GitHub Gateway v1.3.

## What Stays Local

The self-hosted path is designed so that the main runtime artifacts stay with
the operator rather than disappearing behind a hosted control plane.

In Self-hosted GitHub Gateway v1.3 setup, the following remain local:

- the GitHub App private key used by the Gateway write identity
- the local `state.db`
- Runner Keys
- GitHub Read Token storage for the agent
- local logs
- repository allowlist configuration
- the self-hosted data directory

The self-hosted runtime itself does not send telemetry. GitHub API calls still
go to GitHub because the product is operating on GitHub repositories, but the
Gateway is not shipping prompts, payloads, or usage analytics back to Impact
Boundary Labs.

## How a First Evaluation Usually Goes

A first evaluation should stay small and deliberate.

Most teams start by unpacking Self-hosted GitHub Gateway v1.3, starting the Gateway locally, opening
the dashboard, creating a GitHub App through the dashboard template flow,
installing that app only on a test repository, creating a Runner Key, and then
running the story demo against a narrow policy on that test repository.

The goal is not to automate a whole engineering organization on day one. The
goal is to observe the boundary on a repo small enough that every outcome is
easy to inspect.

That is also why the dashboard matters. After the demo runs, the operator
should check the Dashboard Activity feed. The feed shows the Gateway decisions
without exposing secrets, raw payloads, or full intent JSON.

## The Credential Split Still Matters Here

Self-hosted GitHub Gateway v1.3 uses three distinct roles.

The GitHub App private key belongs to the Gateway write identity. The Runner
Key belongs to the agent-to-Gateway submission path. The GitHub Read Token, if
used, belongs to the agent's read-only repository state access.

These are not interchangeable tokens. If they collapse into one broad write
credential, the evaluation loses its meaning. Self-hosted GitHub Gateway v1.3 is only a
clean demonstration when the agent can read and propose, but cannot bypass the
Gateway and push directly.

That is why the push-isolation warning is important. If `git push` works from
the agent environment, the demo is not isolated.

## Runtime Compatibility Note

Some runtime files and environment variables still use the `intent-gateway` or
`INTENT_GATEWAY_*` prefix for compatibility with the current self-hosted package.
The public product name remains **GitHub Gateway by Impact Boundary Labs**.

That distinction is mostly relevant during setup. It does not change the public
product description.

## What This Release Is For

Self-hosted GitHub Gateway v1.3 is for teams that want to evaluate a repository
write boundary with their own Docker runtime, their own GitHub App, and their
own test repository. It is best suited to controlled evaluation, small
reviewable changes, and careful inspection of the outcome model.

It is not presented as a fully managed hosted product, and it is not the right
frame for broad automation claims. Its value is that it lets a team inspect the
boundary itself.

## Where To Go Next

For deeper setup and operator detail, continue with:

- [Technical quickstart](../githubrepo/02-quickstart.md)
- [GitHub App setup](../githubrepo/04-github-app-setup.md)
- [Story demo](../githubrepo/10-story-demo.md)
- [Security model](../githubrepo/12-security-model.md)
