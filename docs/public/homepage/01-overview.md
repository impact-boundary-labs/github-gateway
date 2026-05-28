# Impact Boundary Labs and GitHub Gateway

Impact Boundary Labs is building tooling for a simple but important problem:
agents can propose actions quickly, but external systems still need a clear
boundary before those actions become real impact. The first public product in
that direction is GitHub Gateway.

GitHub Gateway is a write boundary for coding agents. An agent can inspect a
repository, reason about a change, and submit a structured request. The
Gateway decides whether that request may become repository impact. When a
request is admitted, the configured GitHub App creates a reviewable pull
request. When a request is blocked or conflicts with current state, there is no
branch, no commit, and no pull request.

That distinction is the point. The system is not trying to prove that an agent
is correct in every case. It is trying to make write impact explicit, bounded,
and inspectable before it exists in GitHub.

## Why This Exists

Many teams are interested in coding agents, but the usual integration model is
crude. The agent reads the repository and also holds the credential that can
push branches or open pull requests directly. That makes experimentation easy,
but it also collapses two very different jobs into one permission:

- reading repository state
- creating repository impact

Those jobs should not be treated as interchangeable. Reading state is necessary
for any useful coding workflow. Writing to GitHub is different. It creates
review objects, CI load, branch noise, and the possibility of real downstream
effects from stale or malformed requests.

GitHub Gateway exists to separate those steps. The agent can still propose
work, but the write path no longer depends on trusting every agent process with
direct GitHub write credentials.

## What GitHub Gateway Does

GitHub Gateway sits between an agent and repository writes. The agent submits a
structured intent. The Gateway checks whether that request is in scope for the
target repository and branch, whether the requested paths are allowed by policy,
whether the declared source state still matches GitHub, and whether the content
fits the current boundary rules. Only then can the request become a reviewable
pull request.

This produces a very different operational model from "let the agent push and
see what happens." The Gateway can return outcomes such as:

- admitted
- reused
- follow-up completed
- blocked
- conflict
- verification required

Those outcomes matter because they tell the operator whether there was any real
repository impact. A blocked or conflicted request is still useful information,
but it does not create a branch, commit, or pull request in the target
repository.

## How To Read This Section

Start here if you want the product model before the protocol details. These
pages stay at the level of operating model, evaluation story, and boundary
claims. They explain why proposal and impact are separated, why the GitHub App
private key belongs to the Gateway rather than the agent, what the self-hosted
self-hosted demonstrates on a real repository, and what the product deliberately
does not claim.

The technical setup, JSON schema, policy file details, and step-by-step
operator flow live in the GitHub Gateway technical documentation under
[../githubrepo/index.md](../githubrepo/index.md). That is the right place to go
once the product model makes sense and you want exact setup or protocol detail.

## The Core Distinctions

GitHub Gateway is not presented here as a generic AI slogan. It has a narrow,
specific job: controlling agentic write impact on GitHub repositories.

The most important design choice is credential separation. The agent does not
need GitHub write access. It may hold a Runner Key for Gateway submission and,
when needed, a read-only GitHub token for repository state. The GitHub App
private key belongs to the Gateway write identity, not to the agent.

The product also draws a hard line between impact control and correctness
claims. Admission does not mean semantic correctness. The Gateway does not
review code quality, replace CI, or replace human review. It places an explicit
decision boundary before repository writes are materialized.

## What Self-hosted GitHub Gateway v1.3 Demonstrates

Self-hosted GitHub Gateway v1.3 is the current serious evaluation path. It runs
locally, uses Docker, keeps its local state and credentials under operator
control, and demonstrates the core repository outcomes on a test repository.

Self-hosted GitHub Gateway v1.3 is useful because it turns the product claim into something
inspectable. You can see a blocked path produce no pull request. You can see an
allowed config change create a reviewable pull request. You can see equivalent
requests reuse an existing Gateway-created pull request. You can see a
validated follow-up update the same pull request. And you can see stale state
stop a request before write impact.

That is a stronger product story than abstract language about governance or
safety. It is concrete, observable behavior tied to repository impact.

## What This Product Does Not Claim

Impact Boundary Labs is deliberately not making broad promises here.

GitHub Gateway does not claim to make agents safe in every sense. It does not
claim to prevent every malicious action. It does not claim to prove that an
agent understood the code it touched. It does not claim to replace code review,
CI, branch protection, or broader security review.

The boundary is narrower and more defensible than that. It controls how a
structured repository write request may become GitHub impact. That is already a
meaningful improvement over giving every agent direct write power, but it is
not a universal security layer.

## Where To Go Next

If you are new to the product, continue with:

- [Why boundaries matter](02-positioning.md)
- [How GitHub Gateway works](03-how-it-works.md)
- [GitHub Gateway](04-github-gateway-page.md)
- [Self-hosted GitHub Gateway](05-self-hosted-page.md)

If you want the technical setup and protocol reference, continue with:

- [GitHub Gateway technical docs](../githubrepo/index.md)
- [Quickstart](../githubrepo/02-quickstart.md)
- [Security model](../githubrepo/12-security-model.md)
- [Policy YAML](../githubrepo/07-policy-yaml.md)
