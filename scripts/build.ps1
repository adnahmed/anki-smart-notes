# Copyright (C) 2024 Michael Piazza
#
# This file is part of Smart Notes.
#
# Smart Notes is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Smart Notes is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Smart Notes.  If not, see <https://www.gnu.org/licenses/>.

param(
    [Parameter(Position=0)]
    [string]$Command,
    
    [Parameter(Position=1)]
    [string]$Version
)

function Install {
    Write-Host "Installing runtime dependencies to vendor directory..."
    if (Test-Path "vendor") {
        Remove-Item -Recurse -Force vendor
    }
    pip install -r requirements-runtime.txt -t vendor
    Write-Host "Dependencies installed to vendor/"
}

function Clean {
    Write-Host "Cleaning..."
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force dist
    }
    
    $addonPath = "$env:APPDATA\Anki2\addons21\smart-notes"
    if (Test-Path $addonPath) {
        Remove-Item -Recurse -Force $addonPath
    }
}

function Build {
    Write-Host "Building..."
    
    # Clean first
    if (Test-Path "dist") {
        Remove-Item -Recurse -Force dist
    }
    
    # Create dist directories
    New-Item -ItemType Directory -Path "dist" | Out-Null
    
    # Copy files
    Copy-Item "*.py" dist/
    Copy-Item "manifest.json" dist/
    Copy-Item "config.json" dist/
    Copy-Item -Recurse src dist/
    Copy-Item LICENSE dist/
    Copy-Item changelog.md dist/
    
    # Set production environment
    Set-Content -Path "dist/src/env.py" -Value 'environment = "PROD"'
    
    # Remove pycache
    if (Test-Path "dist/__pycache__") {
        Remove-Item -Recurse -Force dist/__pycache__
    }
    
    # Ensure vendor directory exists
    if (-not (Test-Path "vendor")) {
        Write-Host "Vendor directory not found. Running install..."
        Install
    }
    
    # Copy vendor directory
    Copy-Item -Recurse vendor dist/
    
    # Copy voice configurations
    Copy-Item eleven_voices.json dist/
    Copy-Item google_voices.json dist/
    Copy-Item azure_voices.json dist/
    
    # Create zip file (ankiaddon)
    Push-Location dist
    if (Test-Path "smart-notes.ankiaddon") {
        Remove-Item smart-notes.ankiaddon
    }
    Compress-Archive -Path * -DestinationPath smart-notes.ankiaddon -CompressionLevel Optimal
    # Rename from .zip to .ankiaddon if needed
    if (Test-Path "smart-notes.ankiaddon.zip") {
        Move-Item smart-notes.ankiaddon.zip smart-notes.ankiaddon -Force
    }
    Pop-Location
    
    Write-Host "Build complete: dist/smart-notes.ankiaddon"
}

function Link-Dev {
    Write-Host "Linking development environment..."
    $addonPath = "$env:APPDATA\Anki2\addons21\smart-notes"
    
    # Remove if exists
    if (Test-Path $addonPath) {
        Remove-Item -Recurse -Force $addonPath
    }
    
    # Create symbolic link (requires admin or Developer Mode)
    $sourcePath = Get-Location
    New-Item -ItemType SymbolicLink -Path $addonPath -Target $sourcePath | Out-Null
    
    Write-Host "Development link created at: $addonPath"
}

function Link-Dist {
    Write-Host "Linking dist build..."
    $addonPath = "$env:APPDATA\Anki2\addons21\smart-notes"
    
    # Remove if exists
    if (Test-Path $addonPath) {
        Remove-Item -Recurse -Force $addonPath
    }
    
    # Create symbolic link to dist
    $distPath = Join-Path (Get-Location) "dist"
    New-Item -ItemType SymbolicLink -Path $addonPath -Target $distPath | Out-Null
    
    Write-Host "Dist link created at: $addonPath"
}

function Format {
    Write-Host "Formatting code..."
    python -m ruff format .
}

function Lint {
    Write-Host "Linting code..."
    python -m ruff check .
}

function TypeCheck {
    Write-Host "Type checking..."
    python -m pyright .
}

function Check {
    Write-Host "Running all checks..."
    python -m ruff format . --check
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    
    python -m ruff check .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    
    python -m pyright .
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Fix {
    Write-Host "Fixing code issues..."
    python -m ruff format .
    python -m ruff check . --fix
}

function Test {
    Write-Host "Running tests..."
    python -m pytest
}

# Main command dispatcher
switch ($Command) {
    "install" { Install }
    "clean" { Clean }
    "build" { 
        Clean
        Build 
    }
    "link-dev" { Link-Dev }
    "link-dist" { Link-Dist }
    "format" { Format }
    "lint" { Lint }
    "typecheck" { TypeCheck }
    "check" { Check }
    "fix" { Fix }
    "test" { Test }
    default {
        Write-Host "Invalid command: $Command"
        Write-Host ""
        Write-Host "Available commands:"
        Write-Host "  install     - Install runtime dependencies to vendor/"
        Write-Host "  build       - Create production build (smart-notes.ankiaddon)"
        Write-Host "  clean       - Remove dist/ and Anki addon symlink"
        Write-Host "  link-dev    - Symlink current directory to Anki addons21"
        Write-Host "  link-dist   - Symlink dist/ to Anki addons21 for testing builds"
        Write-Host "  format      - Format code with ruff"
        Write-Host "  lint        - Lint code with ruff"
        Write-Host "  typecheck   - Type check with pyright"
        Write-Host "  check       - Run all checks (format, lint, typecheck)"
        Write-Host "  fix         - Auto-fix formatting and linting issues"
        Write-Host "  test        - Run pytest tests"
        exit 1
    }
}

if ($LASTEXITCODE -eq 0) {
    Write-Host "Done"
}
