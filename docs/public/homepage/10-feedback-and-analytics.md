# Feedback and Product Signals

The public feedback path for GitHub Gateway is the Impact Boundary Labs GitHub
organization:

- [impact-boundary-labs on GitHub](https://github.com/impact-boundary-labs)

That path keeps feedback tied to the product surface people can inspect in
public: documentation, self-hosted packaging, issues, and visible repository work.

## How To Read the Telemetry Claim

Self-hosted GitHub Gateway does not present itself as a telemetry-collecting
runtime. The self-hosted Gateway does not send prompts, repository data,
tokens, payloads, or usage analytics back to Impact Boundary Labs.

That statement should be read precisely. It describes Gateway runtime behavior.
It does not mean that no network traffic exists at all. GitHub API calls still
go to GitHub through the configured GitHub App and the credentials the operator
chose to use.

## Website Analytics Are a Separate Topic

Website analytics, if used on a public site, are a separate matter from Gateway
runtime behavior. A public site may use privacy-conscious analytics to
understand page visits or documentation traffic. That should be disclosed
plainly and should not be mixed into the product claim about the self-hosted
runtime.

This separation matters because "site traffic measurement" and "runtime
telemetry from the repository boundary" are not the same thing.

## The Practical Public Message

The simplest public wording is this:

the self-hosted Gateway runtime does not send telemetry to Impact Boundary
Labs, while GitHub API calls still go to GitHub through the GitHub App and
credentials configured by the operator.

That is specific enough to be useful and narrow enough to be credible.

## What Helpful Feedback Looks Like

Good feedback for GitHub Gateway usually falls into a few concrete categories:

- setup friction in Self-hosted GitHub Gateway v1.3
- unclear documentation or missing operator guidance
- Dashboard wording that hides what the Gateway actually decided
- mismatch between public claims and observed behavior
- review-surface issues around Guard Result or Agent Message output

That kind of feedback is more useful than broad reactions because the product
itself is narrow and concrete. The best reports tie a claim, a workflow step, or
an observed outcome to something that a maintainer or evaluator can inspect.

## Why This Matters Publicly

The public feedback path is part of the product story. GitHub Gateway is being
presented as a technical system with bounded claims, so public discussion should
stay anchored to observable behavior, documentation clarity, and the quality of
the boundary itself.

That makes the public surface stronger. It keeps feedback tied to what the
product actually does today instead of drifting into vague expectations about
general AI tooling.

## Where To Go Next

If you want to understand the product before sending feedback, continue with:

- [Overview](01-overview.md)
- [GitHub Gateway](04-github-gateway-page.md)
- [Security and boundary model](07-security-page.md)
