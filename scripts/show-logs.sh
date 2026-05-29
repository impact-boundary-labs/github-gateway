#!/usr/bin/env sh
set -eu

package_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
compose_project_name="github-gateway-self-hosted"

fail() {
  printf '\n%s\n' "$1" >&2
  exit 1
}

if ! command -v docker >/dev/null 2>&1; then
  fail "Docker was not found. Cannot show logs."
fi

if ! docker info >/dev/null 2>&1; then
  fail "Docker does not appear to be running. Cannot show logs."
fi

if ! docker compose version >/dev/null 2>&1; then
  fail "Docker Compose was not found. Cannot show logs."
fi

if [ ! -f "$package_root/docker-compose.yml" ]; then
  fail "docker-compose.yml is missing from the self-hosted folder. Cannot show logs."
fi

env_file=".env"
if [ ! -f "$package_root/.env" ] && [ -f "$package_root/.env.example" ]; then
  env_file=".env.example"
fi

printf 'Showing Gateway logs. Logs should not contain tokens, Runner Keys, PEM contents, or .env values; review before sharing.\n'
(
  cd "$package_root"
  docker compose -p "$compose_project_name" --env-file "$env_file" -f docker-compose.yml logs -f
)
