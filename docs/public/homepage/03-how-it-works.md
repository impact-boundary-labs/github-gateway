# How GitHub Gateway Works

GitHub Gateway works by separating a proposed change from the right to
materialize that change in GitHub. The distinction is simple, but it changes
the shape of the whole workflow.

An agent can inspect repository state, decide what it wants to do, and build a
structured intent. That intent does not create repository impact by itself. It
is a proposal submitted to the Gateway. The Gateway decides whether the request
may become a branch and a reviewable pull request through the configured GitHub
App.

The result is a workflow where the agent can move quickly, but the write path
is explicit instead of ambient.

## Start With the Core Sequence

The public model is:

```text
Read state -> build intent -> admit or reject -> materialize reviewable impact
```

The agent reads repository state directly. It may use a local checkout, a
read-only GitHub token, or helper tooling that provides current state. It then
submits a structured intent that describes what it wants to change and what
state it believes it read.

GitHub Gateway evaluates that request. If the request fits the current
repository scope, policy, and state requirements, the configured GitHub App
creates the pull request impact. If not, the request is blocked or conflicted
before repository impact exists.

## Step 1: The Agent Reads State

GitHub Gateway is not a replacement for repository visibility. The agent still
needs to read the repository well enough to prepare a correct request. It may
need to know whether a file already exists, what the current branch head is,
what the current blob SHA is for a file, or what the current parent pull
request head is before preparing a follow-up.

That matters because the Gateway is not accepting blind write requests. The
agent is expected to declare the state it relied on, and the Gateway checks
that declaration before writing.

This is one of the practical reasons the public docs separate a GitHub Read
Token from the Runner Key. The read path and the write path are different jobs.

## Step 2: The Agent Builds a Structured Intent

The agent does not send "please push this branch" as an informal command. It
sends a structured request. That request includes the target repository, the
target branch or parent pull request context, the relevant source-state facts,
and the requested file content.

The homepage docs do not need the full protocol schema, but the public point is
important: GitHub Gateway operates on declared intent, not on hidden side
effects from a local Git process.

That is why the technical docs emphasize structured intent types such as
single-file write, grouped write set, and controlled follow-up on a
Gateway-created pull request. The protocol gives the boundary something
deterministic to inspect before a GitHub write exists.

## Step 3: The Agent Submits With a Runner Key

The Runner Key is the agent-to-Gateway credential. It is not a GitHub token and
it cannot push to GitHub by itself. Its job is narrower: it authorizes the
agent to submit structured intents to a particular Gateway setup for a given
repository and branch or base-branch scope.

That difference is central to the product model. If the agent only holds a
Runner Key and read-only state access, the write identity still lives behind
the Gateway. If the agent also has a broad GitHub write token, the demonstration
is no longer isolated, because the agent could bypass the boundary entirely.

## Step 4: The Gateway Evaluates the Request

The Gateway checks whether the request is admissible before any GitHub write
happens. At a high level, those checks answer a small set of practical
questions.

Is the target repository in scope for this Gateway setup?

Is the branch or base branch in scope for the Runner Key that submitted the
request?

Does the repository policy allow the requested path?

Does the declared source state still match GitHub, or did the agent build its
request on stale information?

Does the content fit the current sanity checks and boundary rules?

The goal is not to prove that the resulting code is good. The goal is to decide
whether this request is allowed to become repository impact at all.

## Step 5: Admitted Work Becomes Reviewable Impact

If the request passes those checks, the configured GitHub App performs the
write. In Self-hosted GitHub Gateway v1.3, that means the Gateway creates or updates a
reviewable pull request.

This is where the credential split becomes visible. The agent did not need a
GitHub write token to get a pull request. The Gateway owned the GitHub App
write identity and used it only after the admission decision was made.

For a reviewer, this is a better object to inspect than an agent-created branch
that appeared through direct push. The pull request can carry a compact Guard
Result, it can include an Agent Message for context, and it can be tied to a
specific Gateway decision flow rather than to a background Git process that had
direct write power.

## Step 6: Non-Admitted Work Stops Before GitHub Impact

The most important outcome is often the one that does not materialize.

If the request is out of scope, the path is blocked, the source state is stale,
the parent pull request head changed, or the request otherwise fails the
boundary checks, the system stops before branch creation and pull request
creation.

That changes the meaning of failure. A blocked or conflicted request is not a
cleanup problem in GitHub. It is a visible decision in the Gateway Activity
feed with no repository impact.

For many teams, that is the practical reason to evaluate a boundary at all.

## The Outcome Model

The public demo makes the outcome model clear:

- bad intent: no pull request
- good intent: reviewable pull request
- same effect: existing Gateway-created pull request reused
- follow-up: same pull request updated
- stale state: blocked before write

These outcomes are deliberately easier to inspect than abstract policy claims.
You can see whether impact happened. You can see whether the same pull request
was reused. You can see whether a follow-up was allowed. And you can see when a
request was stopped before write.

## Why Reuse and Follow-up Matter

Without reuse, repeated agent requests can create duplicate pull requests for
the same effect. Without controlled follow-up, the next iteration of an allowed
change may drift into ad hoc branch management.

GitHub Gateway treats those as first-class boundary concerns. Equivalent work
can reuse an existing Gateway-created pull request. A validated follow-up can
update the same Gateway-created pull request when the parent head and file
state still match the declared conditions.

This keeps reviewable impact more compact and more legible. Instead of creating
new GitHub objects for every retry or refinement, the system can either reuse a
matching review object or stop the request because the required state changed.

## What Reviewers Still Need to Do

Admission is not approval. An admitted request became reviewable impact because
it passed the boundary checks, not because the Gateway proved the code is
correct.

Reviewers still need to inspect the pull request. CI still matters. Repository
rules still matter. Human review still matters.

That honest limitation is part of how the product should be understood. GitHub
Gateway narrows the write path and makes it inspectable. It does not replace
engineering judgment.

## Where To Go Next

If you want the technical detail behind this flow, continue with:

- [GitHub Gateway technical overview](../githubrepo/01-overview.md)
- [Intent JSON reference](../githubrepo/08-intent-json-reference.md)
- [Guard Result and PR body](../githubrepo/11-guard-result.md)
- [Security model](../githubrepo/12-security-model.md)
