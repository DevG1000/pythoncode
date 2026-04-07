# Quick Staging Environment Setup

## Step 1: Install GitHub CLI (If not installed)

### Windows
```powershell
# Open PowerShell as Administrator
winget install --id GitHub.cli

# If prompted, type 'Y' and press Enter
```

### macOS
```bash
brew install gh
```

### Linux
```bash
sudo apt update
sudo apt install gh
```

## Step 2: Authenticate GitHub CLI

```bash
# Run authentication
gh auth login

# Follow the prompts:
# 1. Select "GitHub.com"
# 2. Select "HTTPS"
# 3. Select "Login with a web browser"
# 4. Copy the one-time code
# 5. Open the link in browser
# 6. Paste the code and authorize
```

## Step 3: Create Staging Environment

### Single Command (Copy and paste):
```bash
# Replace YOUR_USERNAME and YOUR_REPO
OWNER="YOUR_USERNAME"
REPO="YOUR_REPO"

gh api --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$OWNER/$REPO/environments/staging \
  -f '{"wait_timer":0,"reviewers":[],"deployment_branch_policy":{"protected_branches":false,"custom_branch_policies":true}}'
```

### Alternative: Use PowerShell script
```powershell
# Run the provided script
powershell -ExecutionPolicy Bypass -File scripts\create_staging_env.ps1
```

## Step 4: Verify Creation

```bash
# Check if environment exists
gh api /repos/$OWNER/$REPO/environments/staging

# Expected output should show staging environment details
```

## Step 5: Set Required Secrets (For deployment to work)

```bash
# Minimum required secrets for testing
gh secret set STAGING_DATABASE_URL --env staging --body "postgresql://test:test@localhost:5432/test"
gh secret set STAGING_API_KEY --env staging --body "test_key_123"
```

## Step 6: Test the Environment

```bash
# Trigger a test deployment
gh workflow run ".github/workflows/ci-cd-integrated-final.yml" --ref develop

# Monitor the run
gh run list --workflow="CI/CD Pipeline" --limit=5
```

## Troubleshooting

### Error: "Resource not accessible by integration"
- Make sure you're authenticated: `gh auth status`
- Ensure you have admin rights to the repository
- Try creating a personal access token with `repo` scope

### Error: "Environment already exists"
```bash
# Update existing environment
gh api --method PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$OWNER/$REPO/environments/staging \
  -f '{"wait_timer":0}'
```

### Command not found: 'gh'
- Restart your terminal after installation
- Check if GitHub CLI is in PATH: `where gh` (Windows) or `which gh` (macOS/Linux)

## Quick Reference

| Command | Purpose |
|---------|---------|
| `gh --version` | Check installation |
| `gh auth status` | Check authentication |
| `gh api /repos/OWNER/REPO/environments` | List environments |
| `gh secret list --env staging` | List staging secrets |
| `gh variable list --env staging` | List staging variables |

## Next Steps After Setup

1. **Add more secrets** as needed (SSH keys, API tokens, etc.)
2. **Configure deployment workflows** to use the staging environment
3. **Set up monitoring** for staging deployments
4. **Test end-to-end** deployment pipeline

## Need Help?

- Check detailed guide: `scripts/setup_environment_secrets.md`
- Review configuration: `.github/environments/staging.yml`
- Run validation: `python scripts/validate_configuration.py`