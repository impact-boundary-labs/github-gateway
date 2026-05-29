# Security Model

This file explains the security model of **Self-hosted GitHub Gateway v1.3** in plain language.

Detailed reference:

- `docs/public/githubrepo/06-agent-instructions.md`
- `docs/public/githubrepo/04-github-app-setup.md`
- `docs/public/githubrepo/02-quickstart.md`
- `docs/public/githubrepo/07-policy-yaml.md`

## A. The Problem

### Without the Gateway

If the agent holds GitHub write credentials directly:

- the agent may hold GitHub write credentials
- the agent can push branches
- the agent can create pull requests directly
- path policy is only a convention
- stale file state can turn into real repository changes
- mistakes can become GitHub impact immediately

### With the Gateway

With the Gateway in front:

- the agent submits structured intent
- the Gateway validates policy, state, and content
- only admitted intents become a **reviewable pull request**
- blocked or conflicted intents create no repository impact

That is the core boundary.

## B. The Three Credentials

### GitHub App private key

- Used by the Gateway.
- Lets the Gateway create branches and pull requests.
- Stored locally in the self-hosted data or secrets path.
- Never give this to the agent.
- If the agent has this, the boundary is broken.

### Runner Key

- Used by the agent to submit intents to this Gateway.
- It is not a GitHub token.
- It cannot write to GitHub directly.
- It only authorizes intent submission to the local Gateway.
- The Gateway still decides admit, block, or conflict.

### GitHub Read Token

- Used by the agent to read repository state from GitHub.
- Should be fine-grained and read-only.
- Scope it only to the test repository.
- Recommended permissions:
  - Contents: read-only
  - Pull requests: read-only
  - Metadata: read-only
- It must not have write permissions.

## C. Why The Agent Needs A Read Token

The agent is expected to read real GitHub state before it submits an intent.

That includes:

- current branch head
- file existence or absence
- Git blob SHA for existing files
- parent PR head for follow-up requests

The Gateway then checks those declared states before impact.

The **GitHub Read Token** lets the agent prepare accurate intents without
giving it write power.

## D. Why The Runner Key Exists

The **Runner Key** is the agent's credential to the Gateway.

It lets the Gateway know which repository and branch/base scope the agent may
submit for.

It does not:

- bypass policy
- replace GitHub review
- create GitHub impact by itself

It is a submit credential, not a write credential.

## E. Why The GitHub App Private Key Exists

GitHub requires an identity that can create branches and pull requests.

The Gateway owns that identity through the GitHub App private key.

That keeps write power inside the Gateway boundary:

- the agent proposes
- the Gateway checks
- the Gateway creates impact only when intent is admitted

The agent never receives this credential.

## F. Ambient Write Credentials Warning

Important warning:

> If git push works from the agent environment, the demo is not isolated.

The agent environment must not have:

- GitHub write token
- GitHub App private key
- SSH key with write access
- Git Credential Manager write access
- `gh auth` with write access
- classic PAT with repo write scope

Check with:

```bash
git -c credential.helper= push --dry-run origin HEAD:refs/heads/igw-readonly-push-test
```

Expected:

```text
The push must fail.
```

On Windows, a normal `git push` can still work because Git Credential Manager
may have cached write credentials. That does not come from the Runner Key.

For a clean Gateway demo, run the agent in an environment without ambient
GitHub write credentials.

The Gateway cannot remove unrelated credentials from your machine. For the
isolation proof, run the agent environment without ambient GitHub write
credentials.

If no local clone of the test repository exists, skip the push-isolation check.
That does not make the story demo fail; it means this specific isolation proof
was not performed.

## G. Functional Test vs Isolation Proof

The functional test checks whether GitHub Gateway handles the controlled story
demo outcomes:

- Blocked
- Admitted
- Reused
- Follow-up
- Conflict

This can run even when the human operator's normal shell still has GitHub write
access, because the demo submits intents to the Gateway.

The isolation proof checks whether the agent environment lacks ambient GitHub
write credentials. The expected result is that read-only GitHub access works,
but direct write attempts fail.

## H. What The Gateway Blocks

The Gateway can block things such as:

- writes to blocked paths such as `security/*`
- writes to `.github/*`
- writes based on stale `read_blob_sha`
- follow-ups against stale parent PR head
- payloads that fail implemented content sanity checks, such as executable
  headers, binary/non-UTF-8 content in guarded modes, or invalid YAML/JSON for
  those file types
- requests outside the Runner Key repo/branch scope
- invalid or malformed intents

Content sanity is not semantic analysis and not a secret scanner. Keep secrets
out of allowed paths through policy, agent instructions, review, and normal
secret-handling controls.

## I. What The Gateway Does Not Prove

- It does not prove semantic correctness.
- It does not review code quality.
- It does not auto-merge.
- It does not replace human review.
- It does not prove the agent "understood" the file.
- It controls repository impact, not truth.
- Admitted means reviewable pull request, not safe to merge.

## J. Expected Outcomes

### Admitted

A reviewable pull request is created or updated.

### Reused

An existing equivalent Gateway pull request is reused instead of duplicating
impact.

### Follow-up

A validated follow-up updates the same Gateway pull request.

### Blocked

No branch, commit, or pull request is created.

### Conflict

The agent must re-read current state and resubmit.

### Verification required

The Gateway could not safely verify final state. Operator attention is required.
