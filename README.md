# GitHub Gateway Self-hosted 1.3 Preview

This folder is the source-free preview package layout for the first self-hosted
preview of the **GitHub Gateway** reference adapter.

The broader product idea is the **Impact Boundary Core**:

```text
Intent -> Admission -> Impact
```

Agents may read repository state and propose changes. Repository impact goes
through the Gateway. Use this `preview/` folder for user distribution. The
repository-root Compose files are for development or source-build workflows.

No secrets are included in the ZIP.

## Start Here

Quick path:

- `user-guide/start-here.md`
- `user-guide/setup.md`
- `user-guide/security-model.md`
- `user-guide/run-demo.md`
- `user-guide/troubleshooting.md`
- `user-guide/agent-cheatsheet.md`

Detailed reference:

- `docs/public/index.md`
- `docs/public/githubrepo/01-overview.md`
- `docs/public/githubrepo/02-quickstart.md`
- `docs/public/githubrepo/03-self-hosted-preview.md`
- `docs/public/githubrepo/04-github-app-setup.md`
- `docs/public/githubrepo/06-agent-instructions.md`
- `docs/public/githubrepo/12-security-model.md`

## Preview Docs

- Public docs index: `docs/public/index.md`
- Public homepage docs: `docs/public/homepage/`
- Public GitHub Gateway docs: `docs/public/githubrepo/`
- Public GitHub App setup: `docs/public/githubrepo/04-github-app-setup.md`
- Public agent instructions: `docs/public/githubrepo/06-agent-instructions.md`
- Public policy reference: `docs/public/githubrepo/07-policy-yaml.md`
- Public limitations: `docs/public/githubrepo/13-limitations.md`
- Test repository template: `test-repo-template/`
- Test repository policy explanation:
  `test-repo-template/docs/policy-explained.md`

## Start On Windows

1. Install and start Docker Desktop.
2. Unzip the preview folder.
3. Double-click:

```text
Start Intent Gateway.cmd
```

The launcher loads the bundled `intent-gateway-preview.tar` when it is present,
starts Docker Compose, and opens:

```text
http://localhost:18080/dashboard
```

The first dashboard visit opens **Getting started** in light mode by default.
If you later switch theme, the dashboard keeps that browser preference locally.

Some runtime files and environment variables still use the `intent-gateway` /
`INTENT_GATEWAY_*` prefix for preview compatibility. The public product name is
GitHub Gateway by Impact Boundary Labs.

Before you run the demo, edit `.env` in the extracted preview folder
and set:

```dotenv
INTENT_GATEWAY_ALLOWED_REPOS=owner/repo
```

That allowlist belongs in `.env`, not in `data/agents.env`.

Recommended GitHub App setup is inside the dashboard: choose **Create GitHub App
from template**. The account target defaults to **Personal account**. Switch to
**Organization** only when you want the app created under an org such as the
bundled `impact-boundary-labs` demo. The manifest flow stores the created app
metadata and private key locally under:

```text
data/github-app-config.json
data/github-app.pem
```

If that local manifest-created app is deleted or those files become invalid,
use **Reset local GitHub App setup** in the dashboard. It removes only
`data/github-app-config.json` and `data/github-app.pem`. It does not remove
Runner Keys, `state.db`, the pepper file, or repository data. A complete manual
`GITHUB_APP_ID` + `GITHUB_APP_PRIVATE_KEY_PATH` fallback remains available.

Manual setup remains available. The `secrets/` folder is intentionally empty in
the preview ZIP unless you use this fallback. If you already have a GitHub App,
put the PEM at:

```text
secrets/github-app.pem
```

Then add these manual fallback values to `.env`:

```dotenv
GITHUB_APP_ID=<your-github-app-id>
GITHUB_APP_PRIVATE_KEY_PATH=/secrets/github-app.pem
```

## Manual Start

Load the preview image:

```powershell
docker load -i intent-gateway-preview.tar
```

Start the Gateway:

```powershell
docker compose --env-file .env -f docker-compose.yml up -d
```

Open the local dashboard:

```text
http://localhost:18080/dashboard
```

After creating a Runner Key, give the agent the public preview instructions from
`docs/public/githubrepo/06-agent-instructions.md`. The agent needs the
Gateway URL, Runner Key, and a repository-scoped GitHub read token. Do not give
the agent the GitHub App private key.

Create the GitHub Read Token as a fine-grained personal access token:

- GitHub Settings -> Developer settings -> Personal access tokens -> Fine-grained tokens -> Generate new token
- Resource owner: your owner/org
- Repository access: Only selected repositories
- Repository: `OWNER/REPO`
- Permissions: Contents read-only, Pull requests read-only, Metadata read-only

The Gateway does not need this read token. Do not paste it into the dashboard.
The agent should not have GitHub write credentials. If `git push` works from the
agent environment, the demo is not isolated.

The dashboard can write or update `data/agents.env` after Runner Key creation.
That file is local runtime state. It may contain a plaintext Runner Key. Do not
share or commit it.

The preview package also includes a placeholder `data/agents.env` so you can
see where the Runner Key, GitHub Read Token, and test repo values belong. If
you change `IGW_HOST_PORT`, the dashboard-generated `INTENT_GATEWAY_URL` uses
that host port when it updates `data/agents.env`.

Agent environment template:

```dotenv
INTENT_GATEWAY_URL=http://127.0.0.1:18080
INTENT_GATEWAY_API_KEY=<created-runner-key>
GITHUB_READ_TOKEN=<paste-fine-grained-read-token-here>
TEST_REPO=OWNER/REPO
TEST_BRANCH=TARGET_BRANCH
```

Provide these values by configuring the agent to read `data/agents.env`, by
setting environment variables before starting the agent, or by using the agent
tool's own secret/env configuration.

The preview ZIP includes the story demo under `examples/self-hosted/`. Run it
from the extracted preview folder after the Gateway, Runner Key, and GitHub Read
Token are ready. If the required variables are not already set in the shell, the
demo first tries to load `data/agents.env`:

```powershell
python examples/self-hosted/github-gateway-story-demo.py
```

Push isolation check:

```bash
git -c credential.helper= push --dry-run origin HEAD:refs/heads/igw-readonly-push-test
```

Expected result: the push must fail.

Before running that check, open PowerShell in a local clone of the target test
repository.

If port `18080` is occupied, edit `.env` for the local test and set:

```dotenv
IGW_HOST_PORT=18081
```

Then start again with the same env file:

```powershell
docker compose --env-file .env -f docker-compose.yml up -d
```

## Local State

In preview mode, the Gateway creates the local pepper on first start and reuses
it on later starts:

```text
data/intent_gateway_pepper
```

If you use the dashboard GitHub App manifest flow, the Gateway also stores:

```text
data/github-app-config.json
data/github-app.pem
```

The Gateway creates and uses SQLite state at:

```text
data/state.db
```

Deleting `data/` resets local Gateway state and invalidates existing Runner
Keys. Do not share or commit files from `data/`, `.env`, GitHub App private
keys, Runner Keys, logs, payloads, or raw responses.

Older preview runs may have created `data/local-secrets.json`. New preview
starts do not need it for Runner Key creation.

## Test Repository Template

Use `test-repo-template/` to create a small GitHub test repository before you
connect a real project. Copy that folder into a new empty repository, commit and
push it as the human owner, then install the GitHub App only on that test
repository. Read `test-repo-template/docs/policy-explained.md` and
`docs/public/githubrepo/07-policy-yaml.md` before changing the preview policy.

The preview test policy uses `mode: guarded`. `fast` and `strict` exist as
advanced modes, but they are not the main preview setup flow.

The template policy lives at `.github/intent-gateway.yaml` and matches the
preview demo paths.

## Demo Policy Paths

Use demo and smoke writes that match the test repository policy. For the preview
policy `config/*`, allowed writes should be direct files under `config/`, for
example:

```text
config/live-demo-pass-20260520T091206Z.yaml
config/gateway-load-test-20260520T091206Z-001.yaml
```

In this preview policy, `config/*` allows direct files under `config/`. It does
not allow nested paths such as `config/demo/file.yaml`. Blocked examples should
stay outside the allowed scope, for example `security/...` or `.github/...`.

## Stop

Double-click:

```text
Stop Intent Gateway.cmd
```

Or run manually:

```powershell
docker compose --env-file .env -f docker-compose.yml down
```

Use the same env file for `down` that you used for `up`.

## Logs

Double-click:

```text
Show Logs.cmd
```

Or run manually:

```powershell
docker compose --env-file .env -f docker-compose.yml logs -f
```
