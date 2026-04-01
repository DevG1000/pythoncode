# Docker容器化部署指南

## 概述

本文档提供了Python项目的Docker容器化部署方案。通过Docker，您可以轻松地在任何支持Docker的环境中部署和运行本项目。

## 项目架构

```
┌─────────────────────────────────────────────┐
│                 Docker容器架构                │
├─────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐        │
│  │   Nginx     │◄───┤   用户      │        │
│  │ (反向代理)   │    │   (浏览器)  │        │
│  └─────────────┘    └─────────────┘        │
│         │                                   │
│         ▼                                   │
│  ┌─────────────┐    ┌─────────────┐        │
│  │ Flask API   │    │ CMD Agent   │        │
│  │  容器       │    │  容器       │        │
│  └─────────────┘    └─────────────┘        │
│         │                                   │
│         ▼                                   │
│  ┌─────────────┐    ┌─────────────┐        │
│  │ PostgreSQL  │    │   Redis     │        │
│  │  数据库     │    │   缓存      │        │
│  └─────────────┘    └─────────────┘        │
└─────────────────────────────────────────────┘
```

## 快速开始

### 前提条件

1. **Docker** 版本 20.10+
2. **Docker Compose** 版本 2.0+
3. **Git**（可选，用于克隆代码）

### 一键部署

```bash
# 克隆项目（如果尚未克隆）
git clone <repository-url>
cd pythoncode

# 使用docker-compose一键部署
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f api
```

### 访问服务

部署完成后，可以通过以下地址访问服务：

- **API服务**: http://localhost:5000
- **Nginx代理**: http://localhost:80 (自动重定向到HTTPS)
- **健康检查**: http://localhost:5000/api/health

## 详细部署步骤

### 1. 环境准备

#### 1.1 安装Docker和Docker Compose

**Linux (Ubuntu/Debian):**
```bash
# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**Windows:**
- 下载并安装 [Docker Desktop](https://www.docker.com/products/docker-desktop)
- Docker Desktop已包含Docker Compose

**macOS:**
```bash
# 使用Homebrew安装
brew install docker docker-compose
```

#### 1.2 配置环境变量

复制环境变量模板并配置：

```bash
# 复制模板文件
cp .env.example .env

# 编辑环境变量
# Windows: 使用记事本或编辑器打开.env文件
# Linux/macOS: nano .env 或 vim .env
```

主要配置项：
```env
# 应用配置
SECRET_KEY=your-secret-key-change-in-production
APP_NAME=PythonCode

# 数据库配置
DATABASE_URL=sqlite:///instance/users.db
# 如果使用PostgreSQL:
# DATABASE_URL=postgresql://pythoncode:password@postgres:5432/pythoncode

# 邮件配置（用于用户注册验证）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# CMD Agent配置
CMD_MAX_WORKERS=7
CMD_TIMEOUT=15
```

### 2. 构建Docker镜像

#### 2.1 使用构建脚本

**Linux/macOS:**
```bash
# 赋予执行权限
chmod +x build-docker.sh
chmod +x docker-run.sh

# 构建镜像
./build-docker.sh

# 或使用详细选项
./build-docker.sh --name pythoncode --tag v1.0 --test
```

**Windows:**
```bash
# 使用批处理脚本
build-docker.bat

# 或使用详细选项
build-docker.bat -n pythoncode -t v1.0 --test
```

#### 2.2 手动构建
```bash
# 构建镜像
docker build -t pythoncode:latest .

# 查看构建的镜像
docker images | grep pythoncode
```

### 3. 运行容器

#### 3.1 使用docker-compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 启动特定服务
docker-compose up -d api
docker-compose up -d api cmd-agent

# 查看运行状态
docker-compose ps

# 查看日志
docker-compose logs -f api
docker-compose logs -f cmd-agent

# 停止服务
docker-compose down

# 停止并清理数据
docker-compose down -v
```

#### 3.2 使用运行脚本

**Linux/macOS:**
```bash
# 运行API容器
./docker-run.sh run -p 5000:5000

# 运行CMD Agent交互模式
./docker-run.sh run -n pythoncode-cmd -it --command "python cmd_agent.py interactive"

# 查看容器状态
./docker-run.sh ps

# 进入容器shell
./docker-run.sh shell

# 清理所有容器
./docker-run.sh clean
```

**Windows:**
```bash
# 直接使用docker命令
docker run -p 5000:5000 pythoncode:latest
```

#### 3.3 手动运行

```bash
# 运行API服务
docker run -d \
  --name pythoncode-api \
  -p 5000:5000 \
  -v $(pwd)/instance:/app/instance \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  -e FLASK_ENV=production \
  pythoncode:latest

# 运行CMD Agent
docker run -it \
  --name pythoncode-cmd \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/data:/app/data \
  pythoncode:latest \
  python cmd_agent.py interactive

# 运行名片生成器
docker run \
  --name pythoncode-card \
  -v $(pwd)/input.xlsx:/app/input.xlsx:ro \
  -v $(pwd)/output.xlsx:/app/output.xlsx \
  pythoncode:latest \
  python Line2Card.py
```

### 4. 服务配置

#### 4.1 多服务配置

docker-compose.yml支持多种服务配置：

```yaml
# 基本API服务
docker-compose up -d api

# API + 数据库
docker-compose up -d api postgres

# 完整服务栈
docker-compose up -d api postgres redis nginx
```

#### 4.2 自定义配置

创建自定义docker-compose文件：

```yaml
# docker-compose.override.yml
version: '3.8'

services:
  api:
    environment:
      - CMD_MAX_WORKERS=10
      - CMD_TIMEOUT=30
    ports:
      - "8080:5000"
    volumes:
      - ./custom-config:/app/config:ro
```

使用自定义配置：
```bash
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d
```

### 5. 数据管理

#### 5.1 数据持久化

项目使用以下卷进行数据持久化：

- `./instance` - SQLite数据库文件
- `./logs` - 应用日志文件
- `./data` - 用户数据文件
- `postgres-data` - PostgreSQL数据卷（如果使用）
- `redis-data` - Redis数据卷（如果使用）

#### 5.2 备份和恢复

**备份数据库：**
```bash
# SQLite备份
docker exec pythoncode-api cp /app/instance/users.db /app/backup/users.db.backup

# PostgreSQL备份
docker exec pythoncode-postgres pg_dump -U pythoncode pythoncode > backup.sql
```

**恢复数据库：**
```bash
# SQLite恢复
docker cp backup/users.db pythoncode-api:/app/instance/users.db

# PostgreSQL恢复
docker exec -i pythoncode-postgres psql -U pythoncode pythoncode < backup.sql
```

### 6. 监控和维护

#### 6.1 健康检查

```bash
# 检查API健康状态
curl http://localhost:5000/api/health

# 检查容器健康状态
docker inspect --format='{{.State.Health.Status}}' pythoncode-api
```

#### 6.2 日志管理

```bash
# 查看实时日志
docker-compose logs -f api

# 查看特定时间段的日志
docker-compose logs --since="2024-01-15" --until="2024-01-16" api

# 导出日志
docker-compose logs api > api.log

# 清理旧日志
docker-compose exec api python -c "from memory_manager import optimize_memory; optimize_memory()"
```

#### 6.3 性能监控

```bash
# 查看容器资源使用
docker stats pythoncode-api

# 查看系统性能信息
curl http://localhost:5000/api/performance

# 查看内存信息
curl http://localhost:5000/api/memory/info

# 手动触发内存优化
curl -X POST http://localhost:5000/api/memory/optimize
```

### 7. 安全配置

#### 7.1 使用HTTPS

1. 生成SSL证书：
```bash
mkdir -p nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=Company/OU=IT/CN=localhost"
```

2. 更新docker-compose.yml中的Nginx配置

#### 7.2 网络隔离

```yaml
# 创建自定义网络
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # 内部网络，外部无法访问

services:
  nginx:
    networks:
      - frontend
      
  api:
    networks:
      - frontend
      - backend
      
  postgres:
    networks:
      - backend  # 数据库只在内部网络
```

#### 7.3 用户权限

Dockerfile已配置非root用户运行：
```dockerfile
# 创建非root用户
RUN useradd -m -u 1000 appuser
USER appuser
```

### 8. 扩展部署

#### 8.1 多节点部署

创建docker-compose.stack.yml用于Swarm部署：

```yaml
version: '3.8'

services:
  api:
    image: pythoncode:latest
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
      placement:
        constraints:
          - node.role == worker
    networks:
      - pythoncode-network
```

部署到Swarm集群：
```bash
# 初始化Swarm
docker swarm init

# 部署服务栈
docker stack deploy -c docker-compose.stack.yml pythoncode

# 查看服务状态
docker service ls
```

#### 8.2 Kubernetes部署

创建Kubernetes部署文件：

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pythoncode-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: pythoncode-api
  template:
    metadata:
      labels:
        app: pythoncode-api
    spec:
      containers:
      - name: api
        image: pythoncode:latest
        ports:
        - containerPort: 5000
        env:
        - name: FLASK_ENV
          value: "production"
```

### 9. 故障排除

#### 9.1 常见问题

**问题1: 容器启动失败**
```bash
# 查看详细错误信息
docker-compose logs api

# 检查端口占用
netstat -tulpn | grep :5000

# 重新构建镜像
docker-compose build --no-cache api
```

**问题2: 数据库连接失败**
```bash
# 检查数据库容器状态
docker-compose ps postgres

# 检查数据库日志
docker-compose logs postgres

# 测试数据库连接
docker-compose exec api python -c "from config import Config; print(Config.SQLALCHEMY_DATABASE_URI)"
```

**问题3: 内存不足**
```bash
# 查看内存使用
docker stats

# 优化内存
curl -X POST http://localhost:5000/api/memory/optimize

# 调整容器内存限制
docker-compose.yml中配置：
api:
  deploy:
    resources:
      limits:
        memory: 512M
```

#### 9.2 调试技巧

```bash
# 进入容器调试
docker-compose exec api bash

# 查看环境变量
docker-compose exec api env

# 查看文件系统
docker-compose exec api ls -la /app

# 运行Python调试
docker-compose exec api python -c "import sys; print(sys.path)"
```

### 10. 最佳实践

#### 10.1 生产环境建议

1. **使用环境变量**：所有敏感配置通过环境变量传递
2. **启用HTTPS**：使用有效的SSL证书
3. **配置备份**：定期备份数据库和重要数据
4. **监控告警**：设置容器监控和告警
5. **日志聚合**：使用ELK或类似工具集中管理日志

#### 10.2 性能优化

1. **调整工作进程数**：根据CPU核心数调整CMD_MAX_WORKERS
2. **启用缓存**：使用Redis缓存频繁访问的数据
3. **数据库优化**：对PostgreSQL进行性能调优
4. **CDN加速**：静态资源使用CDN加速

#### 10.3 安全建议

1. **定期更新**：定期更新基础镜像和依赖包
2. **漏洞扫描**：使用docker scan扫描镜像漏洞
3. **网络隔离**：使用内部网络隔离敏感服务
4. **访问控制**：配置防火墙和访问控制列表

## 附录

### A. 常用命令参考

```bash
# 构建和运行
docker-compose build          # 构建镜像
docker-compose up -d          # 启动服务
docker-compose down           # 停止服务
docker-compose restart        # 重启服务

# 监控和日志
docker-compose ps             # 查看服务状态
docker-compose logs -f        # 查看实时日志
docker-compose top            # 查看进程信息

# 维护操作
docker-compose exec api bash  # 进入容器
docker-compose pull           # 拉取最新镜像
docker-compose config         # 验证配置

# 清理操作
docker-compose down -v        # 停止并删除卷
docker system prune -a        # 清理所有未使用资源
```

### B. 环境变量参考

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| FLASK_ENV | production | Flask环境模式 |
| DATABASE_URL | sqlite:///instance/users.db | 数据库连接URL |
| SECRET_KEY | (必填) | 应用密钥 |
| MAIL_SERVER | smtp.gmail.com | 邮件服务器 |
| MAIL_USERNAME | (必填) | 邮件用户名 |
| MAIL_PASSWORD | (必填) | 邮件密码 |
| CMD_MAX_WORKERS | 7 | CMD最大并发数 |
| CMD_TIMEOUT | 15 | 命令执行超时(秒) |

### C. 端口说明

| 服务 | 容器端口 | 主机端口 | 说明 |
|------|----------|----------|------|
| API | 5000 | 5000 | Flask应用端口 |
| Nginx | 80, 443 | 80, 443 | HTTP/HTTPS端口 |
| PostgreSQL | 5432 | 5432 | 数据库端口 |
| Redis | 6379 | 6379 | 缓存端口 |

### D. 技术支持

如有问题，请参考：

1. **项目文档**：查看AGENTS.md和README文件
2. **Docker文档**：https://docs.docker.com
3. **问题反馈**：创建GitHub Issue

---

**版本**: 1.0.0  
**更新日期**: 2024-01-15  
**适用环境**: Docker 20.10+, Docker Compose 2.0+