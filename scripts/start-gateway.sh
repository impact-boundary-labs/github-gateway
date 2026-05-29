#!/usr/bin/env sh
set -eu

package_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
compose_project_name="github-gateway-self-hosted"
image_name="github-gateway-self-hosted:1.3.2"
image_tar="$package_root/github-gateway-self-hosted.tar"
env_file="$package_root/.env"
env_example_file="$package_root/.env.example"
compose_file="$package_root/docker-compose.yml"

fail() {
  printf '\n%s\n' "$1" >&2
  exit 1
}

read_host_port() {
  path=$1
  if [ ! -f "$path" ]; then
    printf '%s\n' "18080"
    return
  fi
  line=$(grep -E '^[[:space:]]*IGW_HOST_PORT[[:space:]]*=' "$path" | head -n 1 || true)
  if [ -z "$line" ]; then
    printf '%s\n' "18080"
    return
  fi
  value=${line#*=}
  value=$(printf '%s' "$value" | sed "s/^[[:space:]'\"]*//; s/[[:space:]'\"]*$//")
  if [ -z "$value" ]; then
    printf '%s\n' "18080"
    return
  fi
  printf '%s\n' "$value"
}

remove_legacy_compose_containers() {
  working_dir=$1
  current_project=$2
  ids=$(docker ps -aq --filter "label=com.docker.compose.project.working_dir=$working_dir")
  for id in $ids; do
    [ -n "$id" ] || continue
    project=$(docker inspect --format '{{ index .Config.Labels "com.docker.compose.project" }}' "$id" 2>/dev/null || true)
    if [ -z "$project" ] || [ "$project" = "$current_project" ]; then
      continue
    fi
    container_name=$(docker inspect --format '{{ .Name }}' "$id" 2>/dev/null | sed 's#^/##' || true)
    [ -n "$container_name" ] || container_name=$id
    printf 'Removing legacy self-hosted container %s...\n' "$container_name"
    docker rm -f "$id" >/dev/null
  done
}

if ! command -v docker >/dev/null 2>&1; then
  fail "Docker was not found. Install and start Docker Desktop or Docker Engine, then run this launcher again."
fi

if ! docker info >/dev/null 2>&1; then
  fail "Docker does not appear to be running. Start Docker, wait until it is ready, then run this launcher again."
fi

if ! docker compose version >/dev/null 2>&1; then
  fail "Docker Compose was not found. Install Docker Desktop or the Docker Compose plugin, then run this launcher again."
fi

if [ ! -f "$env_file" ]; then
  if [ -f "$env_example_file" ]; then
    cp "$env_example_file" "$env_file"
    printf 'Created .env from .env.example. Edit .env before running the demo if INTENT_GATEWAY_ALLOWED_REPOS is still OWNER/REPO.\n'
  else
    fail ".env is missing from the self-hosted folder."
  fi
fi

if [ ! -f "$compose_file" ]; then
  fail "docker-compose.yml is missing from the self-hosted folder."
fi

mkdir -p "$package_root/data" "$package_root/secrets"

if [ -f "$image_tar" ]; then
  printf 'Loading bundled self-hosted image...\n'
  docker load -i "$image_tar" >/dev/null
else
  printf 'No bundled image tar found; using local image tag.\n' >&2
  docker image inspect "$image_name" >/dev/null 2>&1 || fail "Docker image $image_name is not loaded and github-gateway-self-hosted.tar was not found."
fi

(
  cd "$package_root"
  docker compose -p "$compose_project_name" --env-file .env -f docker-compose.yml down --remove-orphans >/dev/null 2>&1 || true
  remove_legacy_compose_containers "$package_root" "$compose_project_name"
  docker compose -p "$compose_project_name" --env-file .env -f docker-compose.yml up -d
)

port=$(read_host_port "$env_file")
dashboard_url="http://127.0.0.1:$port/dashboard"

printf '\nSelf-hosted GitHub Gateway v1.3 is starting.\n'
printf 'Dashboard: %s\n\n' "$dashboard_url"
printf 'If setup is incomplete, /healthz may report unhealthy. This is expected until GitHub App setup is complete.\n'
printf 'Use /livez for basic HTTP liveness.\n'

if command -v open >/dev/null 2>&1; then
  open "$dashboard_url" >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then
  xdg-open "$dashboard_url" >/dev/null 2>&1 || true
fi
