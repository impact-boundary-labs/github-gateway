$ErrorActionPreference = "Stop"

$PackageRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$ComposeProjectName = "github-gateway-self-hosted"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker was not found. Nothing was stopped." -ForegroundColor Red
    exit 1
}

Push-Location -LiteralPath $PackageRoot
try {
    docker compose -p $ComposeProjectName --env-file .env -f docker-compose.yml down --remove-orphans
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
