# GitHub CLI 安装和设置指南

## 1. 安装 GitHub CLI

### 方法 A: 使用 winget (Windows)
```powershell
# 以管理员身份运行 PowerShell
winget install --id GitHub.cli

# 如果遇到协议问题，使用：
winget install --id GitHub.cli --accept-package-agreements --accept-source-agreements
```

### 方法 B: 使用 Chocolatey (Windows)
```powershell
# 以管理员身份运行 PowerShell
choco install gh -y
```

### 方法 C: 手动下载
1. 访问: https://github.com/cli/cli/releases
2. 下载 `gh_*_windows_amd64.msi`
3. 运行安装程序
4. 重启终端

### 方法 D: 使用 Scoop (Windows)
```powershell
scoop install gh
```

## 2. 验证安装

安装后，验证 GitHub CLI 是否正常工作：
```bash
# 检查版本
gh --version

# 预期输出类似:
# gh version 2.89.0 (2026-03-25)
# https://github.com/cli/cli/releases/tag/v2.89.0
```

如果命令未找到，请：
1. 重启终端
2. 检查 PATH 环境变量
3. 手动添加安装目录到 PATH

## 3. 认证 GitHub CLI

### 首次认证
```bash
# 启动认证流程
gh auth login

# 按照提示操作:
# 1. 选择 GitHub.com
# 2. 选择 HTTPS 协议
# 3. 选择 "Login with a web browser"
# 4. 复制验证码
# 5. 在浏览器中打开链接
# 6. 输入验证码
# 7. 授权访问
```

### 验证认证状态
```bash
# 检查认证状态
gh auth status

# 预期输出:
# github.com
#   ✓ Logged in to github.com as YOUR_USERNAME (github.com)
#   ✓ Git operations for github.com configured to use https protocol.
#   ✓ Token: *******************
```

### 使用不同方式认证
```bash
# 使用个人访问令牌 (PAT)
gh auth login --with-token < your_token.txt

# 使用 GitHub Enterprise
gh auth login --hostname github.yourcompany.com
```

## 4. 基本命令测试

### 测试仓库访问
```bash
# 查看当前仓库
gh repo view

# 列出问题
gh issue list

# 查看 Pull Requests
gh pr list
```

### 测试工作流
```bash
# 列出工作流
gh workflow list

# 查看工作流运行
gh run list
```

## 5. 配置 GitHub CLI

### 设置默认编辑器
```bash
# 设置 VS Code 为默认编辑器
gh config set editor "code --wait"

# 设置 Vim 为默认编辑器
gh config set editor vim

# 设置记事本为默认编辑器 (Windows)
gh config set editor notepad
```

### 设置 Git 协议
```bash
# 使用 HTTPS (默认)
gh config set git_protocol https

# 使用 SSH
gh config set git_protocol ssh
```

### 查看配置
```bash
# 查看所有配置
gh config list
```

## 6. 故障排除

### 常见问题

#### 问题 1: "command not found"
```bash
# 检查安装位置
where gh

# 手动添加到 PATH (Windows)
setx PATH "%PATH%;C:\Program Files\GitHub CLI\"

# 重启终端
```

#### 问题 2: 认证失败
```bash
# 登出并重新登录
gh auth logout
gh auth login

# 检查令牌权限
gh auth status --show-token
```

#### 问题 3: 权限不足
```bash
# 检查当前用户
gh api /user

# 检查仓库权限
gh api /repos/OWNER/REPO/collaborators/USERNAME/permission
```

#### 问题 4: 网络问题
```bash
# 检查 GitHub API 状态
gh api /meta

# 设置代理 (如果需要)
set HTTPS_PROXY=http://proxy.example.com:8080
set HTTP_PROXY=http://proxy.example.com:8080
```

## 7. 为 CI/CD 管道准备

### 创建自动化脚本
```bash
#!/bin/bash
# setup-gh-cli.sh

# 检查 GitHub CLI
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI..."
    # 根据操作系统安装
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt update
        sudo apt install gh
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh
    elif [[ "$OSTYPE" == "msys" ]]; then
        winget install --id GitHub.cli
    fi
fi

# 检查认证
if ! gh auth status &> /dev/null; then
    echo "Please authenticate GitHub CLI:"
    echo "1. Run: gh auth login"
    echo "2. Follow the prompts"
    exit 1
fi

echo "GitHub CLI is ready!"
```

### 在 GitHub Actions 中使用
```yaml
# .github/workflows/ci-cd.yml 中的示例
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Setup GitHub CLI
        run: |
          gh auth status
          # 使用 GitHub CLI 命令
          gh api /repos/${{ github.repository }}/branches/main/protection
```

## 8. 高级功能

### 使用 GitHub API
```bash
# 获取仓库信息
gh api /repos/OWNER/REPO

# 获取分支保护规则
gh api /repos/OWNER/REPO/branches/main/protection

# 创建环境
gh api --method PUT /repos/OWNER/REPO/environments/production \
  -f '{"wait_timer":30}'
```

### 管理密钥
```bash
# 设置仓库密钥
gh secret set MY_SECRET --repo OWNER/REPO --body "secret-value"

# 设置环境密钥
gh secret set DB_PASSWORD --repo OWNER/REPO --env production --body "db-pass"

# 列出密钥
gh secret list --repo OWNER/REPO
```

### 管理工作流
```bash
# 触发工作流
gh workflow run "CI/CD Pipeline" --ref develop

# 查看工作流运行
gh run view --log <RUN_ID>

# 下载产物
gh run download <RUN_ID>
```

## 9. 安全最佳实践

### 令牌管理
```bash
# 使用最小权限令牌
# 在 https://github.com/settings/tokens 创建令牌时选择:
# - repo (完全控制仓库)
# - workflow (GitHub Actions)
# - read:org (读取组织信息)

# 定期轮换令牌
# 建议每90天更新一次
```

### 审计日志
```bash
# 查看认证日志
gh auth status --show-token

# 查看 API 使用
gh api /rate_limit
```

### 环境隔离
```bash
# 为不同环境使用不同认证
gh auth login --hostname github.company.com --scopes "repo,workflow"
```

## 10. 有用的别名和快捷方式

### 创建别名
```bash
# 查看 PR
alias ghpr="gh pr view --web"

# 查看问题
alias ghissue="gh issue view --web"

# 查看工作流
alias ghworkflow="gh workflow view --web"

# 快速创建 PR
alias ghprc="gh pr create --fill"
```

### 常用命令组合
```bash
# 创建并查看 PR
gh pr create --fill && gh pr view --web

# 部署并监控
gh workflow run "Deploy" --ref main && gh run list --workflow="Deploy" --limit=1

# 检查部署状态
gh api /repos/OWNER/REPO/deployments | jq '.[0].statuses[0].state'
```

## 11. 参考资料

- [GitHub CLI 官方文档](https://cli.github.com/manual/)
- [GitHub API 文档](https://docs.github.com/en/rest)
- [安装指南](https://github.com/cli/cli#installation)
- [认证指南](https://docs.github.com/en/rest/authentication)