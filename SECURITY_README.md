# 安全配置指南

## 重要安全注意事项

### 1. 环境变量管理
- 所有敏感信息必须通过环境变量设置
- 不要将密钥、密码等硬编码在代码中
- 使用不同的密钥用于开发、测试和生产环境

### 2. 生产环境配置
- 设置 `FLASK_ENV=production`
- 设置 `FLASK_DEBUG=0`
- 启用HTTPS和安全的Cookie设置
- 配置适当的CORS策略

### 3. 数据库安全
- 生产环境使用PostgreSQL或MySQL
- 启用SSL/TLS加密连接
- 定期备份数据库
- 使用强密码和最小权限原则

### 4. 密钥管理
- 使用强随机密钥：`openssl rand -hex 32`
- 定期轮换密钥（建议每90天）
- 使用密钥管理服务（如AWS KMS、Hashicorp Vault）

### 5. 监控和日志
- 启用安全日志记录
- 监控异常登录尝试
- 设置告警规则
- 定期审计日志

### 6. 依赖安全
- 定期更新依赖包
- 使用安全漏洞扫描工具
- 固定依赖版本

## 快速安全检查

运行安全检查脚本：
```bash
python scripts/simple_security_check.py
```

## 紧急联系人

- 安全负责人: security@example.com
- 系统管理员: admin@example.com

## 安全策略

请参考 `docs/SECURITY_REQUIREMENTS.md` 获取完整的安全策略。
