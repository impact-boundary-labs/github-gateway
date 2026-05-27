# Run Demo

This is the short path for the preview demo flow.

Detailed reference:

- `docs/public/githubrepo/02-quickstart.md`
- `docs/public/githubrepo/06-agent-instructions.md`
- `test-repo-template/docs/policy-explained.md`

## 1. Use The Test Repo Template

Start with:

```text
test-repo-template/
```

Copy it into a new empty GitHub repository, commit it as the human owner, and
install the GitHub App only on that repository.

Make sure the Gateway allowlist matches that repository:

```text
INTENT_GATEWAY_ALLOWED_REPOS=owner/repo
```

If `.env` still contains `OWNER/REPO`, the dashboard and demo stay in a
partial state and the story demo will fail with `repo_allowlist`. This value
belongs in `.env`, not in `data/agents.env`.

## 2. Know The Preview Policy

Bundled preview examples:

- allowed path:

```text
config/live-demo-pass.yaml
```

- blocked path:

```text
security/live-demo-blocked.yaml
```

Important:

```text
config/* allows direct files under config/
```

It does not allow nested paths like:

```text
config/demo/file.yaml
```

## 3. Prepare The Agent Inputs

The agent needs:

- `INTENT_GATEWAY_URL`
- `INTENT_GATEWAY_API_KEY`
- `GITHUB_READ_TOKEN`
- `TEST_REPO`
- `TEST_BRANCH`

The agent must have **no direct GitHub write access**.

If the shell is not already configured, the story demo first looks for:

```text
data/agents.env
```

Values already set in the shell still win. `TEST_REPO` is required and must
match `INTENT_GATEWAY_ALLOWED_REPOS` in `.env`. If you changed
`IGW_HOST_PORT`, the generated `INTENT_GATEWAY_URL` should use the same host
port.

## 4. Run The Story Demo

From the extracted preview folder:

```powershell
python examples/self-hosted/github-gateway-story-demo.py
```

The demo prints the target repo and branch before it starts. If `TEST_REPO`
does not match the configured Gateway allowlist, it stops early with a local
error instead of sending a confusing blocked request.

## 5. What The Demo Should Show

The intended cases are:

- allowed write under `config/live-demo-pass.yaml`
- blocked write under `security/live-demo-blocked.yaml`
- `content_sanity` failure for an invalid payload under an allowed path
- stale state conflict after the repository state changes
- follow-up update on the same Gateway pull request

## 6. Expected Outcomes

- **Admitted**: a reviewable pull request is created
- **Blocked**: no repository impact
- **Conflict**: the agent must re-read and resubmit
- **Follow-up**: the same Gateway pull request is updated

Watch the dashboard activity feed while the demo runs. It should show sanitized
decision data, not raw payloads or secrets.
