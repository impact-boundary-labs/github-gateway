$ErrorActionPreference = "Stop"

$PackageRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot "..")).Path
$ImageName = "github-gateway-self-hosted:1.3.2"
$ImageTar = Join-Path $PackageRoot "github-gateway-self-hosted.tar"
$EnvFile = Join-Path $PackageRoot ".env"
$EnvExampleFile = Join-Path $PackageRoot ".env.example"
$ComposeFile = Join-Path $PackageRoot "docker-compose.yml"

function Fail($Message) {
    Write-Host ""
    Write-Host $Message -ForegroundColor Red
    exit 1
}

function Read-HostPort($Path) {
    if (-not (Test-Path -LiteralPath $Path)) {
        return "18080"
    }
    $line = Get-Content -LiteralPath $Path | Where-Object { $_ -match "^\s*IGW_HOST_PORT\s*=" } | Select-Object -First 1
    if (-not $line) {
        return "18080"
    }
    $value = ($line -split "=", 2)[1].Trim().Trim('"').Trim("'")
    if ([string]::IsNullOrWhiteSpace($value)) {
        return "18080"
    }
    return $value
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Fail "Docker was not found. Install and start Docker Desktop, then run this launcher again."
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Fail "Docker Desktop does not appear to be running. Start Docker Desktop, wait until it is ready, then run this launcher again."
}

if (-not (Test-Path -LiteralPath $EnvFile)) {
    if (Test-Path -LiteralPath $EnvExampleFile) {
        Copy-Item -LiteralPath $EnvExampleFile -Destination $EnvFile -Force
    } else {
        Fail ".env is missing from the self-hosted folder."
    }
}
if (-not (Test-Path -LiteralPath $ComposeFile)) {
    Fail "docker-compose.yml is missing from the self-hosted folder."
}

New-Item -ItemType Directory -Force -Path (Join-Path $PackageRoot "data") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $PackageRoot "secrets") | Out-Null

if (Test-Path -LiteralPath $ImageTar) {
    Write-Host "Loading bundled self-hosted image..."
    docker load -i $ImageTar
    if ($LASTEXITCODE -ne 0) {
        Fail "Docker image load failed."
    }
} else {
    Write-Host "No bundled image tar found; using local image tag." -ForegroundColor Yellow
    docker image inspect $ImageName *> $null
    if ($LASTEXITCODE -ne 0) {
        Fail "Docker image $ImageName is not loaded and github-gateway-self-hosted.tar was not found."
    }
}

Push-Location -LiteralPath $PackageRoot
try {
    docker compose --env-file .env -f docker-compose.yml up -d
    if ($LASTEXITCODE -ne 0) {
        Fail "Docker Compose failed to start the Gateway."
    }
} finally {
    Pop-Location
}

$port = Read-HostPort $EnvFile
$dashboardURL = "http://localhost:$port/dashboard"
Write-Host ""
Write-Host "Self-hosted GitHub Gateway v1.3 is starting."
Write-Host "Dashboard: $dashboardURL"
Write-Host ""
Write-Host "If setup is incomplete, use the dashboard to create a GitHub App from template or use manual PEM setup."
Start-Process $dashboardURL
