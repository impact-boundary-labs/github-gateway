# GitHub App Setup

The GitHub App is the Gateway write identity.

The agent does not receive this identity. The agent submits structured intents
with a Runner Key. GitHub Gateway decides whether the intent is admitted. Only
after admission does the Gateway use the configured GitHub App to create or
update reviewable pull requests.

## Credential Ownership

| Credential | Belongs to | Purpose |
| --- | --- | --- |
| GitHub App private key | Gateway | Creates branches and pull requests after admission. |
| Runner Key | Agent | Submits intents to this Gateway. |
| GitHub Read Token | Agent or runner | Reads repository state only. |

Never give the GitHub App private key to the agent. If the agent has the
private key, the write boundary is broken.

## Recommended Preview Flow

For GitHub Gateway Self-hosted 1.3, the recommended setup path starts in the
preview dashboard.

The public setup contract is:

1. Open the dashboard.
2. Choose **Create GitHub App from template**.
3. Let GitHub redirect back to the dashboard.
4. Keep the manifest-created App ID and private key local to the Gateway.
5. Install the app only on the selected test repository.
6. Create a Runner Key for the agent after repository installation is ready.

In the current self-hosted preview, the dashboard manifest flow is the
recommended operator path. Manual setup remains the fallback when you already
have a GitHub App or you want to wire the PEM yourself.

Do not assume the agent needs any part of the GitHub App credential.

When the dashboard manifest flow succeeds, the Gateway stores the local app
material under:

```text
data/github-app-config.json
data/github-app.pem
```

Do not move that PEM into the agent environment. The agent never receives the
GitHub App private key.

## Manual GitHub App Fallback

Use the manual flow only when you are not using the dashboard template flow, or
when you already have a GitHub App you want to reuse.

Open GitHub and create a new GitHub App.

For a personal account:

1. Open GitHub.
2. Go to Settings.
3. Open Developer settings.
4. Open GitHub Apps.
5. Create a new GitHub App.

For an organization:

1. Open the organization.
2. Go to Settings.
3. Open GitHub Apps.
4. Create a new GitHub App for that organization.

Use a clear local-preview name such as:

```text
GitHub Gateway Local Preview
```

Use a local dashboard URL for homepage, callback, or setup fields if your
preview asks for them:

```text
http://localhost:18080/dashboard
```

Do not enable webhooks unless your specific preview package explicitly requires
them.

## Required Repository Permissions

Use the narrowest permissions needed for the preview:

| Permission | Access | Why |
| --- | --- | --- |
| Contents | Read and write | Create branches and commits for admitted intents. |
| Pull requests | Read and write | Create and update reviewable pull requests. |
| Metadata | Read-only | Required by GitHub for repository access. |
| Checks | Read and write if enabled | Publish Gateway evidence check runs when supported. |

Do not request broad organization permissions, repository administration,
actions write access, secrets access, members access, or all-repository access
for the first evaluation.

## Private Key Placement

The private key belongs to the Gateway.

Manual preview setup commonly uses:

```text
secrets/github-app.pem
```

Inside the container, the path is typically:

```text
/secrets/github-app.pem
```

The host path and container path are different. Configure the Gateway with the
container path, not a local Windows or macOS path.

Example environment values:

```dotenv
GITHUB_APP_ID=<github-app-id>
GITHUB_APP_PRIVATE_KEY_PATH=/secrets/github-app.pem
INTENT_GATEWAY_ALLOWED_REPOS=OWNER/REPO
```

Do not paste the PEM into docs, chat, issues, screenshots, or logs.

## Repository Installation

After the app is created, install it only on the test repository.

For a personal account:

1. GitHub -> Settings.
2. Developer settings.
3. GitHub Apps.
4. Select the app.
5. Install App or Configure.
6. Choose **Only selected repositories**.
7. Select `OWNER/REPO`.
8. Save.

For an organization:

1. Open the organization.
2. Settings.
3. GitHub Apps.
4. Select the app.
5. Install App or Configure.
6. Choose **Only selected repositories**.
7. Select `OWNER/REPO`.
8. Save.

Do not install the preview app on all repositories for the first run.

GitHub installation state can take a short time to propagate. In the dashboard,
use **Refresh now** after changing installation or permissions.

## Common Setup Failures

| Symptom | Likely cause | Fix |
| --- | --- | --- |
| GitHub App ID missing | App ID not configured or manifest config not present. | Set `GITHUB_APP_ID` or complete dashboard setup. |
| Private key missing | PEM file not mounted or wrong path. | Place the PEM at the expected host path and configure `/secrets/github-app.pem`. |
| Private key invalid | Wrong file, truncated PEM, or permissions problem. | Generate a new private key and replace the local PEM. |
| Authentication fails | App ID and PEM do not belong to the same app. | Use the matching App ID/private key pair. |
| Repository installation not found | App is not installed on the target repo or allowlist is wrong. | Install the app on `OWNER/REPO` and set `INTENT_GATEWAY_ALLOWED_REPOS=OWNER/REPO`. |

## Preview Notes

- The GitHub App private key stays local to the Gateway.
- The agent never receives the PEM.
- Install the app on the test repository only, not on all repositories.
- Use **Refresh now** in the dashboard after GitHub installation or permission
  changes.
- The self-hosted preview does not imply a hosted or cloud path is currently
  available.
