Write-Host "Setting up Memory OS environment..."

python -m pip install -r "Configuration\requirements.txt"

if (-not (Test-Path "Main Application\data")) {
    New-Item -ItemType Directory -Path "Main Application\data" | Out-Null
}

if (-not (Test-Path "Main Application\data\memories.json")) {
    "{`"short_term`": [], `"long_term`": [], `"archived`": []}" | Out-File -FilePath "Main Application\data\memories.json" -Encoding utf8
}

Write-Host "Setup complete."
