#!/bin/bash
# Script to apply branch protection rules using GitHub CLI
# Run these commands manually if GitHub CLI is installed

echo "Applying branch protection rules for main branch..."
echo ""

# Main branch protection
echo "Command for main branch:"
echo "gh api repos/\${{ github.repository }}/branches/main/protection \\"
echo "  --method PUT \\"
echo "  --header 'Accept: application/vnd.github+json' \\"
echo "  --header 'X-GitHub-Api-Version: 2022-11-28' \\"
echo "  --input .github/branch-protection-rules.yml"
echo ""

# Develop branch protection
echo "Command for develop branch:"
echo "gh api repos/\${{ github.repository }}/branches/develop/protection \\"
echo "  --method PUT \\"
echo "  --header 'Accept: application/vnd.github+json' \\"
echo "  --header 'X-GitHub-Api-Version: 2022-11-28' \\"
echo "  --input .github/branch-protection-rules.yml"
echo ""

echo "To install GitHub CLI:"
echo "Windows: winget install --id GitHub.cli"
echo "macOS: brew install gh"
echo "Linux: sudo apt install gh"
echo ""

echo "After installing, authenticate with:"
echo "gh auth login"