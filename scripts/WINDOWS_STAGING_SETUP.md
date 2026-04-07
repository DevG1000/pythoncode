# Windows Staging Environment Setup Guide

## 概述
本文档介绍如何在Windows系统上设置和管理GitHub Actions的staging环境变量和密钥。

## 前提条件

### 1. 安装GitHub CLI
```powershell
# 使用winget安装（推荐）
winget install --id GitHub.cli

# 或从官网下载安装
# https://github.com/cli/cli/releases
```

### 2. 认证GitHub CLI
```powershell
# 运行认证命令
gh auth login

# 按照提示操作：
# 1. 选择 "GitHub.com"
# 2. 选择 "HTTPS"
# 3. 选择 "Login with a web browser"
# 4. 复制一次性代码
# 5. 在浏览器中打开链接并粘贴代码
```

## 使用方法

### 方法1：使用批处理脚本（简单）
```cmd
# 运行批处理脚本
scripts\setup_staging_env_windows.bat
```

### 方法2：使用PowerShell脚本（推荐）
```powershell
# 查看环境状态
.\scripts\manage_staging_env.ps1 status

# 设置默认配置
.\scripts\manage_staging_env.ps1 setup

# 添加环境变量
.\scripts\manage_staging_env.ps1 addvar DB_HOST localhost

# 添加环境密钥
.\scripts\manage_staging_env.ps1 addsecret DB_PASSWORD mypassword

# 查看帮助
.\scripts\manage_staging_env.ps1 help
```

### 方法3：手动设置
```powershell
# 设置环境变量
gh variable set ENVIRONMENT --env staging --body "staging"
gh variable set LOG_LEVEL --env staging --body "DEBUG"
gh variable set API_URL --env staging --body "https://api.staging.pythoncode.com"

# 设置环境密钥
gh secret set STAGING_DATABASE_URL --env staging --body "postgresql://staging_user:staging_pass@localhost:5432/staging_db"
gh secret set STAGING_REDIS_URL --env staging --body "redis://localhost:6379/0"
gh secret set STAGING_API_KEY --env staging --body "staging_api_key_test_123"

# 验证设置
gh variable list --env staging
gh secret list --env staging
```

## 已设置的环境变量

| 变量名 | 值 | 描述 |
|--------|-----|------|
| ENVIRONMENT | staging | 环境标识 |
| LOG_LEVEL | DEBUG | 日志级别 |
| API_URL | https://api.staging.pythoncode.com | API地址 |

## 已设置的环境密钥

| 密钥名 | 描述 |
|--------|------|
| STAGING_DATABASE_URL | 测试数据库连接字符串 |
| STAGING_REDIS_URL | 测试Redis连接 |
| STAGING_API_KEY | 测试环境API密钥 |

## 在CI/CD工作流中使用

### 示例工作流配置
```yaml
name: Deploy to Staging
on:
  push:
    branches: [develop]

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: staging  # 指定使用staging环境
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      
      - name: Use environment variables
        run: |
          echo "Environment: ${{ vars.ENVIRONMENT }}"
          echo "Log Level: ${{ vars.LOG_LEVEL }}"
          echo "API URL: ${{ vars.API_URL }}"
      
      - name: Use environment secrets
        run: |
          echo "Database URL is set: ${{ secrets.STAGING_DATABASE_URL != '' && 'YES' || 'NO' }}"
          echo "API Key is set: ${{ secrets.STAGING_API_KEY != '' && 'YES' || 'NO' }}"
```

## 故障排除

### 常见问题

1. **"gh: command not found"**
   - 重启终端或重新打开PowerShell
   - 检查PATH环境变量：`where gh`

2. **认证失败**
   - 运行：`gh auth status`
   - 重新认证：`gh auth logout && gh auth login`

3. **权限不足**
   - 确保GitHub账户有仓库的管理员权限
   - 检查仓库设置中的权限

4. **环境不存在**
   - 创建环境：`gh api --method PUT repos/DevG1000/pythoncode/environments/staging -f '{"wait_timer":0}'`

### 验证命令
```powershell
# 检查GitHub CLI
gh --version

# 检查认证
gh auth status

# 检查环境
gh api repos/DevG1000/pythoncode/environments/staging

# 列出所有变量和密钥
gh variable list --env staging
gh secret list --env staging
```

## 安全建议

1. **定期轮换密钥**：每90天更新一次API密钥
2. **最小权限原则**：只授予必要的权限
3. **环境隔离**：不同环境使用不同的密钥
4. **访问审计**：定期检查谁访问了密钥

## 相关资源

- [GitHub CLI文档](https://cli.github.com/manual/)
- [GitHub Actions环境文档](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [GitHub Actions密钥文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

## 支持
如有问题，请查看：
- `scripts/setup_environment_secrets.md` - 详细密钥设置指南
- `QUICK_STAGING_SETUP.md` - 快速设置指南
- `.github/environments/staging.yml` - 环境配置文件