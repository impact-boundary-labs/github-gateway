# Troubleshooting

Use this as the short operator checklist.

Detailed reference:

- `docs/public/githubrepo/02-quickstart.md`
- `docs/public/githubrepo/04-github-app-setup.md`
- `docs/public/githubrepo/06-agent-instructions.md`
- `docs/public/githubrepo/07-policy-yaml.md`

## Docker not running

**Symptom**

- the launcher fails immediately
- Docker commands fail

**Likely cause**

- Docker Desktop is not running

**Fix**

- start Docker Desktop
- wait until Docker is ready
- start the preview again

## Port 18080 occupied

**Symptom**

- `http://localhost:18080/dashboard` does not open
- compose reports a bind error

**Likely cause**

- another local process already uses port `18080`

**Fix**

- edit `.env`
- set `IGW_HOST_PORT=18081`
- start again
- create or refresh the Runner Key agent settings so `data/agents.env` uses
  the same port in `INTENT_GATEWAY_URL`

## GitHub App installation not found

**Symptom**

- dashboard shows app authentication OK
- repository installation still missing

**Likely cause**

- the app was installed on the wrong repository
- or not installed at all

**Fix**

- open the GitHub App installation page
- choose **Only selected repositories**
- install only on the correct preview test repository
- wait a moment if GitHub is still propagating the install
- use **Refresh now** in the dashboard

## Manifest app invalid

**Symptom**

- dashboard says the local GitHub App setup is invalid

**Likely cause**

- the manifest-created local app files no longer match a real usable app
- or the local files became unreadable or stale

**Fix**

- use **Reset local GitHub App setup**
- create the app again with Manifest Flow
- or use the manual fallback from `docs/public/githubrepo/04-github-app-setup.md`

## Dashboard says GitHub App invalid

**Symptom**

- Step 1 shows invalid local GitHub App setup

**Likely cause**

- same as manifest invalid: local app files are present but not usable

**Fix**

- reset local GitHub App setup
- recreate the app
- verify installation on the correct test repository

## Reset local GitHub App setup

**Symptom**

- you created the wrong app
- or deleted the app in GitHub
- or Step 1 is stuck in an invalid state

**Likely cause**

- the preview still holds old local manifest-created app files

**Fix**

- use **Reset local GitHub App setup** in the dashboard
- this removes only the local manifest-created App ID/PEM files
- it does not remove Runner Keys, `state.db`, the pepper file, or repository data

## Runner Key missing or invalid

**Symptom**

- dashboard says Runner Key missing
- or says a Runner Key was found but is not valid

**Likely cause**

- no current valid Runner Key exists
- or the old one was invalidated or replaced

**Fix**

- create a new Runner Key in the dashboard
- store it immediately
- update `data/agents.env` or the shell where the agent starts

## GitHub Read Token returns 401

**Symptom**

- the agent cannot read repository state

**Likely cause**

- wrong token
- wrong repository scope
- wrong token permissions

**Fix**

- use a fine-grained token
- scope it only to the preview test repository
- use read-only permissions:
  - Contents
  - Pull requests
  - Metadata

## Agent can still git push

**Symptom**

- direct `git push` works from the agent environment

**Likely cause**

- ambient GitHub write credentials are still available

**Fix**

- remove cached write credentials
- remove write PATs
- remove SSH write access
- remove `gh auth` write access
- remove GitHub App private key access from the agent environment

Check:

```bash
git -c credential.helper= push --dry-run origin HEAD:refs/heads/igw-readonly-push-test
```

Run that check from PowerShell in a local clone of the target test repository.

Expected:

```text
The push must fail.
```

## Path blocked by policy

**Symptom**

- Gateway returns `Blocked`
- activity shows `policy_scope`

**Likely cause**

- the path is outside the allowed preview policy

**Fix**

- use allowed paths such as `config/live-demo-pass.yaml`
- keep blocked examples under `security/...` or `.github/...`

## config/* does not allow nested paths

**Symptom**

- the path looks like it is under `config/`
- but the Gateway still blocks it

**Likely cause**

- the path is nested

Allowed:

```text
config/example.yaml
```

Blocked by scope:

```text
config/demo/example.yaml
```

**Fix**

- use direct files under `config/`

## Demo stops with repo_allowlist

**Symptom**

- the story demo stops early
- the Gateway returns `Blocked`
- `reject_stage=repo_allowlist`

**Likely cause**

- `INTENT_GATEWAY_ALLOWED_REPOS` still contains `OWNER/REPO`
- or `TEST_REPO` in `data/agents.env` does not match the configured allowlist

**Fix**

- set `INTENT_GATEWAY_ALLOWED_REPOS` to the real test repository
- set it in `.env`, not in `data/agents.env`
- update `data/agents.env` so `TEST_REPO` matches that repository
- restart the preview if you changed `.env`
- use **Refresh now** and then run the demo again
