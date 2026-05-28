# Runner Key

A Runner Key is the agent-to-Gateway submit credential.

It is not a GitHub token. It cannot push, create branches, create commits, or
open pull requests directly. It only lets an agent submit structured intents to
this Gateway. The Gateway still decides admit, reuse, block, conflict, or error.

## Why Runner Keys Exist

Without a Runner Key, the agent would need direct GitHub write credentials or
the Gateway would have no scoped way to accept agent submissions.

With a Runner Key:

- the agent can submit intents to the Gateway
- the key is scoped to a repository and branch/base scope
- Gateway policy still applies
- GitHub review still applies
- GitHub writes still happen only through the configured GitHub App after
  admission

The Runner Key does not replace GitHub review and does not prove correctness.

## Scope

A Runner Key is scoped to:

```text
repository: OWNER/REPO
branch/base scope: TARGET_BRANCH
label: optional human-readable label
```

The scope should match the repository where the GitHub App is installed and the
branch the agent or demo will target.

If the agent submits a different repository or branch, the Gateway should reject
the request before repository impact.

## Creating A Runner Key

In Self-hosted GitHub Gateway v1.3, create Runner Keys in the dashboard after:

1. GitHub App setup is complete.
2. The GitHub App is installed on the selected test repository.
3. `INTENT_GATEWAY_ALLOWED_REPOS=OWNER/REPO` is configured for the Gateway.
4. The Gateway has been restarted after `.env` changes.

The dashboard shows the plaintext Runner Key once. Copy it immediately or let
the dashboard write it into the local agent environment file.

If you forget to copy the key, create a new Runner Key. The old plaintext value
cannot be recovered from the Gateway state.

## Storing The Runner Key

For local self-hosted setup, use:

```text
data/agents.env
```

Recommended contents:

```dotenv
INTENT_GATEWAY_URL=http://127.0.0.1:18080
INTENT_GATEWAY_API_KEY=<runner-key>
GITHUB_READ_TOKEN=<github-read-token>
TEST_REPO=OWNER/REPO
TEST_BRANCH=TARGET_BRANCH
```

`INTENT_GATEWAY_API_KEY` is the Runner Key. `GITHUB_READ_TOKEN` is separate and
must be read-only.

Do not commit `data/agents.env`. Do not paste Runner Keys into chat, logs,
screenshots, docs, or issues.

If you run the Gateway on a custom host port, `INTENT_GATEWAY_URL` must use that
same port.

## Shell Alternative

Instead of `data/agents.env`, set environment variables in the shell where the
agent or demo starts:

```powershell
$env:INTENT_GATEWAY_URL="http://127.0.0.1:18080"
$env:INTENT_GATEWAY_API_KEY="<runner-key>"
$env:GITHUB_READ_TOKEN="<github-read-token>"
$env:TEST_REPO="OWNER/REPO"
$env:TEST_BRANCH="TARGET_BRANCH"
```

Use the agent tool's own secret or environment configuration if that is the
safer local workflow.

## What A Runner Key Does Not Do

A Runner Key does not:

- read GitHub
- write GitHub directly
- bypass policy
- bypass state checks
- bypass content sanity checks
- create pull requests by itself
- authorize arbitrary repositories
- authorize arbitrary branches

The agent still needs read-only repository state from a GitHub Read Token, local
checkout, or helper tooling to build valid intents.

## Lost Runner Key

If a Runner Key is lost:

1. Create a new Runner Key in the dashboard.
2. Update `data/agents.env` or the agent environment.
3. Stop using the old key.

The old plaintext key is not recoverable from the Gateway.

## Leaked Runner Key

If a Runner Key is leaked:

1. Stop using the leaked key.
2. Remove it from files, screenshots, logs, and chat history where possible.
3. Create a new Runner Key.
4. Update the agent environment.
5. Treat any submissions made with the leaked key as untrusted until reviewed.

The exact revocation mechanism depends on the Self-hosted GitHub Gateway v1.3 build and local state
management. For a local self-hosted deployment, the conservative recovery path is to
create fresh local Gateway state for the demo environment if you cannot remove
or invalidate the leaked key through the dashboard.

Do not delete unrelated repository data or GitHub App credentials just because a
Runner Key was lost.

## Operator Checklist

Before handing a Runner Key to an agent:

- GitHub App is installed only on the test repository.
- Runner Key repo matches `INTENT_GATEWAY_ALLOWED_REPOS`.
- Runner Key branch/base scope matches the demo or agent target branch.
- `data/agents.env` is local-only and uncommitted.
- `GITHUB_READ_TOKEN` is read-only and scoped to the test repo.
- The agent environment cannot `git push`.
