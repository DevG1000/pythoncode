# GitHub 环境密钥设置指南

## 1. 所需密钥列表

### 通用密钥 (所有环境)
| 密钥名称 | 描述 | 示例值 |
|---------|------|--------|
| `DOCKER_USERNAME` | Docker Hub 用户名 | `yourdockeruser` |
| `DOCKER_PASSWORD` | Docker Hub 密码/令牌 | `dckr_pat_xxx` |
| `SLACK_WEBHOOK_URL` | Slack 通知 Webhook | `https://hooks.slack.com/services/xxx` |
| `MAIL_USERNAME` | 邮件服务器用户名 | `notifications@yourdomain.com` |
| `MAIL_PASSWORD` | 邮件服务器密码 | `yourpassword` |
| `NOTIFICATION_EMAIL` | 通知接收邮箱 | `team@yourdomain.com` |

### 开发/测试环境
| 密钥名称 | 描述 | 示例值 |
|---------|------|--------|
| `STAGING_DATABASE_URL` | 测试数据库连接字符串 | `postgresql://user:pass@staging-db:5432/app` |
| `STAGING_REDIS_URL` | 测试 Redis 连接 | `redis://staging-redis:6379` |
| `STAGING_API_KEY` | 测试环境 API 密钥 | `staging_xxx` |
| `STAGING_SSH_KEY` | 测试服务器 SSH 私钥 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `STAGING_HOST` | 测试服务器地址 | `staging.yourdomain.com` |
| `STAGING_USER` | 测试服务器用户名 | `deploy` |

### 生产环境
| 密钥名称 | 描述 | 示例值 |
|---------|------|--------|
| `PRODUCTION_DATABASE_URL` | 生产数据库连接字符串 | `postgresql://user:pass@prod-db:5432/app` |
| `PRODUCTION_REDIS_URL` | 生产 Redis 连接 | `redis://prod-redis:6379` |
| `PRODUCTION_API_KEY` | 生产环境 API 密钥 | `prod_xxx` |
| `PRODUCTION_SSH_KEY` | 生产服务器 SSH 私钥 | `-----BEGIN RSA PRIVATE KEY-----...` |
| `PRODUCTION_HOST` | 生产服务器地址 | `yourdomain.com` |
| `PRODUCTION_USER` | 生产服务器用户名 | `deploy` |
| `SSL_CERTIFICATE` | SSL 证书 | `-----BEGIN CERTIFICATE-----...` |
| `ENCRYPTION_KEY` | 加密密钥 | `32-char-random-string` |

## 2. 设置方法

### 方法A: 使用 GitHub CLI

```bash
# 设置变量
OWNER="your-github-username"
REPO="pythoncode"

# 设置仓库级密钥
gh secret set DOCKER_USERNAME --repo $OWNER/$REPO --body "yourdockeruser"
gh secret set DOCKER_PASSWORD --repo $OWNER/$REPO --body "dckr_pat_xxx"

# 设置环境特定密钥
gh secret set STAGING_DATABASE_URL --repo $OWNER/$REPO --env staging --body "postgresql://user:pass@staging-db:5432/app"
gh secret set PRODUCTION_DATABASE_URL --repo $OWNER/$REPO --env production --body "postgresql://user:pass@prod-db:5432/app"

# 批量设置脚本
#!/bin/bash
set -e

OWNER="${1:-your-username}"
REPO="${2:-pythoncode}"

echo "Setting secrets for $OWNER/$REPO"

# 通用密钥
declare -A secrets=(
  ["DOCKER_USERNAME"]="yourdockeruser"
  ["DOCKER_PASSWORD"]="dckr_pat_xxx"
  ["SLACK_WEBHOOK_URL"]="https://hooks.slack.com/services/xxx"
  ["MAIL_USERNAME"]="notifications@yourdomain.com"
  ["MAIL_PASSWORD"]="yourpassword"
  ["NOTIFICATION_EMAIL"]="team@yourdomain.com"
)

for key in "${!secrets[@]}"; do
  echo "Setting $key..."
  gh secret set "$key" --repo $OWNER/$REPO --body "${secrets[$key]}"
done

echo "Secrets set successfully!"
```

### 方法B: 使用 GitHub Web 界面

1. **访问仓库设置**
   - 打开: `https://github.com/OWNER/REPO/settings`
   - 左侧菜单: "Secrets and variables" → "Actions"

2. **设置仓库密钥**
   - 点击 "New repository secret"
   - 名称: `DOCKER_USERNAME`
   - 值: `yourdockeruser`
   - 点击 "Add secret"
   - 重复添加所有通用密钥

3. **设置环境密钥**
   - 左侧菜单: "Environments"
   - 点击 "staging" 环境
   - 点击 "Environment secrets" → "Add secret"
   - 名称: `STAGING_DATABASE_URL`
   - 值: `postgresql://user:pass@staging-db:5432/app`
   - 重复添加所有 staging 环境密钥
   - 切换到 "production" 环境，重复添加生产密钥

### 方法C: 使用 GitHub API

```bash
# 设置仓库密钥
curl -L \
  -X PUT \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/actions/secrets/DOCKER_USERNAME \
  -d '{"encrypted_value":"ENCRYPTED_VALUE","key_id":"KEY_ID"}'

# 需要先获取公钥用于加密
curl -L \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/OWNER/REPO/actions/secrets/public-key
```

## 3. 密钥生成指南

### Docker Hub 令牌
1. 访问: https://hub.docker.com/settings/security
2. 点击 "New Access Token"
3. 名称: `github-actions`
4. 权限: Read, Write, Delete
5. 复制生成的令牌

### SSH 密钥生成
```bash
# 生成新的 SSH 密钥对
ssh-keygen -t rsa -b 4096 -C "github-actions@yourdomain.com" -f github-actions-key

# 查看公钥
cat github-actions-key.pub

# 查看私钥 (用于密钥设置)
cat github-actions-key

# 在服务器上添加公钥
ssh-copy-id -i github-actions-key.pub user@server
```

### 数据库连接字符串
```bash
# PostgreSQL 格式
postgresql://username:password@hostname:5432/database_name

# 使用环境变量
echo "postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:5432/${DB_NAME}"
```

### API 密钥生成
```bash
# 生成随机 API 密钥
openssl rand -base64 32
# 或
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

## 4. 环境设置

### 创建 GitHub 环境
```bash
# 使用 GitHub CLI 创建环境
gh api --method PUT /repos/$OWNER/$REPO/environments/staging \
  -f '{"wait_timer":0,"reviewers":[{"type":"Team","id":TEAM_ID}]}'

gh api --method PUT /repos/$OWNER/$REPO/environments/production \
  -f '{"wait_timer":30,"reviewers":[{"type":"Team","id":TEAM_ID}]}'
```

### 环境配置验证
```bash
# 查看环境列表
gh api /repos/$OWNER/$REPO/environments

# 查看特定环境
gh api /repos/$OWNER/$REPO/environments/staging

# 查看环境密钥
gh secret list --repo $OWNER/$REPO --env staging
```

## 5. 密钥管理最佳实践

### 安全建议
1. **最小权限原则**: 只授予必要的权限
2. **定期轮换**: 每 90 天轮换一次密钥
3. **访问审计**: 定期审查谁访问了密钥
4. **环境隔离**: 不同环境使用不同密钥
5. **密钥版本控制**: 记录密钥变更历史

### 轮换策略
```bash
#!/bin/bash
# 密钥轮换脚本
set -e

rotate_secret() {
  local secret_name=$1
  local new_value=$2
  local env=${3:-}
  
  echo "Rotating $secret_name..."
  
  if [ -n "$env" ]; then
    gh secret set "$secret_name" --repo $OWNER/$REPO --env "$env" --body "$new_value"
  else
    gh secret set "$secret_name" --repo $OWNER/$REPO --body "$new_value"
  fi
  
  echo "Updated $secret_name"
}

# 生成新密钥
NEW_API_KEY=$(openssl rand -base64 32)

# 轮换 API 密钥
rotate_secret "PRODUCTION_API_KEY" "$NEW_API_KEY" "production"
```

### 备份策略
```bash
#!/bin/bash
# 密钥备份脚本
set -e

BACKUP_DIR="./secrets-backup/$(date +%Y%m%d)"

mkdir -p "$BACKUP_DIR"

# 导出仓库密钥
gh secret list --repo $OWNER/$REPO --json name,createdAt,updatedAt > "$BACKUP_DIR/repo-secrets.json"

# 导出环境密钥
for env in staging production; do
  gh secret list --repo $OWNER/$REPO --env $env --json name,createdAt,updatedAt > "$BACKUP_DIR/${env}-secrets.json"
done

echo "Secrets backed up to $BACKUP_DIR"
```

## 6. 故障排除

### 常见问题

1. **"Secret not found" 错误**
   ```bash
   # 检查密钥是否存在
   gh secret list --repo $OWNER/$REPO
   
   # 检查环境密钥
   gh secret list --repo $OWNER/$REPO --env staging
   ```

2. **权限不足**
   ```bash
   # 检查权限
   gh auth status
   
   # 可能需要仓库管理员权限
   ```

3. **环境未创建**
   ```bash
   # 创建环境
   gh api --method PUT /repos/$OWNER/$REPO/environments/staging \
     -f '{"wait_timer":0}'
   ```

4. **工作流无法读取密钥**
   ```yaml
   # 确保工作流有正确的权限
   permissions:
     contents: read
     secrets: read
   ```

### 测试密钥访问
```bash
# 创建测试工作流
cat > .github/workflows/test-secrets.yml << 'EOF'
name: Test Secrets
on: [workflow_dispatch]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Test Repository Secrets
        run: |
          echo "Testing repository secrets..."
          if [ -n "${{ secrets.DOCKER_USERNAME }}" ]; then
            echo "✓ DOCKER_USERNAME is set"
          else
            echo "✗ DOCKER_USERNAME is not set"
          fi
      
      - name: Test Environment Secrets
        run: |
          echo "Testing environment secrets..."
          # 这些只在特定环境中可用
EOF
```

## 7. 集成测试

### 测试部署流程
```bash
# 手动触发测试部署
gh workflow run "CI/CD Pipeline" --ref develop

# 查看运行状态
gh run list --workflow="CI/CD Pipeline"

# 查看日志
gh run view --log
```

### 验证密钥使用
```yaml
# 在工作流中添加调试步骤
- name: Debug Secrets
  run: |
    echo "Available secrets:"
    echo "DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME != '' && 'SET' || 'NOT SET' }}"
    echo "STAGING_DATABASE_URL: ${{ secrets.STAGING_DATABASE_URL != '' && 'SET' || 'NOT SET' }}"
```

## 8. 监控和告警

### 设置密钥监控
```bash
# 创建密钥监控工作流
cat > .github/workflows/monitor-secrets.yml << 'EOF'
name: Monitor Secrets
on:
  schedule:
    - cron: '0 9 * * 1'  # 每周一 9:00
  workflow_dispatch:

jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - name: Check secret age
        run: |
          # 检查密钥创建时间
          echo "Secret audit report"
          echo "=================="
EOF
```

## 9. 合规性和审计

### 合规性检查
- [ ] 所有密钥都加密存储
- [ ] 生产密钥有访问限制
- [ ] 密钥轮换策略已实施
- [ ] 访问日志已启用
- [ ] 定期审计计划

### 审计日志
```bash
# 查看密钥访问日志
# 需要 GitHub Enterprise Cloud 或启用审计日志
```

## 10. 参考资料

- [GitHub Actions 密钥文档](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [环境密钥管理](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [安全最佳实践](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)