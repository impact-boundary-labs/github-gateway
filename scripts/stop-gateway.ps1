$ErrorActionPreference = "Stop"

$PreviewRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "Docker was not found. Nothing was stopped." -ForegroundColor Red
    exit 1
}

Push-Location -LiteralPath $PreviewRoot
try {
    docker compose --env-file .env -f docker-compose.yml down
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
