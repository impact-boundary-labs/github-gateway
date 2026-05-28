# Guard Result And PR Body

Gateway-created pull requests include a compact **Guard Result**.

The PR body is intentionally not a full audit log. It gives reviewers the
minimum public context needed to understand the Gateway decision and then points
them back to normal GitHub review, CI, and operator judgment.

## What The PR Body Contains

A Gateway-created PR body may include:

- product/version heading
- compact Guard Result table
- decision
- request status
- applies-to commit
- warning or review note
- optional Agent Message

Example shape:

```text
Guarded by GitHub Gateway

Gateway Guard Result
- Decision: Admitted
- Request status: admitted
- Applies to commit: BRANCH_HEAD_SHA

Warning
This records a Gateway admission for the commit shown above. Review the current
diff and GitHub checks before merging.

Agent Message
Context:
...
```

## What The PR Body Intentionally Excludes

The PR body must not publish:

- full intent JSON
- full payloads
- base64 content
- GitHub tokens
- Runner Keys
- headers
- PEM files or private keys
- full diffs
- complete policy dumps
- internal database state
- raw responses
- private local paths

This keeps the PR body reviewable and reduces the chance that sensitive request
material is copied into GitHub comments.

## Agent Message

The human-readable explanation should come from `agent_message`.

Recommended structure:

```text
Context:
Why the change is needed.

Proposed changes:
- High-level bullets.

Validation:
What state was read and what checks were run.

Safety note:
No known sensitive areas.
```

`agent_message` is PR-public when admitted. It is bounded and sanitized. Treat
it as review context, not proof of correctness.

Do not include:

- secrets
- tokens
- private keys
- `.env` values
- full payloads
- full JSON intents
- huge diffs
- private local paths

## Good Agent Message Example

```text
Context:
This change supports the GitHub Gateway story demo for a config-only update.

Proposed changes:
- Create config/live-demo-pass.yaml.
- Keep the change inside the test policy allowed path.

Validation:
- Branch head was read before submit.
- The target file was treated as absent.

Safety note:
No auth, migration, workflow, or secret-handling changes.
```

## Bad Agent Message Examples

Do not include:

```text
Here is the full request JSON: ...
```

Do not include:

```text
Here is my GitHub token: <github-read-token>
```

Do not include:

```text
Here is the complete diff for every file: ...
```

## What Reviewers Should Do

Reviewers should:

1. Read the Guard Result.
2. Read the Agent Message as context only.
3. Review the GitHub diff.
4. Check CI and branch protection.
5. Confirm the change is semantically correct.
6. Merge only through normal repository review process.

## What Guard Result Does Not Prove

Guard Result does not prove:

- semantic correctness
- business correctness
- runtime behavior
- security of the final code
- future PR state
- that CI will pass

It records that the Gateway admitted the intent under its configured checks for
the commit shown.
