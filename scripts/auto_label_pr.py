#!/usr/bin/env python3
"""
Auto-label PR script
Automatically adds labels to Pull Requests based on changed files and content.

Usage:
    python auto_label_pr.py --pr <pr_number>
    python auto_label_pr.py (reads PR_NUMBER from environment)

Labels are added based on:
- File types changed (.py, .js, .md, etc.)
- File paths (api/, tests/, docs/, etc.)
- Content analysis (security, bug, feature, etc.)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Set

# GitHub API configuration (would be set by GitHub Actions)
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.environ.get("GITHUB_REPOSITORY", "owner/repo")
GITHUB_API_URL = "https://api.github.com"


def run_command(cmd: str, cwd: str = None) -> Dict[str, Any]:
    """Run a command and return result."""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
        return {
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "returncode": -1}


def get_pr_number() -> int:
    """Get PR number from environment or command line."""
    # From environment variable
    pr_number = os.environ.get("PR_NUMBER")
    if pr_number:
        return int(pr_number)

    # From command line argument
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg.startswith("--pr="):
                return int(arg.split("=")[1])

    # From GitHub Actions context
    if "GITHUB_EVENT_PATH" in os.environ:
        try:
            with open(os.environ["GITHUB_EVENT_PATH"], "r") as f:
                event_data = json.load(f)
                return event_data.get("pull_request", {}).get("number", 0)
        except (json.JSONDecodeError, IOError):
            pass

    return 0


def get_changed_files(pr_number: int = 0) -> List[str]:
    """Get list of changed files."""
    changed_files = []

    if pr_number > 0:
        # Try to get changed files using git diff
        cmd = f"git diff --name-only HEAD~1"
        result = run_command(cmd)

        if result["success"] and result["stdout"]:
            changed_files = [f.strip() for f in result["stdout"].split("\n") if f.strip()]
    else:
        # Fallback: get all tracked files
        cmd = "git ls-files"
        result = run_command(cmd)

        if result["success"] and result["stdout"]:
            changed_files = [f.strip() for f in result["stdout"].split("\n") if f.strip()]

    return changed_files


def analyze_changes(files: List[str]) -> Set[str]:
    """Analyze changed files and determine appropriate labels."""
    labels = set()

    for file in files:
        if not file:
            continue

        # Convert to Path object for easier manipulation
        file_path = Path(file)

        # File extension based labels
        if file_path.suffix == ".py":
            labels.add("python")
        elif file_path.suffix in [".js", ".jsx"]:
            labels.add("javascript")
        elif file_path.suffix in [".ts", ".tsx"]:
            labels.add("typescript")
        elif file_path.suffix == ".md":
            labels.add("documentation")
        elif file_path.suffix in [".yml", ".yaml"]:
            labels.add("configuration")
        elif file_path.suffix == ".json":
            labels.add("json")
        elif file_path.suffix in [".html", ".css"]:
            labels.add("frontend")

        # Path based labels
        file_str = str(file_path)

        if file_str.startswith("api/"):
            labels.add("api")
            labels.add("backend")
        elif file_str.startswith("command_system/"):
            labels.add("command-system")
            labels.add("backend")
        elif file_str.startswith("card_generator/"):
            labels.add("card-generator")
            labels.add("backend")
        elif file_str.startswith("tests/"):
            labels.add("tests")
            if "test_" in file_path.name or file_path.name.endswith("_test.py"):
                labels.add("unit-tests")
        elif file_str.startswith("docs/"):
            labels.add("documentation")
        elif file_str.startswith(".github/"):
            labels.add("ci-cd")
            labels.add("github")
        elif file_str.startswith("config/"):
            labels.add("configuration")
            labels.add("devops")
        elif file_str.startswith("scripts/"):
            labels.add("scripts")
            labels.add("devops")
        elif file_str.startswith("utils/"):
            labels.add("utilities")
            labels.add("backend")

        # File name based labels
        file_name = file_path.name.lower()

        if "docker" in file_name:
            labels.add("docker")
            labels.add("devops")

        if "docker-compose" in file_name:
            labels.add("docker-compose")
            labels.add("devops")

        if "requirements" in file_name:
            labels.add("dependencies")

        if "test" in file_name and file_path.suffix == ".py":
            labels.add("tests")

        # Content analysis (simplified - would need file content)
        # This is a placeholder for more sophisticated analysis

    return labels


def analyze_pr_content(pr_title: str = "", pr_body: str = "") -> Set[str]:
    """Analyze PR title and body for additional labels."""
    labels = set()

    content = f"{pr_title} {pr_body}".lower()

    # Bug/fix related
    if any(word in content for word in ["fix", "bug", "issue", "error", "bugfix"]):
        labels.add("bug")

    # Feature related
    if any(word in content for word in ["feat", "feature", "add", "new", "implement"]):
        labels.add("feature")

    # Refactor related
    if any(word in content for word in ["refactor", "cleanup", "optimize", "improve"]):
        labels.add("refactor")

    # Security related
    if any(word in content for word in ["security", "vulnerability", "auth", "login", "password"]):
        labels.add("security")

    # Performance related
    if any(word in content for word in ["performance", "speed", "fast", "optimization"]):
        labels.add("performance")

    # Documentation related
    if any(word in content for word in ["doc", "documentation", "readme", "comment"]):
        labels.add("documentation")

    # Test related
    if any(word in content for word in ["test", "coverage", "pytest", "unit test"]):
        labels.add("tests")

    # Breaking changes
    if any(word in content for word in ["break", "breaking", "deprecate", "remove"]):
        labels.add("breaking-change")

    # Dependencies
    if any(word in content for word in ["dependenc", "upgrade", "update", "bump"]):
        labels.add("dependencies")

    return labels


def add_labels_via_github_api(pr_number: int, labels: Set[str]) -> bool:
    """Add labels to PR using GitHub API."""
    if not labels:
        print("No labels to add")
        return True

    if not GITHUB_TOKEN:
        print("GitHub token not available - simulating label addition")
        for label in labels:
            print(f"  Would add label: {label}")
        return True

    # Convert set to list
    labels_list = list(labels)

    # Prepare API request
    import requests

    url = f"{GITHUB_API_URL}/repos/{GITHUB_REPOSITORY}/issues/{pr_number}/labels"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {"labels": labels_list}

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            print(f"[SUCCESS] Added {len(labels_list)} labels to PR #{pr_number}")
            for label in labels_list:
                print(f"  - {label}")
            return True
        else:
            print(f"[ERROR] Failed to add labels: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error adding labels: {e}")
        return False


def add_labels_via_gh_cli(pr_number: int, labels: Set[str]) -> bool:
    """Add labels to PR using GitHub CLI."""
    if not labels:
        print("No labels to add")
        return True

    success = True

    for label in labels:
        cmd = f"gh pr edit {pr_number} --add-label '{label}'"
        result = run_command(cmd)

        if result["success"]:
            print(f"  [OK] Added label: {label}")
        else:
            print(f"  [FAIL] Failed to add label {label}: {result.get('stderr', 'Unknown error')}")
            success = False

    return success


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Auto-label Pull Requests")
    parser.add_argument("--pr", type=int, help="PR number")
    parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")
    parser.add_argument("--output", default="labels.json", help="Output file for labels")

    args = parser.parse_args()

    # Get PR number
    pr_number = args.pr or get_pr_number()

    if pr_number == 0:
        print("[ERROR] No PR number provided")
        print("Usage: python auto_label_pr.py --pr <number>")
        print("Or set PR_NUMBER environment variable")
        return 1

    print(f"[ANALYZE] Analyzing PR #{pr_number}...")

    # Get changed files
    changed_files = get_changed_files(pr_number)

    if not changed_files:
        print("[WARNING] No changed files found")
        changed_files = []  # Continue with empty list

    print(f"Found {len(changed_files)} changed files")
    if changed_files:
        print("Changed files:")
        for file in changed_files[:10]:  # Show first 10 files
            print(f"  - {file}")
        if len(changed_files) > 10:
            print(f"  ... and {len(changed_files) - 10} more")

    # Analyze changes
    file_labels = analyze_changes(changed_files)

    # Analyze PR content (placeholder - would need PR title/body)
    content_labels = analyze_pr_content()

    # Combine labels
    all_labels = file_labels.union(content_labels)

    # Add some intelligent labels based on context
    if len(changed_files) > 20:
        all_labels.add("large-pr")

    if "api" in all_labels and "security" in all_labels:
        all_labels.add("security-review-required")

    if "tests" in all_labels and "documentation" not in all_labels:
        all_labels.add("needs-docs")

    # Create report
    report = {
        "pr_number": pr_number,
        "changed_files": changed_files,
        "labels": list(all_labels),
        "label_categories": {"file_based": list(file_labels), "content_based": list(content_labels)},
        "analysis": {
            "total_files": len(changed_files),
            "total_labels": len(all_labels),
            "has_security": "security" in all_labels,
            "has_tests": "tests" in all_labels,
            "has_docs": "documentation" in all_labels,
        },
    }

    # Save report
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n[INFO] Analysis complete")
    print(f"Labels to add: {len(all_labels)}")

    if all_labels:
        print("Labels:")
        for label in sorted(all_labels):
            print(f"  - {label}")

    # Add labels
    if not args.dry_run and all_labels:
        print(f"\n[ACTION] Adding labels to PR #{pr_number}...")

        # Try GitHub CLI first, then API
        success = add_labels_via_gh_cli(pr_number, all_labels)

        if not success:
            print("Falling back to GitHub API...")
            success = add_labels_via_github_api(pr_number, all_labels)

        if success:
            print(f"[SUCCESS] Successfully labeled PR #{pr_number}")
        else:
            print(f"[ERROR] Failed to label PR #{pr_number}")
            return 1
    elif args.dry_run:
        print(f"\n[DRY RUN] Dry run - no labels added")
        print(f"Labels would be: {', '.join(sorted(all_labels))}")

    print(f"\n[REPORT] Report saved to: {args.output}")

    # Output for GitHub Actions
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            f.write(f"labels={json.dumps(list(all_labels))}\n")
            f.write(f"label_count={len(all_labels)}\n")
            f.write(f"has_security_labels={'security' in all_labels}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
