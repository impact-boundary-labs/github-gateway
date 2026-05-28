# Self-hosted GitHub Gateway v1.3 Test Repository

This folder is a copyable test repository template for the self-hosted GitHub
Gateway v1.3 run. Use it instead of connecting a real project repository first.

The Gateway reads repository policy from:

```text
.github/intent-gateway.yaml
```

## Create The Test Repository

1. Create a new empty GitHub repository.
2. Copy the contents of this folder into that repository.
3. Commit and push the template files manually as the human repository owner.
4. Install the GitHub App only on this test repository.
5. Create a Runner Key for this repository and branch.
6. Give the agent only the Runner Key and a GitHub Read Token.
7. Run the self-hosted demo.

Do not give the agent GitHub write credentials, the GitHub App private key, SSH
keys with write access, or Git Credential Manager write access.

## Policy Shape

The included policy allows direct files under `config/` and blocks sensitive
areas:

```text
allowed: config/*
blocked: security/*, .github/*
```

The human repository owner commits `.github/intent-gateway.yaml` during initial
test repository setup. After that, Gateway-submitted writes under `.github/*`
are blocked, including attempts to change the policy file through the Gateway.

Allowed demo paths:

```text
config/live-demo-pass.yaml
config/self-hosted-gateway-demo.yaml
config/gateway-load-test-20260520T091206Z-001.yaml
```

Blocked demo paths:

```text
security/live-demo-blocked.yaml
.github/workflows/unsafe.yaml
config/demo/file.yaml
```

In this test policy, `config/*` allows direct files under `config/`. It does
not allow nested paths such as `config/demo/file.yaml`.

Read [docs/policy-explained.md](docs/policy-explained.md) before running the
demo.
