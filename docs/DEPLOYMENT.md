# 快速部署指南

## 一分钟快速开始

### 使用Docker Compose（最简单）

```bash
# 1. 克隆项目（如果尚未克隆）
git clone <repository-url>
cd pythoncode

# 2. 配置环境变量（可选）
cp .env.example .env
# 编辑.env文件，配置邮箱等参数

# 3. 一键启动
docker-compose up -d

# 4. 访问服务
# API服务: http://localhost:5000
# 健康检查: http://localhost:5000/api/health
```

### 使用Docker直接运行

```bash
# 1. 构建镜像
docker build -t pythoncode:latest .

# 2. 运行容器
docker run -d \
  --name pythoncode-app \
  -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/logs:/app/logs \
  pythoncode:latest

# 3. 查看状态
docker ps
docker logs pythoncode-app
```

## 部署选项

### 选项1：基础部署（仅API）
```bash
docker-compose up -d api
```

### 选项2：完整部署（API + 数据库 + 缓存）
```bash
docker-compose up -d api postgres redis
```

### 选项3：生产部署（带Nginx反向代理）
```bash
# 1. 生成SSL证书
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Company/OU=IT/CN=localhost"

# 2. 启动所有服务
docker-compose up -d
```

## 常用命令

### 服务管理
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

### 容器管理
```bash
# 进入容器
docker-compose exec api bash

# 执行命令
docker-compose exec api python cmd_agent.py interactive

# 备份数据库
docker-compose exec api cp /app/instance/users.db /app/backup/
```

### 监控和维护
```bash
# 健康检查
curl http://localhost:5000/api/health

# 性能监控
curl http://localhost:5000/api/performance

# 内存优化
curl -X POST http://localhost:5000/api/memory/optimize
```

## 环境配置

### 必需配置
```env
# .env文件
SECRET_KEY=your-secret-key-change-in-production
```

### 推荐配置
```env
# 邮箱配置（用于用户注册验证）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# 数据库配置（可选，默认使用SQLite）
# DATABASE_URL=postgresql://pythoncode:password@postgres:5432/pythoncode
```

## 故障排除

### 常见问题

**Q: 容器启动失败**
```bash
# 查看详细日志
docker-compose logs api

# 检查端口占用
netstat -tulpn | grep :5000
```

**Q: 数据库连接失败**
```bash
# 检查数据库服务
docker-compose ps postgres

# 重置数据库
docker-compose down -v
docker-compose up -d
```

**Q: 内存不足**
```bash
# 查看内存使用
docker stats

# 清理未使用资源
docker system prune -f
```

### 获取帮助
```bash
# 查看完整文档
cat README_DOCKER.md

# 查看Dockerfile
cat Dockerfile

# 查看docker-compose配置
cat docker-compose.yml
```

## 下一步

1. **配置邮箱**：编辑.env文件配置邮件服务
2. **设置域名**：配置Nginx反向代理和SSL证书
3. **数据备份**：设置定期数据库备份
4. **监控告警**：配置容器监控和告警

---

**提示**: 生产环境部署前，请务必：
1. 修改SECRET_KEY
2. 配置有效的邮箱服务
3. 启用HTTPS
4. 设置数据备份策略