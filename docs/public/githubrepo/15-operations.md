# Operations

This is a public operations guide for Self-hosted GitHub Gateway v1.3. It avoids
private operational details and focuses on safe self-hosted operation.

## Start

Windows launcher: use the start launcher included in the self-hosted folder.

Manual start:

```powershell
docker load -i github-gateway-self-hosted.tar
docker compose --env-file .env -f docker-compose.yml up -d
```

The launcher should load the bundled self-hosted image when the tar is present, then
start Docker Compose.

## Stop

Windows launcher: use the stop launcher included in the self-hosted folder.

Manual stop:

```powershell
docker compose --env-file .env -f docker-compose.yml down
```

## Logs

Windows launcher: use the log launcher included in the self-hosted folder.

Manual logs:

```powershell
docker compose --env-file .env -f docker-compose.yml logs --tail=80
```

Do not post secrets, Runner Keys, GitHub tokens, PEM contents, payloads, diffs,
raw responses, or private logs.

## Health

Liveness:

```text
/livez
```

Readiness:

```text
/healthz
```

`/livez` should return OK when the HTTP server is alive. `/healthz` may report
not ready while GitHub App setup or repository installation is incomplete.

## Local State

Important local files:

```text
data/state.db
data/intent_gateway_pepper
data/agents.env
data/github-app-config.json
data/github-app.pem
secrets/github-app.pem
```

Do not share or commit local state.

## Backups

For self-hosted evaluation, preserve local state only if you need continuity:

- `data/state.db`
- `data/intent_gateway_pepper`
- `data/github-app-config.json`
- `data/github-app.pem`

If you do not need continuity, start from a fresh extracted folder.

## Updates

For a new self-hosted package:

1. Stop the old Gateway.
2. Extract the new self-hosted ZIP into a new folder.
3. Copy or recreate only the local state you intentionally want to keep.
4. Start the new self-hosted package.
5. Use **Refresh now** in the dashboard.

Do not copy old logs, raw responses, temporary payloads, or unrelated local
files into a public demo folder.

## Operator Rules

- Use a test repository first.
- Install the GitHub App only on selected repositories.
- Keep the agent free of direct GitHub write credentials.
- Keep Runner Keys and GitHub Read Tokens out of commits and screenshots.
- Review every Gateway-created pull request before merge.
