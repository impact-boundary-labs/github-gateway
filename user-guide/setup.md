# Setup

This is the short path for the **Self-hosted GitHub Gateway v1.3**.

Detailed reference:

- `docs/public/githubrepo/04-github-app-setup.md`
- `docs/public/githubrepo/02-quickstart.md`

## 1. Unzip The Self-hosted Package

Extract the self-hosted ZIP into a normal local folder.

You should see at least:

```text
docker-compose.yml
.env
Start GitHub Gateway.cmd
scripts/
docs/
user-guide/
test-repo-template/
```

## 2. Start The Gateway

### Windows

Double-click:

```text
Start GitHub Gateway.cmd
```

### macOS/Linux

From the extracted folder, run:

```sh
chmod +x scripts/*.sh
./scripts/start-gateway.sh
```

The ZIP is built on Windows, so macOS/Linux may need `chmod +x` after
extraction. Current bundled image is `linux/amd64`. Docker Desktop on Apple
Silicon may run it via emulation. Native arm64 image is future packaging work
unless multi-arch is implemented later.

### Manual fallback

```sh
docker load -i github-gateway-self-hosted.tar
docker compose --env-file .env -f docker-compose.yml up -d
```

Then open:

```text
http://127.0.0.1:18080/dashboard
```

The first visit opens **Getting started** in light mode by default.

Useful health endpoints:

```text
/livez
/healthz
```

`/livez` means the server process is alive. `/healthz` is readiness. Before
GitHub App setup is complete, `/healthz` may report unhealthy. This is expected.

Stop without deleting local state:

- Windows: `Stop GitHub Gateway.cmd`
- macOS/Linux: `./scripts/stop-gateway.sh`

Show logs:

- Windows: `Show GitHub Gateway Logs.cmd`
- macOS/Linux: `./scripts/show-logs.sh`

Some runtime files and environment variables still use the `intent-gateway` /
`INTENT_GATEWAY_*` prefix for runtime compatibility. The public product name is
GitHub Gateway by Impact Boundary Labs.

Before you run the demo, open `.env` in the extracted self-hosted folder
and set:

```dotenv
INTENT_GATEWAY_ALLOWED_REPOS=owner/repo
```

This setting belongs in `.env`, not in `data/agents.env`.

## 3. Create The GitHub App

In the dashboard, choose:

```text
Create GitHub App from template
```

The account target defaults to **Personal account**. Switch to
**Organization** only if you want the app created under an org. For the bundled
demo, choose **Organization** and use `impact-boundary-labs`.

What this credential is for:

- **GitHub App private key**: Gateway write identity.

The Gateway uses this identity to create branches and reviewable pull requests.
The agent must not receive it.

## 4. Install The App On The Test Repository

After GitHub creates the app:

1. open the installation page
2. choose **Only selected repositories**
3. select only your test repository
4. save the installation
5. use **Refresh now** in the dashboard

GitHub App authentication and repository installation checks may take a moment
after changes on GitHub. Use **Refresh now** after install or permission
changes.

## 5. Create A Runner Key

Create a Runner Key in the dashboard for the repository and branch/base scope
you want to use.

What this credential is for:

- **Runner Key**: agent-to-Gateway submit credential.

It is not a GitHub token. It authorizes intent submission to this Gateway. The
Gateway still decides admit, block, or conflict.

Store the Runner Key when the dashboard shows it. The one-time result is not
shown again on normal reload. Save it in `data/agents.env` or set it in the
shell where the agent starts.

## 6. Create A GitHub Read Token

Create a fine-grained token for the agent:

1. GitHub Settings
2. Developer settings
3. Personal access tokens
4. Fine-grained tokens
5. Generate new token

Use:

- Resource owner: your account or organization
- Repository access: **Only selected repositories**
- Repository: your test repository
- Permissions:
  - Contents: read-only
  - Pull requests: read-only
  - Metadata: read-only

What this credential is for:

- **GitHub Read Token**: agent-to-GitHub read-only credential.

The agent uses it to read branch head, file state, and follow-up PR state. The
Gateway does not need this token.

The dashboard can write or update `data/agents.env` after Runner Key creation.
That file is local runtime state. It may contain a plaintext Runner Key. Do not
share or commit it.

The self-hosted package already includes a placeholder `data/agents.env` file. The
dashboard can fill in the Runner Key and repo values there after creation.

## 7. Run The Demo

Once the GitHub App, Runner Key, and GitHub Read Token are ready, continue with:

- `user-guide/run-demo.md`

Before that, read:

- `user-guide/security-model.md`

That is the shortest explanation of why these three credentials are kept
separate.

## 8. Functional Test vs Isolation Proof

The story demo is the functional test. It checks Gateway decisions such as
Blocked, Admitted, Reused, Follow-up, and Conflict.

The isolation proof is separate. It checks that the agent environment has no
ambient GitHub write credentials. The Gateway cannot remove unrelated
credentials from your machine. For the isolation proof, run the agent environment
without ambient GitHub write credentials.

If you do not have a local clone of the test repository, skip the
push-isolation check. That is not a demo failure; it only means the isolation
proof was not performed from that environment.
