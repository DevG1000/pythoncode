# 测试部署指南

## 1. 测试部署概述

测试部署的目的是验证完整的 CI/CD 管道，包括：
- ✅ 代码质量检查
- ✅ 安全扫描
- ✅ 测试执行
- ✅ 构建过程
- ✅ 部署流程
- ✅ 质量门评估

## 2. 测试部署策略

### 测试环境
- **目标分支**: `develop` (测试环境)
- **部署环境**: `staging`
- **测试类型**: 完整端到端测试

### 测试数据
- 使用模拟数据
- 不连接真实数据库
- 使用测试 API 密钥
- 隔离的测试环境

## 3. 手动触发测试部署

### 使用 GitHub CLI
```bash
# 触发 CI/CD 管道
gh workflow run "CI/CD Pipeline" --ref develop

# 或使用工作流文件名称
gh workflow run ".github/workflows/ci-cd-integrated-final.yml" --ref develop

# 查看运行状态
gh run list --workflow="CI/CD Pipeline"

# 查看特定运行的日志
gh run view --log <RUN_ID>
```

### 使用 GitHub Web 界面
1. 访问: `https://github.com/OWNER/REPO/actions`
2. 点击 "CI/CD Pipeline" 工作流
3. 点击 "Run workflow"
4. 选择分支: `develop`
5. 点击 "Run workflow"

## 4. 测试部署步骤

### 步骤 1: 准备测试代码
```bash
# 创建测试分支
git checkout -b test/deployment-$(date +%Y%m%d) develop

# 创建测试更改
echo "# Test deployment $(date)" >> TEST_DEPLOYMENT.md
echo "This is a test deployment to verify CI/CD pipeline." >> TEST_DEPLOYMENT.md

# 提交更改
git add TEST_DEPLOYMENT.md
git commit -m "test: Add deployment test file"

# 推送到远程
git push origin test/deployment-$(date +%Y%m%d)
```

### 步骤 2: 创建测试 Pull Request
```bash
# 使用 GitHub CLI 创建 PR
gh pr create \
  --title "Test: CI/CD Pipeline Deployment" \
  --body "This PR tests the complete CI/CD pipeline with quality gates." \
  --base develop \
  --head test/deployment-$(date +%Y%m%d)

# 或通过 Web 界面
# 访问: https://github.com/OWNER/REPO/pull/new/test/deployment-...
```

### 步骤 3: 监控工作流执行

#### 预期工作流序列
1. **PR Quality Gates** (自动触发)
   - Code Quality Check
   - Security Scan
   - Test Coverage
   - Architecture Review
   - Performance Check

2. **CI/CD Pipeline** (手动或自动触发)
   - Security Audit
   - Lint and Format
   - Quality Gates Assessment
   - Unit Tests
   - Integration Tests
   - E2E Tests
   - Docker Build
   - Deploy to Staging
   - Smoke Tests

#### 监控命令
```bash
# 实时监控工作流
watch -n 10 'gh run list --workflow="CI/CD Pipeline" --limit=5'

# 检查特定作业状态
gh run view <RUN_ID> --job=<JOB_ID>

# 查看作业日志
gh run view <RUN_ID> --log --job=<JOB_ID>
```

## 5. 验证检查点

### 检查点 1: 质量门评估
```bash
# 检查质量门作业输出
gh run view <RUN_ID> --log --job=quality-gates-assessment

# 预期输出:
# ✅ SOLID Principles Check: Passed
# 📊 Code Complexity: Within acceptable limits
# 🔧 Maintainability Index: Good
# 🧪 Test Coverage: >80%
```

### 检查点 2: 测试结果
```bash
# 检查测试结果
gh run view <RUN_ID> --log --job=unit-tests
gh run view <RUN_ID> --log --job=integration-tests
gh run view <RUN_ID> --log --job=e2e-tests

# 下载测试报告
gh run download <RUN_ID> -n test-reports
```

### 检查点 3: 构建结果
```bash
# 检查 Docker 构建
gh run view <RUN_ID> --log --job=docker-build

# 检查构建产物
gh run download <RUN_ID> -n docker-image
```

### 检查点 4: 部署结果
```bash
# 检查部署作业
gh run view <RUN_ID> --log --job=deploy-staging

# 验证部署状态
curl -I https://staging.pythoncode.com/health
```

## 6. 自动化测试脚本

### 完整测试脚本
```bash
#!/bin/bash
# run-test-deployment.sh
set -e

echo "Starting test deployment..."
echo "=========================="

# 配置
BRANCH="test/deployment-$(date +%Y%m%d-%H%M%S)"
PR_TITLE="Test: CI/CD Pipeline Deployment $(date +%Y-%m-%d)"
PR_BODY="Automated test deployment to verify CI/CD pipeline functionality."

# 1. 创建测试分支
echo "1. Creating test branch: $BRANCH"
git checkout -b "$BRANCH" develop

# 2. 创建测试文件
echo "2. Creating test files..."
cat > TEST_DEPLOYMENT.md << EOF
# Test Deployment $(date)

This is an automated test deployment to verify:
- CI/CD pipeline execution
- Quality gates assessment
- Test execution
- Docker build process
- Staging deployment

## Test Details
- Branch: $BRANCH
- Timestamp: $(date -u)
- Purpose: Validate complete pipeline
EOF

# 3. 提交更改
echo "3. Committing changes..."
git add TEST_DEPLOYMENT.md
git commit -m "test: Automated deployment test $(date +%Y%m%d)"

# 4. 推送到远程
echo "4. Pushing to remote..."
git push origin "$BRANCH"

# 5. 创建 Pull Request
echo "5. Creating Pull Request..."
PR_URL=$(gh pr create \
  --title "$PR_TITLE" \
  --body "$PR_BODY" \
  --base develop \
  --head "$BRANCH" \
  --json url --jq '.url')

echo "PR created: $PR_URL"

# 6. 触发 CI/CD 管道
echo "6. Triggering CI/CD pipeline..."
WORKFLOW_RUN=$(gh workflow run "CI/CD Pipeline" \
  --ref "$BRANCH" \
  --json id --jq '.id')

echo "Workflow run ID: $WORKFLOW_RUN"

# 7. 监控执行
echo "7. Monitoring workflow execution..."
echo "Follow progress at: https://github.com/$(gh repo view --json nameWithOwner --jq '.nameWithOwner')/actions/runs/$WORKFLOW_RUN"

# 8. 等待完成
echo "8. Waiting for completion..."
while true; do
  STATUS=$(gh run view "$WORKFLOW_RUN" --json status --jq '.status')
  CONCLUSION=$(gh run view "$WORKFLOW_RUN" --json conclusion --jq '.conclusion')
  
  echo "Status: $STATUS, Conclusion: $CONCLUSION"
  
  if [[ "$STATUS" == "completed" ]]; then
    if [[ "$CONCLUSION" == "success" ]]; then
      echo "✅ Deployment test PASSED!"
      break
    else
      echo "❌ Deployment test FAILED!"
      gh run view "$WORKFLOW_RUN" --log
      exit 1
    fi
  fi
  
  sleep 30
done

# 9. 清理
echo "9. Cleaning up..."
read -p "Delete test branch? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  git checkout develop
  git branch -D "$BRANCH"
  git push origin --delete "$BRANCH"
  echo "Test branch deleted."
fi

echo "Test deployment completed successfully!"
```

### 简化测试脚本
```bash
#!/bin/bash
# quick-test.sh
set -e

echo "Quick CI/CD Pipeline Test"
echo "========================"

# 触发工作流
echo "Triggering workflow..."
RUN_ID=$(gh workflow run ".github/workflows/ci-cd-integrated-final.yml" \
  --ref develop \
  --json id --jq '.id')

echo "Workflow run: $RUN_ID"

# 监控进度
echo "Monitoring progress (Ctrl+C to stop)..."
while true; do
  STATUS=$(gh run view $RUN_ID --json status --jq '.status')
  echo "Status: $STATUS"
  
  if [[ "$STATUS" == "completed" ]]; then
    CONCLUSION=$(gh run view $RUN_ID --json conclusion --jq '.conclusion')
    echo "Conclusion: $CONCLUSION"
    
    if [[ "$CONCLUSION" == "success" ]]; then
      echo "✅ Test PASSED"
      exit 0
    else
      echo "❌ Test FAILED"
      gh run view $RUN_ID --log
      exit 1
    fi
  fi
  
  sleep 10
done
```

## 7. 测试验证清单

### 预部署检查
- [ ] 代码库是最新状态
- [ ] 测试分支已创建
- [ ] 测试更改已提交
- [ ] GitHub CLI 已认证
- [ ] 必要的密钥已设置

### 部署过程检查
- [ ] 工作流已触发
- [ ] 所有作业正在运行
- [ ] 质量门评估通过
- [ ] 测试全部通过
- [ ] Docker 构建成功
- [ ] 部署到 staging 成功

### 后部署检查
- [ ] 服务健康检查通过
- [ ] 日志无错误
- [ ] 性能指标正常
- [ ] 回滚功能测试
- [ ] 清理测试资源

## 8. 故障排除

### 常见问题

#### 问题 1: 工作流未触发
```bash
# 检查工作流文件
gh workflow list

# 检查触发器配置
cat .github/workflows/ci-cd-integrated-final.yml | head -20

# 手动触发
gh workflow run "CI/CD Pipeline" --ref develop
```

#### 问题 2: 作业失败
```bash
# 查看失败作业日志
gh run view <RUN_ID> --log --job=<FAILED_JOB>

# 常见失败原因:
# - 缺少密钥
# - 权限不足
# - 测试失败
# - 超时
```

#### 问题 3: 质量门失败
```bash
# 查看质量门评估详情
gh run view <RUN_ID> --log --job=quality-gates-assessment

# 检查阈值配置
cat scripts/quality_thresholds.yml

# 临时调整阈值进行测试
```

#### 问题 4: 部署失败
```bash
# 检查部署日志
gh run view <RUN_ID> --log --job=deploy-staging

# 验证环境配置
gh api /repos/OWNER/REPO/environments/staging

# 检查部署密钥
gh secret list --env staging
```

### 调试模式
在测试期间启用详细日志：
```yaml
# 在工作流中添加调试步骤
- name: Debug Information
  run: |
    echo "GITHUB_WORKFLOW: $GITHUB_WORKFLOW"
    echo "GITHUB_RUN_ID: $GITHUB_RUN_ID"
    echo "GITHUB_REF: $GITHUB_REF"
    echo "Secrets available:"
    echo "DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME != '' && 'SET' || 'NOT SET' }}"
```

## 9. 性能测试

### 基准测试
```bash
# 记录开始时间
START_TIME=$(date +%s)

# 运行测试部署
./run-test-deployment.sh

# 计算持续时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "Total deployment time: $DURATION seconds"

# 目标时间:
# - 完整管道: < 30 分钟
# - 质量门: < 10 分钟
# - 测试: < 15 分钟
# - 构建: < 5 分钟
# - 部署: < 5 分钟
```

### 资源使用监控
```bash
# 监控 GitHub Actions 使用
# 访问: https://github.com/OWNER/REPO/settings/actions

# 查看运行时间
gh run view <RUN_ID> --json databaseId,status,createdAt,updatedAt
```

## 10. 测试报告

### 生成测试报告
```bash
#!/bin/bash
# generate-test-report.sh
set -e

RUN_ID=$1
REPORT_FILE="test-report-$(date +%Y%m%d).md"

echo "# Test Deployment Report" > $REPORT_FILE
echo "## Run ID: $RUN_ID" >> $REPORT_FILE
echo "## Date: $(date)" >> $REPORT_FILE
echo "" >> $REPORT_FILE

# 获取工作流信息
echo "## Workflow Information" >> $REPORT_FILE
gh run view $RUN_ID --json name,status,conclusion,createdAt,updatedAt,headBranch,headSha \
  --jq '. | to_entries[] | "- \(.key): \(.value)"' >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "## Job Results" >> $REPORT_FILE

# 获取作业结果
gh run view $RUN_ID --json jobs --jq '.jobs[] | "### \(.name)\n- Status: \(.status)\n- Conclusion: \(.conclusion)\n- Duration: \(((.completedAt | fromdate) - (.startedAt | fromdate)) / 60) minutes"' >> $REPORT_FILE

echo "" >> $REPORT_FILE
echo "## Artifacts" >> $REPORT_FILE
gh run download $RUN_ID --dir artifacts
find artifacts -type f -name "*.json" -o -name "*.xml" -o -name "*.html" | \
  xargs -I {} echo "- {}" >> $REPORT_FILE

echo "Report generated: $REPORT_FILE"
```

### 报告模板
```markdown
# CI/CD 管道测试报告

## 测试概述
- **测试日期**: 2026-04-03
- **测试类型**: 完整端到端测试
- **目标环境**: staging
- **测试分支**: test/deployment-20260403

## 执行结果
| 组件 | 状态 | 持续时间 | 备注 |
|------|------|---------|------|
| 质量门评估 | ✅ 通过 | 8m 32s | SOLID 原则: 85% |
| 单元测试 | ✅ 通过 | 3m 15s | 覆盖率: 82% |
| 集成测试 | ✅ 通过 | 5m 48s | 所有测试通过 |
| Docker 构建 | ✅ 通过 | 2m 10s | 镜像大小: 245MB |
| 部署到 Staging | ✅ 通过 | 1m 45s | 健康检查通过 |

## 问题发现
1. 无重大问题发现
2. 性能在预期范围内
3. 所有检查点通过

## 建议
1. 考虑添加缓存优化构建时间
2. 监控生产环境资源使用
3. 定期运行性能测试

## 结论
✅ CI/CD 管道功能正常，可以投入生产使用。
```

## 11. 后续步骤

### 测试通过后
1. **合并测试分支**: 如果测试成功，可以合并到 develop
2. **更新文档**: 记录测试结果和经验
3. **优化配置**: 根据测试结果调整配置
4. **计划生产部署**: 安排正式的生产部署

### 测试失败后
1. **分析原因**: 查看日志，确定失败原因
2. **修复问题**: 修复代码、配置或工作流
3. **重新测试**: 修复后重新运行测试
4. **更新流程**: 如果发现流程问题，更新部署流程

## 12. 参考资料

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [工作流调试指南](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows)
- [部署最佳实践](https://docs.github.com/en/actions/deployment/about-deployments/deployment-protection-rules)