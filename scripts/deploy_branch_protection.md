# 分支保护规则部署指南

## 1. 安装 GitHub CLI

### Windows
```powershell
# 方法1: 使用 winget
winget install --id GitHub.cli

# 方法2: 使用 Chocolatey
choco install gh

# 方法3: 手动下载
# 访问: https://github.com/cli/cli/releases
# 下载 gh_*_windows_amd64.msi 并安装
```

### macOS
```bash
# 使用 Homebrew
brew install gh

# 或使用 MacPorts
sudo port install gh
```

### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install gh

# Fedora
sudo dnf install gh

# Arch Linux
sudo pacman -S github-cli
```

## 2. 认证 GitHub CLI

```bash
# 登录 GitHub
gh auth login

# 选择 GitHub.com
# 选择 HTTPS 协议
# 选择 "Login with a web browser"
# 按照提示完成认证
```

## 3. 应用分支保护规则

### 方法A: 使用自定义格式 (推荐)
使用 `.github/branch-protection-rules.yml` 中的 CLI 命令：

```bash
# 设置变量
OWNER="your-github-username"
REPO="pythoncode"

# 应用 main 分支保护
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/$OWNER/$REPO/branches/main/protection \
  -f '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["code-quality", "security-scan", "test-coverage", "build", "docker-build"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 2,
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": true,
      "require_last_push_approval": false
    },
    "restrictions": null,
    "required_linear_history": true,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "block_creations": false,
    "required_conversation_resolution": true,
    "lock_branch": false,
    "allow_fork_syncing": false
  }'

# 应用 develop 分支保护
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/$OWNER/$REPO/branches/develop/protection \
  -f '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["code-quality", "security-scan", "test-coverage"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": false,
      "require_last_push_approval": false
    },
    "restrictions": null,
    "required_linear_history": false,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "block_creations": false,
    "required_conversation_resolution": true,
    "lock_branch": false,
    "allow_fork_syncing": true
  }'
```

### 方法B: 使用 API 格式文件
使用 `.github/branch-protection-api.yml`：

```bash
# 创建 JSON 文件
cat > branch-protection-main.json << 'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "security-audit",
      "lint-and-format",
      "quality-gates-assessment",
      "unit-tests",
      "integration-tests",
      "e2e-tests",
      "docker-build"
    ]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "required_approving_review_count": 2,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": false
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": false
}
EOF

# 应用规则
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/$OWNER/$REPO/branches/main/protection \
  --input branch-protection-main.json
```

## 4. 验证分支保护

```bash
# 查看 main 分支保护状态
gh api /repos/$OWNER/$REPO/branches/main/protection

# 查看 develop 分支保护状态
gh api /repos/$OWNER/$REPO/branches/develop/protection

# 查看所有分支保护规则
gh api /repos/$OWNER/$REPO/branches | jq '.[].protection'
```

## 5. 手动设置 (如果没有 GitHub CLI)

### 通过 GitHub Web 界面
1. 访问: `https://github.com/OWNER/REPO/settings/branches`
2. 点击 "Add branch protection rule"
3. 分支名称模式: `main`
4. 设置:
   - ✅ Require a pull request before merging
   - ✅ Require approvals (2 required)
   - ✅ Dismiss stale pull request approvals
   - ✅ Require review from Code Owners
   - ✅ Require status checks to pass
     - 添加检查: `security-audit`, `lint-and-format`, `quality-gates-assessment`, `unit-tests`, `integration-tests`, `e2e-tests`, `docker-build`
   - ✅ Require branches to be up to date before merging
   - ✅ Include administrators
   - ✅ Restrict who can push to matching branches
   - ✅ Allow force pushes: ❌
   - ✅ Allow deletions: ❌

5. 重复步骤 2-4 为 `develop` 分支 (调整设置)

## 6. 状态检查上下文

确保以下状态检查在工作流中定义：
- `security-audit` - 安全审计
- `lint-and-format` - 代码格式检查
- `quality-gates-assessment` - 质量门评估
- `unit-tests` - 单元测试
- `integration-tests` - 集成测试
- `e2e-tests` - 端到端测试
- `docker-build` - Docker 构建

## 7. 故障排除

### 常见问题

1. **"Resource not accessible by integration"**
   ```bash
   # 确保有足够的权限
   gh auth status
   # 可能需要组织管理员权限
   ```

2. **状态检查未显示**
   ```bash
   # 等待工作流运行一次
   # 或手动触发工作流
   gh workflow run "CI/CD Pipeline"
   ```

3. **API 错误**
   ```bash
   # 检查 API 版本
   gh api --version
   # 使用正确的头部
   -H "Accept: application/vnd.github+json"
   -H "X-GitHub-Api-Version: 2022-11-28"
   ```

### 测试命令
```bash
# 测试认证
gh auth status

# 测试 API 访问
gh api /user

# 测试仓库访问
gh api /repos/$OWNER/$REPO

# 列出工作流
gh workflow list
```

## 8. 自动化脚本

创建 `apply-protection.sh`:
```bash
#!/bin/bash
set -e

OWNER="${1:-your-username}"
REPO="${2:-pythoncode}"

echo "Applying branch protection for $OWNER/$REPO"

# Main branch
echo "Protecting main branch..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/$OWNER/$REPO/branches/main/protection \
  -f '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["security-audit", "lint-and-format", "quality-gates-assessment", "unit-tests", "integration-tests", "e2e-tests", "docker-build"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 2,
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": true,
      "require_last_push_approval": false
    },
    "restrictions": null,
    "required_linear_history": true,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "block_creations": false,
    "required_conversation_resolution": true,
    "lock_branch": false,
    "allow_fork_syncing": false
  }'

# Develop branch
echo "Protecting develop branch..."
gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  /repos/$OWNER/$REPO/branches/develop/protection \
  -f '{
    "required_status_checks": {
      "strict": true,
      "contexts": ["security-audit", "lint-and-format", "quality-gates-assessment", "unit-tests"]
    },
    "enforce_admins": false,
    "required_pull_request_reviews": {
      "required_approving_review_count": 1,
      "dismiss_stale_reviews": true,
      "require_code_owner_reviews": false,
      "require_last_push_approval": false
    },
    "restrictions": null,
    "required_linear_history": false,
    "allow_force_pushes": false,
    "allow_deletions": false,
    "block_creations": false,
    "required_conversation_resolution": true,
    "lock_branch": false,
    "allow_fork_syncing": true
  }'

echo "Branch protection applied successfully!"
```

运行:
```bash
chmod +x apply-protection.sh
./apply-protection.sh your-username pythoncode
```

## 9. 后续步骤

1. **验证状态检查**: 推送更改并确保所有状态检查通过
2. **测试 PR 流程**: 创建测试 PR 验证保护规则
3. **监控合规性**: 定期检查分支保护状态
4. **更新规则**: 根据需要调整保护规则

## 10. 参考资料

- [GitHub CLI 文档](https://cli.github.com/manual/)
- [GitHub Branch Protection API](https://docs.github.com/en/rest/branches/branch-protection)
- [分支保护设置指南](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/managing-a-branch-protection-rule)