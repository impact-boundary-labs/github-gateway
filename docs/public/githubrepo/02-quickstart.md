# Quickstart

This quickstart walks through a first Self-hosted GitHub Gateway v1.3 run from a source-free
ZIP package.

Use a test repository first. The first goal is not to merge code. The first
goal is to see GitHub Gateway admit, block, reuse, and conflict on controlled
repository changes.

## What You Need

- Docker Desktop running
- a GitHub account or organization where you can create or install a GitHub App
- a test repository
- access to create a fine-grained read-only GitHub token for the agent
- Self-hosted GitHub Gateway v1.3 ZIP package

The default local URL is:

```text
http://127.0.0.1:18080/dashboard
```

If you change the host port, use that same port for `INTENT_GATEWAY_URL` in the
agent environment.

Some runtime files and environment variables still use the `intent-gateway` /
`INTENT_GATEWAY_*` prefix for runtime compatibility. The public product name is
GitHub Gateway by Impact Boundary Labs.

## 1. Unzip The Self-hosted Package

Unzip the self-hosted package into a local folder.

The extracted folder should contain files and folders similar to:

```text
github-gateway-self-hosted.tar
docker-compose.yml
.env
README.md
start helper
stop helper
log helper
scripts/
docs/
user-guide/
examples/
data/
secrets/
test-repo-template/
```

The `data/` folder is local runtime state. The `secrets/` folder is for manual
GitHub App private key fallback. Do not commit either folder.

## 2. Configure The Target Repository

Set the repository allowlist in the Self-hosted GitHub Gateway v1.3 `.env` file:

```dotenv
INTENT_GATEWAY_ALLOWED_REPOS=OWNER/REPO
```

Use the repository where you will install the GitHub App and run the story demo.

Do not put `INTENT_GATEWAY_ALLOWED_REPOS` in `data/agents.env`. That setting
belongs to the Gateway process, not the agent.

If the self-hosted package still contains `OWNER/REPO`, the demo should stop before
submitting changes.

## 3. Start The Gateway

On Windows, use the start helper included in the self-hosted folder.

Or run from the extracted self-hosted folder:

```powershell
docker load -i .\github-gateway-self-hosted.tar
docker compose --env-file .env -f docker-compose.yml up -d
```

The launcher should load the bundled image tar before starting Compose. That
prevents a stale local image with the same tag from being used by mistake.

Open:

```text
http://127.0.0.1:18080/dashboard
```

Useful health endpoints:

```text
http://127.0.0.1:18080/livez
http://127.0.0.1:18080/healthz
```

`/livez` checks that the HTTP server is alive. `/healthz` may report not ready
until GitHub App setup is complete.

## 4. Create Or Configure The GitHub App

The GitHub App is the Gateway write identity.

The agent never receives the GitHub App private key. The Gateway uses that key
only after an intent is admitted.

Follow the dashboard Step 1 or the full [GitHub App setup](04-github-app-setup.md)
guide.

At the end of this step:

- the Gateway has a GitHub App ID
- the Gateway has a private key locally
- the private key was not given to the agent
- the dashboard shows GitHub App ID and private key configured

If status looks stale after setup, use **Refresh now**.

## 5. Install The App On The Test Repository

Install the GitHub App only on the selected test repository.

Choose:

```text
Only selected repositories
```

Then select:

```text
OWNER/REPO
```

Do not install GitHub App on all repositories for the first run.

After saving in GitHub, wait briefly and use **Refresh now** in the dashboard.
Repository installation checks can take a moment after GitHub changes.

## 6. Create A Runner Key

Create a Runner Key in the dashboard for:

```text
Repository: OWNER/REPO
Branch/base scope: TARGET_BRANCH
```

The Runner Key:

- is not a GitHub token
- lets the agent submit intents to this local Gateway
- is scoped to repository and branch/base scope
- does not bypass policy
- is shown only once

The dashboard can write or update:

```text
data/agents.env
```

The file should contain placeholders or values like:

```dotenv
INTENT_GATEWAY_URL=http://127.0.0.1:18080
INTENT_GATEWAY_API_KEY=<runner-key>
GITHUB_READ_TOKEN=<github-read-token>
TEST_REPO=OWNER/REPO
TEST_BRANCH=TARGET_BRANCH
```

Do not commit or share `data/agents.env`.

## 7. Create A GitHub Read Token

The agent needs read-only repository state. It does not need GitHub write
access.

Create a fine-grained personal access token:

- repository access: only selected repositories
- repository: `OWNER/REPO`
- Contents: read-only
- Pull requests: read-only
- Metadata: read-only

Paste it into `data/agents.env` as:

```dotenv
GITHUB_READ_TOKEN=<github-read-token>
```

Do not paste the GitHub Read Token into the dashboard. The Gateway does not need
this token.

## 8. Check Agent Write Isolation

Open PowerShell in a local clone of the test repository and run:

```powershell
git -c credential.helper= push --dry-run origin HEAD:refs/heads/igw-readonly-push-test
```

Expected result:

```text
The push must fail.
```

If the push succeeds, the agent environment still has ambient GitHub write
credentials. That write access does not come from the Runner Key. Remove stored
write credentials before using the environment as an isolated agent demo.

## 9. Use The Test Repo Template

Self-hosted GitHub Gateway v1.3 includes a test repo template under:

```text
test-repo-template/
```

Use it to prepare a repository with:

- `main` branch
- `.github/intent-gateway.yaml` policy file
- allowed direct files under `config/`
- blocked paths under `security/`
- blocked later Gateway/agent writes under `.github/`

The policy file is created by the human owner initially. Later Gateway/agent
writes to `.github/*` should be blocked by policy.

## 10. Run The Story Demo

From the extracted self-hosted folder:

```powershell
python examples/self-hosted/github-gateway-story-demo.py
```

The demo loads `data/agents.env` if required variables are not already set in
the shell.

Expected story:

1. Bad intent against `security/*` is blocked.
2. Good intent against `config/*` creates a reviewable PR.
3. Equivalent intent reuses the existing Gateway PR.
4. Follow-up updates the same Gateway PR.
5. Stale parent head is rejected as a conflict.

After the demo, open the dashboard and check the Activity log. It should show
sanitized Gateway decisions such as Blocked, Admitted, Reused, follow-up
completed, and Conflict.

## Common First-Run Failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| Dashboard does not open | Docker is not running or port is occupied. | Start Docker Desktop or change the host port. |
| `/livez` works but `/healthz` fails | Gateway is alive but setup is incomplete. | Continue GitHub App and repository setup. |
| GitHub App ID not configured | App setup did not complete. | Create/configure the GitHub App and refresh. |
| Repository installation not found | App not installed on `OWNER/REPO` or allowlist mismatch. | Install only on selected repo and set `INTENT_GATEWAY_ALLOWED_REPOS=OWNER/REPO`. |
| Runner Key missing | No local Runner Key exists. | Create one in the dashboard. |
| GitHub Read Token returns 401/403/404 | Token missing, wrong owner, wrong repo, or insufficient permissions. | Regenerate a fine-grained read-only token scoped to the test repo. |
| Demo blocks with repo allowlist | `TEST_REPO` does not match `INTENT_GATEWAY_ALLOWED_REPOS`. | Fix `.env`, restart Gateway, and update `data/agents.env`. |
| No PR created | Intent was blocked or conflicted. | Check the dashboard Activity log and follow `required_next_action`. |

## Stop The Gateway

Use the stop helper included in the self-hosted folder.

Or:

```powershell
docker compose --env-file .env -f docker-compose.yml down
```

Stopping the Gateway should not delete `data/` or `secrets/`.
