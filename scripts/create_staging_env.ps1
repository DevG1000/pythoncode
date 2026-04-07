# PowerShell script to create staging environment
# Run after installing and authenticating GitHub CLI

Write-Host "Staging Environment Creation Script" -ForegroundColor Cyan
Write-Host "===================================" -ForegroundColor Cyan

# Configuration
$Owner = Read-Host "Enter GitHub username or organization name"
$Repo = Read-Host "Enter repository name (default: pythoncode)"
if ([string]::IsNullOrWhiteSpace($Repo)) { $Repo = "pythoncode" }

Write-Host "`nTarget: $Owner/$Repo" -ForegroundColor Yellow

# Check GitHub CLI
Write-Host "`nChecking GitHub CLI..." -ForegroundColor Yellow
try {
    $ghCheck = gh --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GitHub CLI is installed" -ForegroundColor Green
    } else {
        Write-Host "❌ GitHub CLI is not installed or not in PATH" -ForegroundColor Red
        Write-Host "Please install GitHub CLI first:" -ForegroundColor Yellow
        Write-Host "  winget install --id GitHub.cli" -ForegroundColor Yellow
        Write-Host "  or download from: https://github.com/cli/cli/releases" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ GitHub CLI check failed: $_" -ForegroundColor Red
    exit 1
}

# Check authentication
Write-Host "`nChecking authentication..." -ForegroundColor Yellow
try {
    $authCheck = gh auth status 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ GitHub CLI is authenticated" -ForegroundColor Green
    } else {
        Write-Host "❌ GitHub CLI is not authenticated" -ForegroundColor Red
        Write-Host "Please run: gh auth login" -ForegroundColor Yellow
        Write-Host "Then run this script again" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ Authentication check failed: $_" -ForegroundColor Red
    exit 1
}

# Create staging environment
Write-Host "`nCreating staging environment..." -ForegroundColor Green

$envJson = @{
    wait_timer = 0
    reviewers = @()
    deployment_branch_policy = @{
        protected_branches = $false
        custom_branch_policies = $true
    }
} | ConvertTo-Json -Compress

Write-Host "Command to execute:" -ForegroundColor Cyan
Write-Host "gh api --method PUT \"
Write-Host "  -H `"Accept: application/vnd.github+json`" \"
Write-Host "  -H `"X-GitHub-Api-Version: 2022-11-28`" \"
Write-Host "  /repos/$Owner/$Repo/environments/staging \"
Write-Host "  -f '$envJson'"

Write-Host "`nDo you want to proceed? (Y/N)" -ForegroundColor Yellow
$confirmation = Read-Host

if ($confirmation -eq 'Y' -or $confirmation -eq 'y') {
    try {
        Write-Host "`nExecuting command..." -ForegroundColor Green
        
        $result = gh api --method PUT `
          -H "Accept: application/vnd.github+json" `
          -H "X-GitHub-Api-Version: 2022-11-28" `
          /repos/$Owner/$Repo/environments/staging `
          -f $envJson
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Staging environment created successfully!" -ForegroundColor Green
            Write-Host "`nEnvironment details:" -ForegroundColor Cyan
            Write-Host $result
            
            # Verify creation
            Write-Host "`nVerifying environment..." -ForegroundColor Yellow
            gh api /repos/$Owner/$Repo/environments/staging
            
        } else {
            Write-Host "❌ Failed to create staging environment" -ForegroundColor Red
            Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "❌ Error creating environment: $_" -ForegroundColor Red
    }
} else {
    Write-Host "Operation cancelled" -ForegroundColor Yellow
}

# Next steps
Write-Host "`nNext steps after creating environment:" -ForegroundColor Cyan
Write-Host "1. Set environment variables:" -ForegroundColor Yellow
Write-Host "   gh variable set ENVIRONMENT --env staging --body `"staging`"" -ForegroundColor White
Write-Host "   gh variable set LOG_LEVEL --env staging --body `"DEBUG`"" -ForegroundColor White
Write-Host "   gh variable set API_URL --env staging --body `"https://api.staging.pythoncode.com`"" -ForegroundColor White

Write-Host "`n2. Set environment secrets:" -ForegroundColor Yellow
Write-Host "   gh secret set STAGING_DATABASE_URL --env staging --body `"postgresql://user:pass@staging-db:5432/app`"" -ForegroundColor White
Write-Host "   gh secret set STAGING_REDIS_URL --env staging --body `"redis://staging-redis:6379`"" -ForegroundColor White
Write-Host "   gh secret set STAGING_API_KEY --env staging --body `"staging_api_key_123`"" -ForegroundColor White

Write-Host "`n3. Update workflow to use staging environment:" -ForegroundColor Yellow
Write-Host "   In .github/workflows/ci-cd-integrated-final.yml:" -ForegroundColor White
Write-Host "   Add `environment: staging` to deploy-staging job" -ForegroundColor White

Write-Host "`n4. Test deployment:" -ForegroundColor Yellow
Write-Host "   gh workflow run `".github/workflows/ci-cd-integrated-final.yml`" --ref develop" -ForegroundColor White

Write-Host "`nFor more details, see:" -ForegroundColor Cyan
Write-Host "   - scripts/setup_environment_secrets.md" -ForegroundColor White
Write-Host "   - .github/environments/staging.yml" -ForegroundColor White

Write-Host "`nPress any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")