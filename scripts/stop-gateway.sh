#!/usr/bin/env sh
set -eu

package_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
compose_project_name="github-gateway-self-hosted"

fail() {
  printf '\n%s\n' "$1" >&2
  exit 1
}

if ! command -v docker >/dev/null 2>&1; then
  fail "Docker was not found. Nothing was stopped."
fi

if ! docker info >/dev/null 2>&1; then
  fail "Docker does not appear to be running. Nothing was stopped."
fi

if ! docker compose version >/dev/null 2>&1; then
  fail "Docker Compose was not found. Nothing was stopped."
fi

if [ ! -f "$package_root/docker-compose.yml" ]; then
  fail "docker-compose.yml is missing from the self-hosted folder. Nothing was stopped."
fi

env_file=".env"
if [ ! -f "$package_root/.env" ] && [ -f "$package_root/.env.example" ]; then
  env_file=".env.example"
fi

(
  cd "$package_root"
  docker compose -p "$compose_project_name" --env-file "$env_file" -f docker-compose.yml down --remove-orphans
)

printf '\nSelf-hosted GitHub Gateway v1.3 stopped.\n'
printf 'Local data/ and secrets/ folders were preserved.\n'
