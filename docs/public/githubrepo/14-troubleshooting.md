# Troubleshooting

This page covers common first-run issues in GitHub Gateway Self-hosted 1.3.

Start with the dashboard status column and the Activity log. The Activity log is
especially useful after a demo run because it shows sanitized Gateway decisions
without payloads, tokens, private keys, or raw request bodies.

## Docker Desktop Not Running

Symptom:

- dashboard does not open
- Compose fails to start
- Docker commands fail

Likely cause:

- Docker Desktop is stopped or still starting

Fix:

1. Start Docker Desktop.
2. Wait until Docker reports it is running.
3. Start the preview again.

## Port 18080 Occupied

Symptom:

- Compose fails with a port binding error
- dashboard URL does not load
- another service responds on port 18080

Likely cause:

- another process is already using host port `18080`

Fix:

1. Stop the other process, or choose another host port.
2. If using a custom host port, set the preview port override.
3. Use the same port in `INTENT_GATEWAY_URL`.

Example:

```dotenv
INTENT_GATEWAY_URL=http://127.0.0.1:18081
```

## Dashboard Reachable But GitHub App Not Configured

Symptom:

- `/livez` returns OK
- dashboard opens
- GitHub App ID or private key status is missing or error
- `/healthz` may report not ready

Likely cause:

- HTTP server is alive, but Gateway write identity is not configured

Fix:

1. Complete dashboard GitHub App setup, or use manual setup.
2. Confirm the Gateway has the GitHub App ID.
3. Confirm the Gateway can read the private key.
4. Use **Refresh now**.

## PEM Path Issues

Symptom:

- dashboard says private key missing or unusable
- GitHub App authentication fails

Likely cause:

- PEM file is missing
- PEM is mounted at the wrong host path
- Gateway is configured with a host path instead of a container path
- PEM does not match the App ID

Fix:

Manual setup should use the container path:

```dotenv
GITHUB_APP_PRIVATE_KEY_PATH=/secrets/github-app.pem
```

Place the actual file in the preview's `secrets/` folder as expected by the
package. Do not paste PEM contents into docs, chat, logs, or issues.

## GitHub App Not Installed On Repository

Symptom:

- dashboard says repository installation not found or inaccessible
- write readiness is not OK
- demo fails before creating PRs

Likely cause:

- app was created but not installed on `OWNER/REPO`
- app was installed on a different repository
- app installation is still propagating
- `INTENT_GATEWAY_ALLOWED_REPOS` does not match the demo target

Fix:

1. Open GitHub App installation settings.
2. Choose **Only selected repositories**.
3. Select `OWNER/REPO`.
4. Save.
5. Confirm `.env` contains `INTENT_GATEWAY_ALLOWED_REPOS=OWNER/REPO`.
6. Restart the Gateway after `.env` changes.
7. Use **Refresh now** in the dashboard.

## Runner Key Missing Or Invalid

Symptom:

- dashboard says Runner Key missing or invalid
- demo returns unauthorized or forbidden submit responses

Likely cause:

- no Runner Key exists
- wrong Runner Key in `data/agents.env`
- Runner Key belongs to another repo or branch scope
- local Gateway state changed

Fix:

1. Create a new Runner Key in the dashboard.
2. Let the dashboard update `data/agents.env`, or update the file manually.
3. Confirm `TEST_REPO` and `TEST_BRANCH` match the Runner Key scope.
4. Do not confuse Runner Key with GitHub Read Token.

## GITHUB_READ_TOKEN Returns 401, 403, Or 404

Symptom:

- demo cannot read branch head or file state
- GitHub API read calls fail
- token appears valid but repo read fails

Likely cause:

- token missing
- token expired
- token scoped to wrong owner
- token scoped to wrong repository
- permissions are too narrow
- repository is private and token lacks access

Fix:

Create a fine-grained token with:

- repository access: only selected repositories
- repository: `OWNER/REPO`
- Contents: read-only
- Pull requests: read-only
- Metadata: read-only

Store it in:

```dotenv
GITHUB_READ_TOKEN=<github-read-token>
```

Do not put the GitHub Read Token in the Gateway `.env`. The Gateway does not
need it.

## Agent Can Still git push

Symptom:

- the push isolation check succeeds

Likely cause:

- Git Credential Manager has stored write credentials
- `gh auth` has write access
- SSH key has write access
- classic PAT or other write credential is available

Fix:

Use a clean agent environment without GitHub write credentials.

Check:

```powershell
git -c credential.helper= push --dry-run origin HEAD:refs/heads/ggw-readonly-push-test
```

Expected:

```text
The push must fail.
```

## config/* Nested Path Mistake

Symptom:

- path under `config/` is blocked even though policy allows `config/*`

Likely cause:

- `config/*` allows direct files only

Allowed:

```text
config/file.yaml
```

Not allowed:

```text
config/nested/file.yaml
```

Fix:

Use a direct file path for the first demo or update policy intentionally.

## No PR Created After Blocked Or Conflict

Symptom:

- demo reports Blocked or Conflict
- no branch, commit, or PR appears in GitHub

Likely cause:

- this is expected behavior

Fix:

Open the dashboard Activity log and read:

- decision
- request status
- reject stage
- required next action

For Blocked, fix path, policy, content, or scope. For Conflict, re-read state
and build a new intent if appropriate.

## Dashboard Shows Stale Status

Symptom:

- app was installed or credentials changed
- dashboard still shows old state

Likely cause:

- remote GitHub checks are cached briefly
- GitHub installation state is still propagating

Fix:

Use **Refresh now**. If needed, wait a minute and refresh again.

## Demo Stops On repo_allowlist

Symptom:

- demo stops with `repo_allowlist`

Likely cause:

- `TEST_REPO` in `data/agents.env` does not match `INTENT_GATEWAY_ALLOWED_REPOS`
- Gateway was not restarted after editing `.env`

Fix:

1. Set `INTENT_GATEWAY_ALLOWED_REPOS=OWNER/REPO` in `.env`.
2. Set `TEST_REPO=OWNER/REPO` in `data/agents.env`.
3. Restart the Gateway.
4. Use **Refresh now**.
5. Run the demo again.
