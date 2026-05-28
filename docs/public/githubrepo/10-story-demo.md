# Story Demo

The Story Demo is a screen-recording-friendly walkthrough of the GitHub
Gateway Self-hosted 1.3 flow.

Run it from the extracted self-hosted folder:

```powershell
python examples/self-hosted/github-gateway-story-demo.py
```

## Required Environment

The demo reads `data/agents.env` when shell variables are missing.

Required values:

```dotenv
INTENT_GATEWAY_URL=http://127.0.0.1:18080
INTENT_GATEWAY_API_KEY=<runner-key>
GITHUB_READ_TOKEN=<github-read-token-if-needed>
TEST_REPO=OWNER/REPO
TEST_BRANCH=TARGET_BRANCH
```

`TEST_REPO` must match `INTENT_GATEWAY_ALLOWED_REPOS` in the Gateway `.env`
file. If the Gateway is running on a custom host port, `INTENT_GATEWAY_URL` must
use that port.

## What It Demonstrates

The intended cases are:

1. Bad intent blocked before impact.
2. Good intent creates a reviewable pull request.
3. Same effect reuses an existing Gateway-created pull request.
4. Follow-up updates the same Gateway-created pull request.
5. Stale state is blocked before write.

## Expected Operator Story

Bad intent:

```text
No branch.
No commit.
No pull request.
```

Good intent:

```text
Reviewable pull request created.
```

Same effect:

```text
Existing Gateway-created pull request reused.
```

Follow-up:

```text
Same pull request updated after parent-head validation.
```

Stale state:

```text
Conflict before write.
Agent must re-read and rebuild the intent.
```

## Demo Paths

Allowed demo path:

```text
config/live-demo-pass-<timestamp>.yaml
```

Blocked demo path:

```text
security/live-demo-blocked-<timestamp>.yaml
```

The test policy allows direct files under `config/` and blocks `security/*`.

The default story demo does not test semantic correctness or secret scanning.
Content-sanity validation is a separate smoke check for implemented format
failures such as executable headers, binary/non-UTF-8 content in guarded modes,
or invalid YAML/JSON. A key-like string inside otherwise valid YAML is not a
content-sanity scanner test.

## What It Should Not Print

The story demo should not print:

- Runner Keys
- GitHub tokens
- GitHub App private keys
- `.env` values
- payload bodies
- raw request bodies
- raw response bodies
- diffs

It may print safe decision data, target repo, target branch, and pull request
URL for admitted/reused work.
