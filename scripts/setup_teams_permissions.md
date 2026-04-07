# GitHub 团队和权限配置指南

## 1. 团队结构设计

### 核心团队定义
根据 `.github/permissions.yml` 配置，需要创建以下团队：

| 团队名称 | 成员数量 | 主要职责 | 仓库权限 |
|---------|---------|---------|---------|
| `backend-team` | 8 | 后端开发 | Write |
| `frontend-team` | 6 | 前端开发 | Write |
| `devops-team` | 4 | DevOps 和基础设施 | Admin |
| `qa-team` | 5 | 质量保证 | Read |
| `security-team` | 3 | 安全审查 | Read |
| `team-leads` | 4 | 团队领导和技术管理 | Maintain |

### 个人角色
| 角色 | 权限级别 | 职责 |
|------|---------|------|
| `cto` | Admin | 首席技术官 |
| `head-of-engineering` | Admin | 工程负责人 |
| `head-of-security` | Maintain | 安全负责人 |
| `deployment-manager` | Write | 部署经理 |

## 2. 创建团队 (GitHub 组织)

### 使用 GitHub Web 界面
1. **访问组织设置**
   - 打开: `https://github.com/organizations/ORG-NAME/teams`
   - 点击 "New team"

2. **创建每个团队**
   - **团队名称**: `backend-team`
   - **描述**: `Backend development team`
   - **隐私**: `Visible` (或 `Secret` 如果需要)
   - **父团队**: (可选) 选择父团队
   - 点击 "Create team"

3. **重复创建所有团队**
   - `frontend-team`
   - `devops-team`
   - `qa-team`
   - `security-team`
   - `team-leads`

### 使用 GitHub CLI
```bash
# 设置变量
ORG="your-organization-name"

# 创建团队
gh api --method POST /orgs/$ORG/teams \
  -f '{"name":"backend-team","description":"Backend development team","privacy":"closed"}'

gh api --method POST /orgs/$ORG/teams \
  -f '{"name":"frontend-team","description":"Frontend development team","privacy":"closed"}'

gh api --method POST /orgs/$ORG/teams \
  -f '{"name":"devops-team","description":"DevOps and infrastructure team","privacy":"closed"}'

gh api --method POST /orgs/$ORG/teams \
  -f '{"name":"qa-team","description":"Quality assurance team","privacy":"closed"}'

gh api --method POST /orgs/$ORG/teams \
  -f '{"name":"security-team","description":"Security team","privacy":"closed"}'

gh api --method POST /orgs/$ORG/teams \
  -f '{"name":"team-leads","description":"Team leads and managers","privacy":"closed"}'
```

## 3. 添加团队成员

### 添加成员到团队
```bash
# 添加用户到团队
gh api --method PUT /orgs/$ORG/teams/backend-team/memberships/USERNAME \
  -f '{"role":"member"}'

# 添加团队维护者
gh api --method PUT /orgs/$ORG/teams/backend-team/memberships/USERNAME \
  -f '{"role":"maintainer"}'

# 批量添加脚本
#!/bin/bash
set -e

ORG="your-organization"
TEAM="backend-team"

# 成员列表
MEMBERS=("alice" "bob" "charlie" "david" "eve" "frank" "grace" "henry")

for member in "${MEMBERS[@]}"; do
  echo "Adding $member to $TEAM..."
  gh api --method PUT /orgs/$ORG/teams/$TEAM/memberships/$member \
    -f '{"role":"member"}' || echo "Failed to add $member"
done
```

### 使用 Web 界面添加成员
1. 访问团队页面: `https://github.com/orgs/ORG-NAME/teams/TEAM-NAME`
2. 点击 "Add a member"
3. 输入用户名或邮箱
4. 选择角色: `Member` 或 `Maintainer`
5. 点击 "Add"

## 4. 设置仓库权限

### 为团队设置仓库权限
```bash
# 设置变量
ORG="your-organization"
REPO="pythoncode"

# 设置团队权限
# backend-team: Write 权限
gh api --method PUT /orgs/$ORG/teams/backend-team/repos/$ORG/$REPO \
  -f '{"permission":"write"}'

# frontend-team: Write 权限
gh api --method PUT /orgs/$ORG/teams/frontend-team/repos/$ORG/$REPO \
  -f '{"permission":"write"}'

# devops-team: Admin 权限
gh api --method PUT /orgs/$ORG/teams/devops-team/repos/$ORG/$REPO \
  -f '{"permission":"admin"}'

# qa-team: Read 权限
gh api --method PUT /orgs/$ORG/teams/qa-team/repos/$ORG/$REPO \
  -f '{"permission":"read"}'

# security-team: Read 权限
gh api --method PUT /orgs/$ORG/teams/security-team/repos/$ORG/$REPO \
  -f '{"permission":"read"}'

# team-leads: Maintain 权限
gh api --method PUT /orgs/$ORG/teams/team-leads/repos/$ORG/$REPO \
  -f '{"permission":"maintain"}'
```

### 权限级别说明
| 权限级别 | 描述 | 适用团队 |
|---------|------|---------|
| `Read` | 查看代码，不能推送 | qa-team, security-team |
| `Write` | 推送代码，创建分支 | backend-team, frontend-team |
| `Maintain` | 管理仓库设置 | team-leads |
| `Admin` | 完全控制 | devops-team |

## 5. 环境权限配置

### 设置环境部署权限
```bash
# 创建或更新环境
# Staging 环境
gh api --method PUT /repos/$ORG/$REPO/environments/staging \
  -f '{
    "wait_timer": 0,
    "reviewers": [
      {"type": "Team", "id": TEAM_ID_FOR_TEAM_LEADS},
      {"type": "Team", "id": TEAM_ID_FOR_QA_TEAM}
    ],
    "deployment_branch_policy": {
      "protected_branches": false,
      "custom_branch_policies": true
    }
  }'

# Production 环境
gh api --method PUT /repos/$ORG/$REPO/environments/production \
  -f '{
    "wait_timer": 30,
    "reviewers": [
      {"type": "Team", "id": TEAM_ID_FOR_TEAM_LEADS},
      {"type": "Team", "id": TEAM_ID_FOR_SECURITY_TEAM},
      {"type": "User", "id": USER_ID_FOR_CTO}
    ],
    "deployment_branch_policy": {
      "protected_branches": true,
      "custom_branch_policies": false
    }
  }'
```

### 获取团队 ID
```bash
# 获取团队 ID
gh api /orgs/$ORG/teams | jq '.[] | select(.name=="team-leads") | .id'

# 获取用户 ID
gh api /users/USERNAME | jq '.id'
```

## 6. 分支保护集成

### 配置代码所有者 (CODEOWNERS)
创建 `.github/CODEOWNERS` 文件：
```
# 后端代码
/api/ @org/backend-team
/command_system/ @org/backend-team

# 前端代码
/web/ @org/frontend-team
/static/ @org/frontend-team

# 配置和部署
/.github/ @org/devops-team
/docker/ @org/devops-team
/kubernetes/ @org/devops-team

# 安全相关
/security/ @org/security-team

# 所有文件 (后备)
* @org/team-leads
```

### 启用代码所有者审查
在分支保护规则中启用：
```json
{
  "required_pull_request_reviews": {
    "required_approving_review_count": 2,
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": true,
    "require_last_push_approval": false
  }
}
```

## 7. 工作流权限配置

### 工作流权限设置
在 `ci-cd-integrated-final.yml` 中：
```yaml
permissions:
  contents: read
  packages: write
  deployments: write
  checks: write
  pull-requests: write
  actions: read
  issues: read
```

### 环境特定的权限
```yaml
# 生产部署作业
deploy-production:
  environment: production
  permissions:
    contents: read
    deployments: write
    id-token: write  # 用于 OIDC
```

## 8. 访问控制策略

### 基于角色的访问控制 (RBAC)
| 角色 | 仓库访问 | 环境部署 | 分支管理 | 密钥访问 |
|------|---------|---------|---------|---------|
| 开发者 | Write | Staging | 功能分支 | 有限 |
| 质量保证 | Read | Staging | 只读 | 有限 |
| 安全专家 | Read | 审批生产 | 只读 | 有限 |
| 团队领导 | Maintain | 审批所有 | 所有分支 | 读 |
| DevOps | Admin | 所有环境 | 所有分支 | 写 |
| CTO | Admin | 所有环境 | 所有分支 | 写 |

### 紧急访问流程
1. **紧急情况**: 安全漏洞、服务中断、数据损坏
2. **审批要求**: CTO + 安全负责人
3. **时间限制**: 4小时
4. **事后审查**: 必须进行

## 9. 审计和合规

### 启用审计日志
```bash
# 查看团队活动
gh api /orgs/$ORG/audit-log

# 查看团队仓库访问
gh api /orgs/$ORG/teams/TEAM-NAME/repos
```

### 合规性检查清单
- [ ] 所有团队都有明确职责
- [ ] 权限遵循最小特权原则
- [ ] 代码所有者审查已启用
- [ ] 环境部署需要审批
- [ ] 定期权限审查计划
- [ ] 审计日志已启用

## 10. 自动化管理脚本

### 完整设置脚本
```bash
#!/bin/bash
# setup-teams-permissions.sh
set -e

ORG="your-organization"
REPO="pythoncode"

echo "Setting up teams and permissions for $ORG/$REPO"

# 1. 创建团队
teams=(
  "backend-team:Backend development team"
  "frontend-team:Frontend development team"
  "devops-team:DevOps and infrastructure team"
  "qa-team:Quality assurance team"
  "security-team:Security team"
  "team-leads:Team leads and managers"
)

for team_info in "${teams[@]}"; do
  IFS=':' read -r name description <<< "$team_info"
  echo "Creating team: $name"
  gh api --method POST /orgs/$ORG/teams \
    -f "{\"name\":\"$name\",\"description\":\"$description\",\"privacy\":\"closed\"}" || true
done

# 2. 设置仓库权限
echo "Setting repository permissions..."
gh api --method PUT /orgs/$ORG/teams/backend-team/repos/$ORG/$REPO -f '{"permission":"write"}'
gh api --method PUT /orgs/$ORG/teams/frontend-team/repos/$ORG/$REPO -f '{"permission":"write"}'
gh api --method PUT /orgs/$ORG/teams/devops-team/repos/$ORG/$REPO -f '{"permission":"admin"}'
gh api --method PUT /orgs/$ORG/teams/qa-team/repos/$ORG/$REPO -f '{"permission":"read"}'
gh api --method PUT /orgs/$ORG/teams/security-team/repos/$ORG/$REPO -f '{"permission":"read"}'
gh api --method PUT /orgs/$ORG/teams/team-leads/repos/$ORG/$REPO -f '{"permission":"maintain"}'

# 3. 创建 CODEOWNERS 文件
echo "Creating CODEOWNERS file..."
cat > .github/CODEOWNERS << 'EOF'
# 后端代码
/api/ @$ORG/backend-team
/command_system/ @$ORG/backend-team

# 前端代码
/web/ @$ORG/frontend-team
/static/ @$ORG/frontend-team

# 配置和部署
/.github/ @$ORG/devops-team
/docker/ @$ORG/devops-team

# 安全相关
/security/ @$ORG/security-team

# 所有文件
* @$ORG/team-leads
EOF

echo "Setup completed!"
```

### 权限验证脚本
```bash
#!/bin/bash
# verify-permissions.sh
set -e

ORG="your-organization"
REPO="pythoncode"

echo "Verifying permissions for $ORG/$REPO"

# 检查团队权限
echo "Team permissions:"
gh api /orgs/$ORG/teams | jq -r '.[] | "\(.name): \(.permission // "no access")"'

# 检查环境设置
echo -e "\nEnvironment settings:"
gh api /repos/$ORG/$REPO/environments | jq -r '.[].name'

# 检查分支保护
echo -e "\nBranch protection:"
gh api /repos/$ORG/$REPO/branches/main/protection | jq '.required_status_checks.contexts'
```

## 11. 故障排除

### 常见问题

1. **"Resource not accessible by integration"**
   ```bash
   # 检查组织权限
   gh auth status
   # 可能需要组织所有者权限
   ```

2. **团队创建失败**
   ```bash
   # 检查团队是否已存在
   gh api /orgs/$ORG/teams | jq '.[].name'
   
   # 更新现有团队
   gh api --method PATCH /orgs/$ORG/teams/TEAM-NAME \
     -f '{"description":"New description"}'
   ```

3. **权限不生效**
   ```bash
   # 清除缓存
   # 等待 GitHub 同步 (最多 5 分钟)
   
   # 直接测试权限
   gh api /repos/$ORG/$REPO/collaborators/USERNAME/permission
   ```

4. **环境审批不工作**
   ```bash
   # 检查环境配置
   gh api /repos/$ORG/$REPO/environments/production
   
   # 检查审批者 ID
   gh api /orgs/$ORG/teams/team-leads | jq '.id'
   ```

### 测试权限
```bash
# 测试推送权限
git clone https://github.com/$ORG/$REPO.git
cd $REPO
echo "test" > test.txt
git add test.txt
git commit -m "Test permission"
git push origin main  # 应该失败 (受保护分支)
git push origin feature/test  # 应该成功 (如果有权限)
```

## 12. 维护和更新

### 定期审查
- **每月**: 审查团队成员
- **每季度**: 审查权限设置
- **每半年**: 审查安全策略
- **每年**: 全面审计

### 权限更新流程
1. **请求**: 团队成员提交权限请求
2. **审批**: 团队领导审批
3. **实施**: DevOps 团队实施
4. **验证**: 请求者验证权限
5. **记录**: 更新权限文档

### 离职流程
1. **通知**: HR 通知 DevOps 团队
2. **撤销**: 从所有团队移除
3. **审查**: 审查其访问记录
4. **更新**: 更新相关密钥
5. **确认**: 确认权限已撤销

## 13. 参考资料

- [GitHub Teams 文档](https://docs.github.com/en/organizations/organizing-members-into-teams)
- [仓库权限管理](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/managing-repository-settings/managing-teams-and-people-with-access-to-your-repository)
- [环境部署权限](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
- [CODEOWNERS 文件](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners)