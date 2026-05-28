# Current Scope and Limitations

GitHub Gateway should be understood through its current scope, not through
imagined future claims. The public product today is **Self-hosted GitHub
Gateway v1.3**, a local release that demonstrates a repository write boundary
on GitHub. That is already meaningful, but it is intentionally narrower than a
complete hosted platform story.

## What Is Available Today

The current public path is Self-hosted GitHub Gateway v1.3. It runs locally, uses a
configured GitHub App as the write identity, creates Runner Keys for agent
submission, and demonstrates guarded pull request creation, pull request reuse,
and validated follow-up on Gateway-created pull requests.

That means the product can already be evaluated in terms of real repository
impact. It is not just a mockup or a concept note.

## What It Does Not Claim

GitHub Gateway does not claim to prove semantic correctness. It does not claim
to review code quality, replace CI, replace branch protection, or auto-merge
agent work. It does not claim to prevent every malicious action an agent might
attempt in a broader environment. It does not claim to be a complete hosted
governance platform.

Those limits are not weaknesses in the description. They are part of an honest
public contract. The product claim is about controlling agentic write impact on
GitHub repositories, not about proving that every generated change is good.

## Why the Scope Is Deliberately Narrow

The narrower scope is what makes the product legible. A team can inspect
whether blocked work creates no pull request. It can inspect whether allowed
work becomes a reviewable pull request. It can inspect whether follow-up stays
on the same Gateway-created review object.

Those are tractable, testable questions. Claims such as "the system makes agent
coding safe" are not. GitHub Gateway is more credible when it stays anchored to
the write boundary it actually implements.

## What Kinds of Changes Fit Best

Self-hosted GitHub Gateway v1.3 is best for small, reviewable repository changes. It is well suited
to configuration updates, bounded code edits, and demonstrations where the
resulting pull request is easy for a human reviewer to inspect.

It is not described as the best tool for huge refactors, bulk generated assets,
opaque binary changes, or unconstrained long-running repository automation. The
boundary model is clearest when the requested change is small enough that the
decision and resulting review object remain legible.

## Why Hosted Availability Is Not the Current Story

A hosted GitHub Gateway may become part of the future product direction, but it
is not the public path today. The serious path today is Self-hosted GitHub
Gateway v1.3. That is where teams can actually inspect the boundary, keep the
write identity under their control, and evaluate whether the model fits their
needs.

This matters because vague hosted language can overstate what is currently
available. The honest description is simpler: Self-hosted GitHub Gateway v1.3 is the
current product surface, and any future hosted surface would still need to
preserve the same core separation between agent proposals and external impact.

## The Practical Reading of These Limits

The right way to read the current scope is not "too small to matter." It is
"narrow enough to evaluate honestly." The product is focused on repository
impact, reviewable pull requests, and the credential split between the agent
and the Gateway write identity.

That focus is also what makes the next step clear. If Self-hosted GitHub Gateway v1.3
solves the repository-boundary problem for a team, then broader product surfaces
can be considered later. If it does not, the evaluation still revealed
something concrete rather than hiding behind inflated claims.

## Where To Go Next

For technical detail on the current product surface, continue with:

- [GitHub Gateway technical overview](../githubrepo/01-overview.md)
- [Self-hosted GitHub Gateway v1.3 docs](../githubrepo/03-self-hosted-gateway.md)
- [Limitations in technical detail](../githubrepo/13-limitations.md)
