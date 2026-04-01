# 生产环境部署指南

## 概述

本文档提供PythonCode项目的生产环境部署指南，包括安全配置、监控设置和运维最佳实践。

## 1. 环境要求

### 1.1 系统要求
- **操作系统**: Ubuntu 20.04 LTS 或更高版本
- **内存**: 至少 4GB RAM
- **存储**: 至少 20GB 可用空间
- **CPU**: 至少 2核

### 1.2 软件要求
- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **Python**: 3.9 或更高版本（仅用于管理脚本）
- **OpenSSL**: 用于证书生成

## 2. 快速开始

### 2.1 克隆项目
```bash
git clone <repository-url>
cd pythoncode
```

### 2.2 设置生产环境
```bash
# 运行生产环境设置脚本
python scripts/setup_production.py

# 或者手动设置
cp .env.production.example .env.production
# 编辑 .env.production 文件，设置所有必要的环境变量
```

### 2.3 启动服务
```bash
# 使用Docker Compose启动所有服务
docker-compose -f config/docker-compose.production.yml up -d

# 查看服务状态
docker-compose -f config/docker-compose.production.yml ps

# 查看日志
docker-compose -f config/docker-compose.production.yml logs -f api
```

## 3. 详细配置

### 3.1 环境变量配置

编辑 `.env.production` 文件，设置以下关键变量：

```bash
# 应用配置
FLASK_ENV=production
SECRET_KEY=<生成的安全密钥>

# 数据库配置
DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
POSTGRES_DB=pythoncode
POSTGRES_USER=pythoncode
POSTGRES_PASSWORD=<生成的数据库密码>

# Redis配置
REDIS_PASSWORD=<生成的Redis密码>

# 邮件配置
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# 监控配置
GRAFANA_PASSWORD=<生成的Grafana密码>
SECURITY_ALERT_EMAIL=security@example.com
```

### 3.2 SSL证书配置

#### 选项1: 使用自签名证书（仅测试环境）
```bash
# 脚本已自动生成自签名证书
# 证书位置: config/nginx/ssl/
```

#### 选项2: 使用Let's Encrypt（生产环境推荐）
```bash
# 安装Certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 证书位置: /etc/letsencrypt/live/your-domain.com/
# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem config/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem config/nginx/ssl/key.pem
sudo chmod 600 config/nginx/ssl/key.pem
```

### 3.3 防火墙配置
```bash
# 启用防火墙
sudo ufw enable

# 允许必要端口
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP (重定向到HTTPS)
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 3000/tcp    # Grafana (可选，建议限制IP)

# 查看防火墙状态
sudo ufw status
```

## 4. 服务说明

### 4.1 主要服务
- **api**: 主应用服务 (端口: 5000)
- **nginx**: 反向代理和SSL终止 (端口: 80, 443)
- **postgres**: PostgreSQL数据库 (端口: 5432)
- **redis**: Redis缓存 (端口: 6379)

### 4.2 监控服务
- **monitoring**: Grafana监控面板 (端口: 3000)
- **security-monitor**: 安全监控服务
- **logstash**: 日志收集服务

## 5. 监控和日志

### 5.1 访问监控面板
1. 访问: `http://your-server-ip:3000`
2. 用户名: `admin`
3. 密码: 查看 `.env.production` 中的 `GRAFANA_PASSWORD`

### 5.2 查看日志
```bash
# 查看应用日志
docker-compose -f config/docker-compose.production.yml logs api

# 查看Nginx访问日志
tail -f logs/nginx/access.log

# 查看Nginx错误日志
tail -f logs/nginx/error.log

# 查看安全监控日志
docker-compose -f config/docker-compose.production.yml logs security-monitor
```

### 5.3 健康检查
```bash
# API健康检查
curl -f https://your-domain.com/api/health

# 数据库健康检查
docker-compose -f config/docker-compose.production.yml exec postgres pg_isready

# Redis健康检查
docker-compose -f config/docker-compose.production.yml exec redis redis-cli ping
```

## 6. 安全配置

### 6.1 定期安全审计
```bash
# 手动运行安全审计
python scripts/security_audit_simple.py

# 自动安全监控已集成在CI/CD中
# 查看 .github/workflows/scheduled-tests.yml
```

### 6.2 安全加固建议
1. **定期更新密码**: 每月更新所有服务密码
2. **限制访问**: 使用防火墙限制非必要端口
3. **启用2FA**: 为管理账户启用双因素认证
4. **定期备份**: 配置数据库和文件备份
5. **安全扫描**: 定期运行漏洞扫描

### 6.3 备份配置
```bash
# 数据库备份脚本
#!/bin/bash
BACKUP_DIR="/backups/database"
DATE=$(date +%Y%m%d_%H%M%S)

docker-compose -f config/docker-compose.production.yml exec postgres \
  pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > ${BACKUP_DIR}/backup_${DATE}.sql

# 保留最近7天的备份
find ${BACKUP_DIR} -name "*.sql" -mtime +7 -delete
```

## 7. 维护操作

### 7.1 更新应用
```bash
# 拉取最新代码
git pull origin main

# 重建并重启服务
docker-compose -f config/docker-compose.production.yml down
docker-compose -f config/docker-compose.production.yml up -d --build

# 运行数据库迁移（如果需要）
docker-compose -f config/docker-compose.production.yml exec api \
  python manage.py db upgrade
```

### 7.2 服务管理
```bash
# 启动所有服务
docker-compose -f config/docker-compose.production.yml up -d

# 停止所有服务
docker-compose -f config/docker-compose.production.yml down

# 重启单个服务
docker-compose -f config/docker-compose.production.yml restart api

# 查看服务状态
docker-compose -f config/docker-compose.production.yml ps

# 查看服务资源使用
docker stats
```

### 7.3 清理操作
```bash
# 清理未使用的Docker资源
docker system prune -f

# 清理日志文件（保留最近30天）
find logs -name "*.log" -mtime +30 -delete

# 清理上传的临时文件（保留最近7天）
find uploads -type f -mtime +7 -delete
```

## 8. 故障排除

### 8.1 常见问题

#### 问题1: 服务启动失败
```bash
# 查看详细错误信息
docker-compose -f config/docker-compose.production.yml logs

# 检查端口冲突
netstat -tulpn | grep :80
netstat -tulpn | grep :443
```

#### 问题2: 数据库连接失败
```bash
# 检查数据库服务状态
docker-compose -f config/docker-compose.production.yml ps postgres

# 检查数据库日志
docker-compose -f config/docker-compose.production.yml logs postgres

# 测试数据库连接
docker-compose -f config/docker-compose.production.yml exec postgres \
  psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c "SELECT 1;"
```

#### 问题3: SSL证书问题
```bash
# 检查证书文件
ls -la config/nginx/ssl/

# 测试SSL连接
openssl s_client -connect your-domain.com:443

# 重新生成自签名证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout config/nginx/ssl/key.pem \
  -out config/nginx/ssl/cert.pem \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"
```

### 8.2 性能优化

#### 调整Docker资源限制
```yaml
# 在docker-compose.production.yml中添加资源限制
services:
  api:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

#### 优化数据库性能
```sql
-- 创建性能优化索引
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at DESC);

-- 定期清理旧数据
DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days';
```

## 9. 扩展部署

### 9.1 多服务器部署
对于高可用性需求，建议使用以下架构：
- **负载均衡器**: Nginx或HAProxy
- **应用服务器**: 2+个API实例
- **数据库**: PostgreSQL主从复制
- **缓存**: Redis集群
- **存储**: 共享存储或对象存储

### 9.2 Kubernetes部署
项目包含Kubernetes配置示例：
```bash
# 部署到Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

## 10. 支持

### 10.1 获取帮助
- **文档**: 查看 `docs/` 目录
- **问题**: 提交GitHub Issue
- **安全报告**: 查看 `SECURITY.md`

### 10.2 紧急联系人
- **运维团队**: ops@example.com
- **安全团队**: security@example.com
- **技术支持**: support@example.com

---

**最后更新**: 2026-03-16  
**版本**: 1.0.0  
**维护者**: PythonCode团队