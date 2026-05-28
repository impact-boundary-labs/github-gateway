# Security Model

GitHub Gateway controls repository impact from coding-agent proposals.

It does not control intelligence, prove correctness, or replace review. Its
security value comes from separating agent proposal from GitHub write impact.

## The Problem

Without a write boundary, an agent with GitHub write credentials can:

- push branches
- create commits
- open pull requests
- update pull requests
- modify workflow files if credentials allow it
- make stale file assumptions become real repository impact

Path policy becomes a convention inside the agent prompt rather than an enforced
boundary.

## The Boundary

With GitHub Gateway:

1. The agent reads repository state.
2. The agent submits structured intent to the Gateway.
3. The Gateway validates scope, policy, declared state, content sanity, and
   materialization checks.
4. Only admitted intents become reviewable pull requests.
5. Blocked or conflicted intents create no branch, no commit, and no pull
   request.

## Credential Split

| Credential | Holder | Capability |
| --- | --- | --- |
| GitHub App private key | Gateway | GitHub write identity after admission. |
| Runner Key | Agent | Submit intents to this Gateway. |
| GitHub Read Token | Agent or runner | Read repository state only. |

### GitHub App private key

The GitHub App private key belongs to the Gateway.

It lets the Gateway create branches and pull requests after admission. It should
be stored locally in the self-hosted data or secrets path, depending on the setup
flow.

Never give this key to the agent. If the agent has the GitHub App private key,
the boundary is broken.

### Runner Key

The Runner Key belongs to the agent for Gateway submit.

It is not a GitHub token. It cannot write to GitHub directly. It only authorizes
intent submission to the Gateway for a scoped repository and branch/base scope.
Gateway policy and state checks still apply.

### GitHub Read Token

The GitHub Read Token belongs to the agent or runner for read-only state.

Recommended permissions:

- Contents: read-only
- Pull requests: read-only
- Metadata: read-only

Scope it only to the test repository. It must not have write permissions.

## Why The Agent Needs Read Access

The agent needs state evidence to build valid intents:

- branch head commit
- file existence
- Git blob SHA for existing files
- parent PR head for follow-ups

That evidence may come from:

- read-only GitHub access
- a local checkout
- helper tooling
- controlled runner state

The Gateway validates claimed state against GitHub before writing.

## Ambient Write Credentials

The agent environment must not have ambient GitHub write access.

Remove or avoid:

- GitHub write token
- GitHub App private key
- SSH key with write access
- Git Credential Manager write credential
- `gh auth` write session
- classic PAT with repository write scope

Check from the agent environment:

```powershell
git -c credential.helper= push --dry-run origin HEAD:refs/heads/ggw-readonly-push-test
```

Expected:

```text
The push must fail.
```

If it succeeds, the demo is not isolated.

## What The Gateway Blocks

Depending on policy and request state, GitHub Gateway can block:

- writes outside Runner Key repository scope
- writes outside Runner Key branch/base scope
- writes to blocked paths such as `security/*`
- writes to `.github/*` after initial human policy setup
- writes based on stale `read_blob_sha`
- follow-ups against stale parent PR head
- payloads that fail implemented content sanity checks, such as executable
  headers, binary/non-UTF-8 content in guarded modes, or invalid YAML/JSON for
  those file types
- malformed intents
- requests outside configured allowlist

Blocked and conflicted requests should create no branch, no commit, and no pull
request.

Content sanity is not a semantic review and not a secret scanner. A
secret-looking string inside an otherwise valid allowed file is not a DLP
guarantee failure by itself; keep secrets out through repository policy, agent
instructions, review, and normal secret-handling controls.

## State Binding

State binding prevents an agent from turning stale assumptions into repository
impact.

For fresh writes:

- `snapshot_hash` binds the intent to the branch head read by the agent.
- `read_blob_sha` binds existing file updates to the file state read by the
  agent.

For follow-ups:

- `expected_parent_head_commit` binds the intent to the current Gateway-created
  PR head.

If these values are stale or unverifiable, the Gateway fails closed before
materializing impact.

## Runtime Data Boundaries

Self-hosted GitHub Gateway v1.3 runs locally.

Local runtime state may include:

- `state.db`
- local pepper file
- Runner Key digests and grants
- dashboard activity metadata
- manifest-created GitHub App config under `data/github-app-config.json` and
  `data/github-app.pem`
- local logs

The self-hosted Gateway runtime does not send telemetry to Impact Boundary Labs.
GitHub API calls still go to GitHub through the configured GitHub App and any
read-only token used by the agent.

Website analytics, if used on a public website, are separate from Gateway
runtime telemetry and should be disclosed separately.

## What The Gateway Does Not Prove

GitHub Gateway does not prove:

- semantic correctness
- business correctness
- code quality
- runtime safety
- that tests pass
- that a change should be merged
- that the agent understood the file

It reduces the need to trust every agent with write credentials. It does not
remove the need to trust and operate the Gateway itself.

## Security Checklist

Before a demo:

- GitHub App installed only on the test repository
- GitHub App private key stored only for the Gateway
- Runner Key stored locally for agent submit
- GitHub Read Token read-only and repo-scoped
- `git push --dry-run` fails from the agent environment
- policy blocks `security/*` and `.github/*`
- dashboard Activity is reviewed after the story demo
