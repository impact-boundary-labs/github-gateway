# Demo and Live Run

The story demo is the shortest path from product claim to observable behavior.
It shows the same point the rest of the homepage docs make, but it shows it as
a sequence of decisions rather than as a description.

The agent can read the repository directly, but repository impact only happens
through GitHub Gateway.

## What the Demo Shows

The demo is structured around five outcomes that make the boundary visible.

First, it shows a blocked path. A request outside the allowed repository policy
should create no branch, no commit, and no pull request.

Second, it shows a small allowed change under the test policy. That request
should become a reviewable pull request through the Gateway.

Third, it resubmits the same effect. Instead of creating a duplicate review
object, the Gateway can reuse the existing Gateway-created pull request.

Fourth, it submits a validated follow-up to that same pull request. If the
parent head and file state still match, the Gateway can update the same review
object.

Fifth, it shows a stale follow-up. When the parent state has changed, the
Gateway stops the request before write impact and tells the agent to re-read
state.

## Why the Demo Matters

This is not just a convenience script. It is the clearest public demonstration that the
product is about repository impact, not just about prompts or dashboards.

If a bad path creates no pull request, that matters. If an allowed change
creates a reviewable pull request through the GitHub App, that matters. If a
repeat attempt reuses the same pull request instead of generating duplicate
noise, that matters. If a stale follow-up is blocked before write, that matters.

Each step turns the abstract boundary claim into something the operator can
inspect.

## What To Watch During the Demo

The pull request result is only part of the story. The operator should also
watch the Dashboard Activity feed while the demo runs.

The Activity feed should show the sanitized Gateway decisions in order. It
should make the outcome visible without exposing tokens, raw payloads, or full
intent JSON. That matters because the dashboard is not meant to become a raw
request dump. It is meant to show recognized Gateway decisions in a way an
operator can actually use.

## What the Demo Does Not Prove

The demo does not prove that the admitted code change is semantically correct.
It does not replace human review. It does not replace CI. It does not show a
general-purpose autonomous engineering system.

What it demonstrates is narrower and more useful: repository impact goes through the
Gateway, and the Gateway can stop bad or stale requests before they create
review objects in GitHub.

## Where To Go Next

For the technical setup behind the demo, continue with:

- [Self-hosted GitHub Gateway v1.3](05-self-hosted-page.md)
- [Technical story demo docs](../githubrepo/10-story-demo.md)
- [Technical quickstart](../githubrepo/02-quickstart.md)
