#!/bin/bash
# Script to create staging environment using GitHub CLI
# Run after installing and authenticating GitHub CLI

echo "Creating Staging Environment"
echo "============================"

# Configuration
OWNER="${1:-your-github-username}"
REPO="${2:-pythoncode}"
ENV_NAME="staging"

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI is not installed"
    echo "Please install it first:"
    echo "  Windows: winget install --id GitHub.cli"
    echo "  macOS: brew install gh"
    echo "  Linux: sudo apt install gh"
    echo ""
    echo "After installation, authenticate with: gh auth login"
    exit 1
fi

# Check authentication
if ! gh auth status &> /dev/null; then
    echo "Error: GitHub CLI is not authenticated"
    echo "Please run: gh auth login"
    exit 1
fi

echo "Creating environment: $ENV_NAME for $OWNER/$REPO"
echo ""

# Create staging environment with basic configuration
echo "Command 1: Create basic staging environment"
echo "-------------------------------------------"
cat << 'EOF'
gh api --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$OWNER/$REPO/environments/staging \
  -f '{
    "wait_timer": 0,
    "reviewers": [],
    "deployment_branch_policy": {
      "protected_branches": false,
      "custom_branch_policies": true
    }
  }'
EOF

echo ""
echo "Command 2: Add reviewers (if teams exist)"
echo "-----------------------------------------"
cat << 'EOF'
# First, get team IDs
TEAM_BACKEND_ID=$(gh api /orgs/$ORG/teams/backend-team --jq '.id')
TEAM_QA_ID=$(gh api /orgs/$ORG/teams/qa-team --jq '.id')

# Update environment with reviewers
gh api --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$OWNER/$REPO/environments/staging \
  -f '{
    "wait_timer": 0,
    "reviewers": [
      {"type": "Team", "id": '$TEAM_BACKEND_ID'},
      {"type": "Team", "id": '$TEAM_QA_ID'}
    ],
    "deployment_branch_policy": {
      "protected_branches": false,
      "custom_branch_policies": true
    }
  }'
EOF

echo ""
echo "Command 3: Set environment variables"
echo "------------------------------------"
cat << 'EOF'
# Note: Environment variables need to be set via GitHub UI or API
# This is a template for setting variables

# Set individual variables
gh variable set ENVIRONMENT --env staging --body "staging"
gh variable set LOG_LEVEL --env staging --body "DEBUG"
gh variable set API_URL --env staging --body "https://api.staging.pythoncode.com"

# Or use bulk approach
cat > staging-vars.json << 'JSONVARS'
{
  "variables": [
    {"name": "ENVIRONMENT", "value": "staging"},
    {"name": "LOG_LEVEL", "value": "DEBUG"},
    {"name": "API_URL", "value": "https://api.staging.pythoncode.com"}
  ]
}
JSONVARS

gh api --method PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$OWNER/$REPO/environments/staging/variables \
  --input staging-vars.json
EOF

echo ""
echo "Command 4: Set environment secrets"
echo "----------------------------------"
cat << 'EOF'
# Set secrets (replace with actual values)
gh secret set STAGING_DATABASE_URL --env staging --body "postgresql://user:pass@staging-db:5432/app"
gh secret set STAGING_REDIS_URL --env staging --body "redis://staging-redis:6379"
gh secret set STAGING_API_KEY --env staging --body "staging_api_key_123"
gh secret set STAGING_SSH_KEY --env staging --body "$(cat ~/.ssh/id_rsa_staging)"
EOF

echo ""
echo "Simplified One-Command Version"
echo "------------------------------"
cat << 'EOF'
# Replace YOUR_USERNAME and YOUR_REPO
OWNER="YOUR_USERNAME"
REPO="YOUR_REPO"

gh api --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$OWNER/$REPO/environments/staging \
  -f '{
    "wait_timer": 0,
    "reviewers": [],
    "deployment_branch_policy": {
      "protected_branches": false,
      "custom_branch_policies": true
    }
  }' && \
echo "Staging environment created successfully!"
EOF

echo ""
echo "Verification Commands"
echo "---------------------"
cat << 'EOF'
# Check if environment exists
gh api /repos/$OWNER/$REPO/environments/staging

# List all environments
gh api /repos/$OWNER/$REPO/environments

# Check environment variables
gh variable list --env staging

# Check environment secrets
gh secret list --env staging
EOF

echo ""
echo "Troubleshooting"
echo "---------------"
echo "If you get 'Resource not accessible by integration' error:"
echo "1. Make sure you have admin rights to the repository"
echo "2. Check authentication: gh auth status"
echo "3. Try with personal access token with repo scope"
echo ""
echo "If environment already exists, use PATCH instead of PUT:"
cat << 'EOF'
gh api --method PATCH \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  /repos/$OWNER/$REPO/environments/staging \
  -f '{
    "wait_timer": 0,
    "reviewers": []
  }'
EOF

echo ""
echo "Next Steps After Creating Environment"
echo "-------------------------------------"
echo "1. Set up environment-specific secrets"
echo "2. Configure deployment workflows to use the environment"
echo "3. Test deployments to staging"
echo "4. Set up monitoring and alerts"
echo ""
echo "For detailed configuration, see: .github/environments/staging.yml"