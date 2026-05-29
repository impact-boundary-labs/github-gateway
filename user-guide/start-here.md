# Start Here

The **Self-hosted GitHub Gateway v1.3** is a local Gateway that separates
agent read access from repository write impact.

Core idea:

> Agents may read repository state and propose changes. Repository impact goes
> through the Gateway.

Without that split, an agent often ends up holding GitHub write credentials and
can create repository impact directly. Self-hosted GitHub Gateway v1.3 shows a different model:
the agent reads GitHub, submits structured intent to the Gateway, and only
admitted intent becomes a **reviewable pull request**.

Self-hosted GitHub Gateway v1.3 is intended for test repositories and controlled evaluation before
production use.

## What Problem It Solves

The Gateway gives you a boundary between:

- what the agent can read
- what the agent can propose
- what is allowed to become real GitHub impact

The goal is **controlled repository impact** with **no direct GitHub write
access for the agent**.

## What You Need

- Docker Desktop running locally
- the extracted self-hosted folder
- a browser for the local dashboard
- a GitHub account or organization
- a small GitHub test repository

The local dashboard runs at:

```text
http://127.0.0.1:18080/dashboard
```

If port `18080` is busy, edit `.env` and change `IGW_HOST_PORT`.

On Windows, start with `Start GitHub Gateway.cmd`. On macOS/Linux, run:

```sh
chmod +x scripts/*.sh
./scripts/start-gateway.sh
```

The ZIP is built on Windows, so macOS/Linux may need `chmod +x` after
extraction. The current bundled image is `linux/amd64`; Docker Desktop on Apple
Silicon may run it via emulation.

## Recommended First Run

Do not start with a real project repository.

Use the bundled test repository template first:

```text
test-repo-template/
```

It gives you a matching demo policy and predictable allowed/blocked paths.

## Where To Go Next

Quick path in this repository:

- `user-guide/setup.md`
- `user-guide/security-model.md`
- `user-guide/run-demo.md`
- `user-guide/troubleshooting.md`
- `user-guide/agent-cheatsheet.md`

Quick path in the extracted self-hosted ZIP:

- `user-guide/setup.md`
- `user-guide/security-model.md`
- `user-guide/run-demo.md`
- `user-guide/troubleshooting.md`
- `user-guide/agent-cheatsheet.md`

Detailed reference:

- `docs/public/githubrepo/02-quickstart.md`
- `docs/public/githubrepo/04-github-app-setup.md`
- `docs/public/githubrepo/06-agent-instructions.md`
- `docs/public/githubrepo/13-limitations.md`
