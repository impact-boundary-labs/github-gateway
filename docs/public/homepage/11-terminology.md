# Terminology

GitHub Gateway uses a small set of terms repeatedly. The terms matter because
the product is about a specific write boundary, not a vague idea of agent
supervision. This page explains the public vocabulary in the simplest useful
form.

## Impact Boundary Labs

Impact Boundary Labs is the company and brand behind GitHub Gateway. The name
signals the broader systems idea: agent proposals and external impact should
not be treated as the same thing.

## GitHub Gateway

GitHub Gateway is the product. It is a write boundary for coding agents on
GitHub repositories. An agent can propose repository changes, but GitHub
Gateway decides whether those changes may become pull request impact.

## Self-hosted GitHub Gateway

Self-hosted GitHub Gateway v1.3 is the current public product variant. It is the
self-hosted release that runs locally, keeps the GitHub App private key and
runtime state under operator control, and demonstrates the boundary on a test
repository.

This is the serious evaluation path available today.

## Intent

An intent is the structured change request submitted by the agent. The term
should remain in the vocabulary because it names the technical concept clearly.

The agent does not merely send prose. It submits a structured intent that says
what repository change it wants, what state it believes it read, and where the
requested impact should land.

In this documentation, "intent" refers to that technical change request. It
should not be confused with older internal product naming.

## Runner Key

The Runner Key is the agent-to-Gateway credential. It authorizes a specific
agent environment to submit intents to a specific Gateway setup for a given
repository and branch or base-branch scope.

It is not a GitHub token and it does not grant direct GitHub write access. That
distinction is essential to the product model.

## GitHub App Private Key

The GitHub App private key belongs to the Gateway write identity. It is how the
configured GitHub App can create branches and pull requests after admission.

The public rule is simple: the GitHub App private key belongs to the Gateway,
not to the agent.

## GitHub Read Token

The GitHub Read Token is the agent's read-only path to repository state when a
local checkout or other read source is not being used. It helps the agent read
branch heads, file state, and pull request state without giving it GitHub write
authority.

This is why the public docs separate read access from write access so clearly.

## Guard Result

The Guard Result is the compact public summary the Gateway places in a
Gateway-created pull request. It explains the Gateway outcome at a level useful
for review without exposing secrets, raw payloads, or internal secret material.

It is not meant to be a full execution log. It is a review-facing result
surface.

## Agent Message

The Agent Message is optional review context submitted by the agent. It can
explain the purpose of a change, the intended scope, or a short safety note for
reviewers.

It is public in the pull request when admitted, so it should stay short and it
must not contain secrets or private runtime data.

## Admission and Repository Impact

Admission is the decision point where the Gateway decides whether a structured
intent may become repository impact. Repository impact means the creation or
update of reviewable GitHub objects such as a pull request through the
configured GitHub App.

This distinction is the core of the product model. Proposal is not impact.
Impact exists only after admission and materialization.

## Compatibility Names

Some runtime file names and environment variables still use `intent-gateway` or
`INTENT_GATEWAY_*` prefixes for compatibility with the current self-hosted package.
Those are technical runtime names, not the public product name.

The public product name remains **GitHub Gateway by Impact Boundary Labs**.

## Where To Go Next

If you want the technical definitions and protocol detail behind these terms,
continue with:

- [Technical overview](../githubrepo/01-overview.md)
- [Runner Key](../githubrepo/05-runner-key.md)
- [Intent JSON reference](../githubrepo/08-intent-json-reference.md)
- [Guard Result and PR body](../githubrepo/11-guard-result.md)
