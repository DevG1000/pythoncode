#!/bin/bash
# Docker构建脚本
# 用于构建和推送Python项目Docker镜像

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
IMAGE_NAME="pythoncode"
IMAGE_TAG="latest"
REGISTRY=""
PUSH_TO_REGISTRY=false
BUILD_PLATFORM="linux/amd64"
CLEAN_BUILD=false
TEST_IMAGE=false

# 显示帮助信息
show_help() {
    cat << EOF
Docker构建脚本 - Python项目容器镜像构建工具

用法: $0 [选项]

选项:
  -h, --help            显示此帮助信息
  -n, --name NAME       镜像名称 (默认: pythoncode)
  -t, --tag TAG         镜像标签 (默认: latest)
  -r, --registry REG    镜像仓库地址 (例如: docker.io/username)
  -p, --push            构建后推送到镜像仓库
  --platform PLATFORM   构建平台 (默认: linux/amd64)
  -c, --clean           清理构建缓存
  --test                构建后测试镜像
  --multi-platform      多平台构建 (amd64,arm64)

示例:
  $0                      # 构建默认镜像
  $0 -n myapp -t v1.0     # 构建指定名称和标签的镜像
  $0 -r docker.io/user -p # 构建并推送到Docker Hub
  $0 --multi-platform     # 构建多平台镜像
EOF
}

# 解析命令行参数
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_help
            exit 0
            ;;
        -n|--name)
            IMAGE_NAME="$2"
            shift 2
            ;;
        -t|--tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -p|--push)
            PUSH_TO_REGISTRY=true
            shift
            ;;
        --platform)
            BUILD_PLATFORM="$2"
            shift 2
            ;;
        -c|--clean)
            CLEAN_BUILD=true
            shift
            ;;
        --test)
            TEST_IMAGE=true
            shift
            ;;
        --multi-platform)
            BUILD_PLATFORM="linux/amd64,linux/arm64"
            shift
            ;;
        *)
            echo -e "${RED}错误: 未知选项 $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# 构建完整镜像名称
if [[ -n "$REGISTRY" ]]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"
fi

# 打印构建信息
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}开始构建Docker镜像${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "镜像名称: ${YELLOW}${FULL_IMAGE_NAME}${NC}"
echo -e "构建平台: ${YELLOW}${BUILD_PLATFORM}${NC}"
echo -e "项目目录: ${YELLOW}$(pwd)${NC}"
echo -e "构建时间: ${YELLOW}$(date)${NC}"
echo -e "${BLUE}========================================${NC}"

# 清理构建缓存
if [[ "$CLEAN_BUILD" == true ]]; then
    echo -e "${YELLOW}清理Docker构建缓存...${NC}"
    docker builder prune -f
    docker image prune -f
fi

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo -e "${RED}错误: Docker未安装${NC}"
    exit 1
fi

# 检查Docker守护进程是否运行
if ! docker info &> /dev/null; then
    echo -e "${RED}错误: Docker守护进程未运行${NC}"
    exit 1
fi

# 构建镜像
echo -e "${GREEN}开始构建镜像...${NC}"
if [[ "$BUILD_PLATFORM" == *","* ]]; then
    # 多平台构建
    echo -e "${YELLOW}执行多平台构建: ${BUILD_PLATFORM}${NC}"
    
    # 创建构建器实例（如果需要）
    if ! docker buildx ls | grep -q multiarch-builder; then
        echo -e "${YELLOW}创建多平台构建器...${NC}"
        docker buildx create --name multiarch-builder --use
    fi
    
    # 启动构建器
    docker buildx use multiarch-builder
    docker buildx inspect --bootstrap
    
    # 执行构建
    docker buildx build \
        --platform "$BUILD_PLATFORM" \
        -t "$FULL_IMAGE_NAME" \
        --push=$PUSH_TO_REGISTRY \
        .
else
    # 单平台构建
    docker build \
        --platform "$BUILD_PLATFORM" \
        -t "$FULL_IMAGE_NAME" \
        .
fi

# 检查构建是否成功
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✅ 镜像构建成功: ${FULL_IMAGE_NAME}${NC}"
    
    # 显示镜像信息
    echo -e "${BLUE}镜像信息:${NC}"
    docker image inspect "$FULL_IMAGE_NAME" --format='{{.Size}}' | awk '{print "大小: " $1/1024/1024 " MB"}'
    docker image inspect "$FULL_IMAGE_NAME" --format='{{.Created}}' | awk '{print "创建时间: " $1}'
    docker image inspect "$FULL_IMAGE_NAME" --format='{{.Config.Cmd}}' | awk '{print "默认命令: " $0}'
else
    echo -e "${RED}❌ 镜像构建失败${NC}"
    exit 1
fi

# 测试镜像（如果启用）
if [[ "$TEST_IMAGE" == true ]]; then
    echo -e "${YELLOW}测试镜像...${NC}"
    
    # 创建测试容器
    TEST_CONTAINER_NAME="test-${IMAGE_NAME}-$(date +%s)"
    
    # 运行健康检查
    echo -e "${BLUE}运行健康检查...${NC}"
    docker run -d --name "$TEST_CONTAINER_NAME" -p 5001:5000 "$FULL_IMAGE_NAME"
    
    # 等待应用启动
    echo -e "${YELLOW}等待应用启动...${NC}"
    sleep 10
    
    # 检查健康端点
    if curl -f http://localhost:5001/api/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 健康检查通过${NC}"
    else
        echo -e "${RED}❌ 健康检查失败${NC}"
        docker logs "$TEST_CONTAINER_NAME"
    fi
    
    # 清理测试容器
    docker stop "$TEST_CONTAINER_NAME" > /dev/null 2>&1
    docker rm "$TEST_CONTAINER_NAME" > /dev/null 2>&1
    echo -e "${GREEN}✅ 镜像测试完成${NC}"
fi

# 推送到镜像仓库（如果启用）
if [[ "$PUSH_TO_REGISTRY" == true ]] && [[ "$BUILD_PLATFORM" != *","* ]]; then
    echo -e "${YELLOW}推送镜像到仓库...${NC}"
    
    # 检查是否已登录
    if ! docker info | grep -q "Username"; then
        echo -e "${RED}错误: 未登录到Docker Registry${NC}"
        echo -e "${YELLOW}请先运行: docker login${NC}"
        exit 1
    fi
    
    # 推送镜像
    if docker push "$FULL_IMAGE_NAME"; then
        echo -e "${GREEN}✅ 镜像推送成功${NC}"
        
        # 显示镜像仓库信息
        if [[ "$REGISTRY" == *"docker.io"* ]]; then
            REPO_NAME=$(echo "$FULL_IMAGE_NAME" | sed 's|docker.io/||')
            echo -e "${BLUE}镜像地址: https://hub.docker.com/r/${REPO_NAME%:*}${NC}"
        fi
    else
        echo -e "${RED}❌ 镜像推送失败${NC}"
        exit 1
    fi
fi

# 显示使用说明
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}构建完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${YELLOW}使用说明:${NC}"
echo -e "1. 运行容器: ${GREEN}docker run -p 5000:5000 ${FULL_IMAGE_NAME}${NC}"
echo -e "2. 使用docker-compose: ${GREEN}docker-compose up -d${NC}"
echo -e "3. 查看运行容器: ${GREEN}docker ps${NC}"
echo -e "4. 查看日志: ${GREEN}docker logs <container_name>${NC}"
echo -e "5. 进入容器: ${GREEN}docker exec -it <container_name> bash${NC}"
echo -e "${BLUE}========================================${NC}"

# 保存构建信息
BUILD_INFO_FILE=".docker-build-info"
cat > "$BUILD_INFO_FILE" << EOF
# Docker构建信息
构建时间: $(date)
镜像名称: $FULL_IMAGE_NAME
构建平台: $BUILD_PLATFORM
Git提交: $(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
Python版本: $(python --version 2>/dev/null || echo "N/A")
EOF

echo -e "${GREEN}构建信息已保存到: ${BUILD_INFO_FILE}${NC}"