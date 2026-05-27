# GitHub Gateway Self-hosted 1.3

GitHub Gateway Self-hosted 1.3 is the current public preview path for GitHub
Gateway by Impact Boundary Labs.

It runs locally in Docker. The Gateway process owns the GitHub App write
identity, local state, Runner Keys, and dashboard. The agent receives a scoped
Runner Key for submitting intents and uses read-only repository state from
GitHub, a local checkout, or helper tooling.

## What Stays Local

In the self-hosted preview:

- the GitHub App private key stays on the user's machine
- `state.db` stays on the user's machine
- Runner Keys stay on the user's machine
- Gateway logs stay on the user's machine
- the Gateway does not send telemetry
- GitHub API calls go to GitHub through the configured GitHub App

The preview dashboard may link to public docs or feedback channels, but the
Gateway runtime does not collect prompts, repository payloads, tokens, or usage
analytics.

Website analytics, if used on a public marketing site, are separate from
Gateway runtime telemetry and should be documented separately.

## Preview Package Shape

The source-free preview package contains the runtime image and local helper
files:

```text
intent-gateway-preview.tar
docker-compose.yml
.env
README.md
Windows start/stop/log launchers
scripts/
data/
secrets/
docs/
user-guide/
test-repo-template/
examples/self-hosted/
```

The package must not include source directories, `.git`, real `.env` files,
state databases, real PEM files, Runner Keys, GitHub tokens, logs, payloads,
raw responses, or private data.

## GitHub App Setup

Recommended path:

1. Open the dashboard.
2. Choose **Create GitHub App from template**.
3. Complete the GitHub App Manifest Flow.
4. Install the app only on the test repository.

The Manifest Flow stores local app material under:

```text
data/github-app-config.json
data/github-app.pem
```

Manual fallback:

```text
secrets/github-app.pem
```

For manual setup, the container path is:

```text
/secrets/github-app.pem
```

The host path and container path are different. In Docker Compose, `./secrets`
is mounted read-only as `/secrets`. If the PEM is on the host at
`secrets/github-app.pem`, the environment variable inside the container should
use `/secrets/github-app.pem`.

## Agent Credential Split

The agent should not receive GitHub write credentials.

The agent needs:

- a Runner Key for submitting to GitHub Gateway
- read-only repository state access from GitHub, a local checkout, or helper
  tooling

The Gateway validates claimed repository state against GitHub before writing.

## Preview Defaults

Default dashboard URL:

```text
http://localhost:18080/dashboard
```

Default preview allowlist placeholder:

```text
INTENT_GATEWAY_ALLOWED_REPOS=OWNER/REPO
```

The user must replace `OWNER/REPO` with the intended test repository before
running the demo.

## Reset Local App Setup

If a manifest-created GitHub App is deleted or invalid, the dashboard can reset
local GitHub App setup. That action removes only:

```text
data/github-app-config.json
data/github-app.pem
```

It does not remove `state.db`, the pepper file, Runner Keys, read tokens, local
repo files, or repository state.
