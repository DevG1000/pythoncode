#!/bin/bash
# Setup Permissions Script
# Applies repository permissions and configurations

echo "Setting up GitHub repository permissions..."
echo "=========================================="

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI is not installed. Please install it first:"
    echo "  Windows: winget install --id GitHub.cli"
    echo "  macOS: brew install gh"
    echo "  Linux: sudo apt install gh"
    echo ""
    echo "After installation, authenticate with: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Not authenticated with GitHub. Please run: gh auth login"
    exit 1
fi

echo ""
echo "Available commands:"
echo "=================="
echo ""
echo "1. Apply branch protection rules:"
echo "   ./scripts/apply_branch_protection.sh"
echo ""
echo "2. View current permissions:"
echo "   gh api /repos/{owner}/{repo}/collaborators"
echo ""
echo "3. View team permissions:"
echo "   gh api /orgs/{org}/teams"
echo ""
echo "4. Set up environments:"
echo "   # Create staging environment"
echo "   gh api --method PUT /repos/{owner}/{repo}/environments/staging \\"
echo "     --input .github/environments/staging.yml"
echo ""
echo "   # Create production environment"
echo "   gh api --method PUT /repos/{owner}/{repo}/environments/production \\"
echo "     --input .github/environments/production.yml"
echo ""
echo "5. Configure repository settings:"
echo "   gh api --method PATCH /repos/{owner}/{repo} \\"
echo "     -f '{\"allow_squash_merge\": true, \"allow_merge_commit\": false, \"allow_rebase_merge\": true}'"
echo ""
echo "6. Set up webhooks (if needed):"
echo "   gh api --method POST /repos/{owner}/{repo}/hooks \\"
echo "     -f '{\"name\": \"web\", \"active\": true, \"events\": [\"push\", \"pull_request\"], \"config\": {\"url\": \"https://your-webhook-url.com\", \"content_type\": \"json\"}}'"
echo ""
echo "Note: Replace {owner} and {repo} with your GitHub organization and repository name."
echo ""
echo "For detailed permission setup, refer to:"
echo "- .github/permissions.yml (team and individual permissions)"
echo "- .github/environments/ (environment configurations)"
echo "- .github/branch-protection-rules.yml (branch protection rules)"
echo ""
echo "Manual steps required:"
echo "====================="
echo "1. Create teams in GitHub organization"
echo "2. Add members to teams"
echo "3. Set team repository permissions"
echo "4. Configure environment secrets"
echo "5. Set up required status checks"
echo ""
echo "Automation recommendations:"
echo "==========================="
echo "Consider using Infrastructure as Code (IaC) tools like:"
echo "- Terraform with github provider"
echo "- Pulumi with GitHub resources"
echo "- GitHub's own repository templates"
echo ""
echo "For production use, implement:"
echo "- Regular permission audits"
echo -e "- Secret rotation automation\n- Access review workflows"