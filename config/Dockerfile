# Python项目Docker镜像
# 多阶段构建：构建阶段 + 运行阶段

# ==================== 构建阶段 ====================
FROM python:3.9-slim AS builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 创建虚拟环境并安装依赖
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ==================== 运行阶段 ====================
FROM python:3.9-slim

# 设置元数据
LABEL maintainer="pythoncode@example.com"
LABEL version="1.0.0"
LABEL description="Python项目容器镜像 - 包含名片生成、用户API和CMD代理"

# 安装运行时系统依赖
RUN apt-get update && apt-get install -y \
    # 字体支持（用于名片生成）
    fonts-wqy-microhei \
    fonts-wqy-zenhei \
    ttf-mscorefonts-installer \
    # 系统工具
    curl \
    vim \
    && rm -rf /var/lib/apt/lists/*

# 创建非root用户
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# 设置工作目录
WORKDIR /app

# 从构建阶段复制虚拟环境
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# 复制应用代码
COPY --chown=appuser:appuser . .

# 创建必要的目录
RUN mkdir -p instance logs data && \
    chown -R appuser:appuser instance logs data

# 设置环境变量
ENV FLASK_APP=api/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai

# 切换到非root用户
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# 暴露端口
EXPOSE 5000

# 默认启动命令（可以根据需要覆盖）
CMD ["python", "api/app.py"]

# ==================== 多服务支持 ====================
# 可以通过docker-compose或Kubernetes启动不同服务

# 启动API服务
# docker run -p 5000:5000 pythoncode:latest python api/app.py

# 启动CMD Agent
# docker run -it pythoncode:latest python command_system/cmd_agent.py interactive

# 启动名片生成器
# docker run -v $(pwd)/data:/app/data pythoncode:latest python card_generator/Line2Card.py