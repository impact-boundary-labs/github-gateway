# Roadmap and Future Direction

This page is for readers who already understand the current product surface and
want to know what may come next. It should be read as a sequence of product
deepening, not as a promise that every possible hosted or multi-system surface
already exists. Impact Boundary Labs is starting with a concrete repository
boundary and expanding from what can be demonstrated honestly.

## What Exists Now

Today, the serious public path is Self-hosted GitHub Gateway. It demonstrates a
working repository write boundary with a local dashboard, a GitHub App write
identity, Runner Keys for agent submission, guarded pull request creation,
equivalent pull request reuse, controlled same-pull-request follow-up, and a
story demo that shows the main outcome model on a test repository.

That is enough to evaluate the core claim: the agent can propose work without
holding direct GitHub write access, and repository impact only appears after
Gateway admission.

## What Comes Next

The next reasonable product steps are not dramatic changes in philosophy. They
are improvements in usability, clarity, and operator experience. Better setup
guidance, stronger review surfaces, clearer docs, smoother install flow,
improved demonstration material, and richer visibility into admitted and
non-admitted outcomes all fit the current direction.

Read-state helpers and related operator tooling may also improve the quality of
agent submissions without weakening the core separation between proposal and
materialization.

Another important near-term category is operator clarity. A boundary product
gets stronger when its decisions are easier to read, easier to explain, and
easier to verify in normal engineering workflows. Better setup flow, better
documentation, better review surfaces, and better visibility into why work was
admitted, reused, blocked, or conflicted all fit that category.

## What Later Could Mean

A later phase may include broader product surfaces such as a hosted GitHub
Gateway, a more developed workflow ledger, multi-agent orchestration around
explicit impact boundaries, or additional adapters beyond GitHub.

Those possibilities should be read as future product directions, not as present
availability. The current public path remains Self-hosted GitHub Gateway v1.3.

That distinction matters because hosted language can easily overstate maturity.
The roadmap should describe future surfaces as possible expansions of the same
boundary model, not as current promises hidden behind soft wording.

## What Stays Constant

Even if the product surface grows, the central idea should remain stable:
agent proposals are not the same thing as external impact. A useful product in
this space should preserve that distinction rather than hiding it behind a more
convenient user interface.

## Where To Go Next

If you want the current product surface instead of future direction, continue
with:

- [GitHub Gateway](04-github-gateway-page.md)
- [Self-hosted GitHub Gateway](05-self-hosted-page.md)
- [Technical docs](../githubrepo/index.md)
