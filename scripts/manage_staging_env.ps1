# PowerShell script for managing staging environment on Windows
# Usage: .\manage_staging_env.ps1 [command]

param(
    [string]$Command = "status"
)

$Owner = "DevG1000"
$Repo = "pythoncode"

function Show-Header {
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host "   Staging Environment Manager for Windows" -ForegroundColor Cyan
    Write-Host "===========================================" -ForegroundColor Cyan
    Write-Host "Repository: $Owner/$Repo" -ForegroundColor Yellow
    Write-Host ""
}

function Check-GitHubCLI {
    Write-Host "Checking GitHub CLI..." -ForegroundColor Yellow
    try {
        $ghVersion = gh --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ GitHub CLI is installed" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ GitHub CLI is not installed or not in PATH" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ GitHub CLI check failed: $_" -ForegroundColor Red
        return $false
    }
}

function Check-Authentication {
    Write-Host "Checking authentication..." -ForegroundColor Yellow
    try {
        $authStatus = gh auth status 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ GitHub CLI is authenticated" -ForegroundColor Green
            return $true
        } else {
            Write-Host "❌ GitHub CLI is not authenticated" -ForegroundColor Red
            return $false
        }
    } catch {
        Write-Host "❌ Authentication check failed: $_" -ForegroundColor Red
        return $false
    }
}

function Show-Status {
    Write-Host "Environment Status:" -ForegroundColor Cyan
    Write-Host "-------------------" -ForegroundColor Cyan
    
    # Check if environment exists
    try {
        $envInfo = gh api repos/$Owner/$Repo/environments/staging 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Staging environment exists" -ForegroundColor Green
        } else {
            Write-Host "❌ Staging environment not found" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error checking environment: $_" -ForegroundColor Red
    }
    
    # List variables
    Write-Host "`nEnvironment Variables:" -ForegroundColor Cyan
    Write-Host "---------------------" -ForegroundColor Cyan
    try {
        $variables = gh variable list --env staging 2>$null
        if ($LASTEXITCODE -eq 0) {
            if ($variables) {
                $variables | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
            } else {
                Write-Host "  No variables found" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "  Error listing variables" -ForegroundColor Red
    }
    
    # List secrets
    Write-Host "`nEnvironment Secrets:" -ForegroundColor Cyan
    Write-Host "-------------------" -ForegroundColor Cyan
    try {
        $secrets = gh secret list --env staging 2>$null
        if ($LASTEXITCODE -eq 0) {
            if ($secrets) {
                $secrets | ForEach-Object { Write-Host "  $_" -ForegroundColor White }
            } else {
                Write-Host "  No secrets found" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "  Error listing secrets" -ForegroundColor Red
    }
}

function Add-Variable {
    param(
        [string]$Name,
        [string]$Value
    )
    
    Write-Host "Adding variable: $Name" -ForegroundColor Yellow
    try {
        gh variable set $Name --env staging --body $Value 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Variable '$Name' added successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to add variable '$Name'" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error adding variable: $_" -ForegroundColor Red
    }
}

function Add-Secret {
    param(
        [string]$Name,
        [string]$Value
    )
    
    Write-Host "Adding secret: $Name" -ForegroundColor Yellow
    try {
        gh secret set $Name --env staging --body $Value 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Secret '$Name' added successfully" -ForegroundColor Green
        } else {
            Write-Host "❌ Failed to add secret '$Name'" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error adding secret: $_" -ForegroundColor Red
    }
}

function Setup-Defaults {
    Write-Host "Setting up default configuration..." -ForegroundColor Cyan
    
    # Add default variables
    $defaultVariables = @{
        "ENVIRONMENT" = "staging"
        "LOG_LEVEL" = "DEBUG"
        "API_URL" = "https://api.staging.pythoncode.com"
        "APP_VERSION" = "1.0.0"
        "MAX_RETRIES" = "3"
    }
    
    foreach ($var in $defaultVariables.Keys) {
        Add-Variable -Name $var -Value $defaultVariables[$var]
    }
    
    # Add default secrets
    $defaultSecrets = @{
        "STAGING_DATABASE_URL" = "postgresql://staging_user:staging_pass@localhost:5432/staging_db"
        "STAGING_REDIS_URL" = "redis://localhost:6379/0"
        "STAGING_API_KEY" = "staging_api_key_$(New-Guid)"
        "STAGING_JWT_SECRET" = "$([System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes((New-Guid).ToString())))"
    }
    
    foreach ($secret in $defaultSecrets.Keys) {
        Add-Secret -Name $secret -Value $defaultSecrets[$secret]
    }
    
    Write-Host "`n✅ Default configuration setup complete!" -ForegroundColor Green
}

function Show-Help {
    Write-Host "Usage: .\manage_staging_env.ps1 [command]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Available commands:" -ForegroundColor Yellow
    Write-Host "  status     - Show current environment status (default)" -ForegroundColor White
    Write-Host "  setup      - Set up default variables and secrets" -ForegroundColor White
    Write-Host "  addvar     - Add a new environment variable" -ForegroundColor White
    Write-Host "  addsecret  - Add a new environment secret" -ForegroundColor White
    Write-Host "  help       - Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\manage_staging_env.ps1 status" -ForegroundColor White
    Write-Host "  .\manage_staging_env.ps1 setup" -ForegroundColor White
    Write-Host "  .\manage_staging_env.ps1 addvar DB_HOST localhost" -ForegroundColor White
    Write-Host "  .\manage_staging_env.ps1 addsecret DB_PASSWORD mypassword" -ForegroundColor White
}

# Main execution
Show-Header

# Check prerequisites
if (-not (Check-GitHubCLI)) {
    Write-Host "`nPlease install GitHub CLI first:" -ForegroundColor Yellow
    Write-Host "  winget install --id GitHub.cli" -ForegroundColor White
    Write-Host "  or download from: https://github.com/cli/cli/releases" -ForegroundColor White
    exit 1
}

if (-not (Check-Authentication)) {
    Write-Host "`nPlease authenticate GitHub CLI:" -ForegroundColor Yellow
    Write-Host "  gh auth login" -ForegroundColor White
    exit 1
}

# Execute command
switch ($Command.ToLower()) {
    "status" {
        Show-Status
    }
    "setup" {
        Setup-Defaults
        Show-Status
    }
    "addvar" {
        if ($args.Count -lt 2) {
            Write-Host "Usage: .\manage_staging_env.ps1 addvar NAME VALUE" -ForegroundColor Red
            exit 1
        }
        Add-Variable -Name $args[0] -Value $args[1]
    }
    "addsecret" {
        if ($args.Count -lt 2) {
            Write-Host "Usage: .\manage_staging_env.ps1 addsecret NAME VALUE" -ForegroundColor Red
            exit 1
        }
        Add-Secret -Name $args[0] -Value $args[1]
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use 'help' to see available commands" -ForegroundColor Yellow
    }
}

Write-Host "`nDone!" -ForegroundColor Green