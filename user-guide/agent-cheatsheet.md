# Agent Cheatsheet

Short agent-facing summary for the **GitHub Gateway Self-hosted preview**.

Detailed reference:

```text
docs/public/githubrepo/06-agent-instructions.md
```

## Credentials

Read GitHub with:

```text
GITHUB_READ_TOKEN
```

Submit intents to the Gateway with:

```text
INTENT_GATEWAY_API_KEY
```

Target the configured preview repository with:

```text
TEST_REPO
TEST_BRANCH
```

The agent must have **no direct GitHub write access**.

If available, read local runtime values from:

```text
data/agents.env
```

Do not commit or share that file. It may contain a plaintext Runner Key.

## Do Not

- do not `git push`
- do not create pull requests directly
- do not use GitHub write APIs
- do not use the GitHub App private key
- do not treat the Runner Key as a GitHub token

## Do

- read repository state from GitHub
- submit `write` for one file
- submit `write_set` for grouped multi-file changes
- submit follow-up intent only for controlled updates to an existing Gateway PR
- follow `required_next_action`

## Compact Intent Shapes

Single file:

```text
operation=write
path=config/example.yaml
```

Multi-file:

```text
operation=write_set
changes[]=...
```

Follow-up:

```text
operation=update_gateway_pr_write_set
```

## Typical Outcomes

- `Admitted`: review the pull request
- `Blocked`: fix the request or policy issue first
- `Conflict`: re-read GitHub state and rebuild the intent
- `Follow-up`: continue on the same Gateway pull request when allowed

## Reminder

The Gateway controls repository impact. It does not replace human review.
