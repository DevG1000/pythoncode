# PowerShell script to install GitHub CLI
Write-Host "Installing GitHub CLI..." -ForegroundColor Cyan

# Method 1: Check if already installed
try {
    $ghVersion = gh --version 2>$null
    if ($ghVersion) {
        Write-Host "GitHub CLI is already installed:" -ForegroundColor Green
        Write-Host $ghVersion -ForegroundColor Green
        exit 0
    }
} catch {
    Write-Host "GitHub CLI not found, proceeding with installation..." -ForegroundColor Yellow
}

# Method 2: Try winget (requires admin)
Write-Host "`nAttempting to install with winget..." -ForegroundColor Yellow
try {
    # Check if winget is available
    $wingetCheck = Get-Command winget -ErrorAction SilentlyContinue
    if ($wingetCheck) {
        Write-Host "Found winget, installing GitHub CLI..." -ForegroundColor Green
        winget install --id GitHub.cli --accept-package-agreements --accept-source-agreements
    } else {
        Write-Host "winget not found" -ForegroundColor Red
    }
} catch {
    Write-Host "Winget installation failed: $_" -ForegroundColor Red
}

# Method 3: Try Chocolatey
Write-Host "`nAttempting to install with Chocolatey..." -ForegroundColor Yellow
try {
    # Check if Chocolatey is available
    $chocoCheck = Get-Command choco -ErrorAction SilentlyContinue
    if ($chocoCheck) {
        Write-Host "Found Chocolatey, installing GitHub CLI..." -ForegroundColor Green
        choco install gh -y
    } else {
        Write-Host "Chocolatey not found" -ForegroundColor Red
    }
} catch {
    Write-Host "Chocolatey installation failed: $_" -ForegroundColor Red
}

# Method 4: Manual download
Write-Host "`nIf automatic installation failed, please:" -ForegroundColor Yellow
Write-Host "1. Download from: https://github.com/cli/cli/releases" -ForegroundColor Yellow
Write-Host "2. Run the installer manually" -ForegroundColor Yellow
Write-Host "3. Restart your terminal" -ForegroundColor Yellow

# Verify installation
Write-Host "`nVerifying installation..." -ForegroundColor Cyan
try {
    $ghCheck = Get-Command gh -ErrorAction SilentlyContinue
    if ($ghCheck) {
        Write-Host "✅ GitHub CLI installed successfully!" -ForegroundColor Green
        gh --version
    } else {
        Write-Host "❌ GitHub CLI installation failed" -ForegroundColor Red
        Write-Host "Please install manually from: https://cli.github.com/" -ForegroundColor Yellow
    }
} catch {
    Write-Host "Verification failed: $_" -ForegroundColor Red
}