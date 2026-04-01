#!/bin/bash
# Docker容器运行和管理脚本
# 用于启动、停止、管理Python项目容器

set -e  # 遇到错误时退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 默认值
CONTAINER_NAME="pythoncode-app"
IMAGE_NAME="pythoncode:latest"
PORT="5000"
VOLUME_MAPPING=""
ENV_VARS=""
NETWORK=""
COMMAND=""
ACTION="run"
DETACH=true
CLEAN=false
FOLLOW_LOGS=false
INTERACTIVE=false

# 显示帮助信息
show_help() {
    cat << EOF
Docker容器运行和管理脚本

用法: $0 [动作] [选项]

动作:
  run     运行容器 (默认)
  start   启动已停止的容器
  stop    停止运行中的容器
  restart 重启容器
  rm      删除容器
  logs    查看容器日志
  exec    在容器中执行命令
  ps      查看容器状态
  stats   查看容器资源使用
  shell   进入容器shell
  clean   清理所有相关容器和镜像

选项:
  -h, --help            显示此帮助信息
  -n, --name NAME       容器名称 (默认: pythoncode-app)
  -i, --image IMAGE     镜像名称 (默认: pythoncode:latest)
  -p, --port PORT       主机端口:容器端口 (默认: 5000:5000)
  -v, --volume DIR      挂载目录 (格式: 主机目录:容器目录)
  -e, --env KEY=VALUE   环境变量
  --network NETWORK     网络名称
  -c, --command CMD     覆盖默认命令
  -d, --detach          后台运行 (默认)
  -it, --interactive    交互模式运行
  -f, --follow          跟随日志输出
  --clean               清理模式

示例:
  $0 run                    # 运行默认容器
  $0 run -p 8080:5000      # 指定端口运行
  $0 run -v ./data:/app/data # 挂载数据目录
  $0 logs -f               # 查看并跟随日志
  $0 shell                 # 进入容器shell
  $0 exec "python test.py" # 在容器中执行命令
  $0 clean                 # 清理所有容器和镜像
EOF
}

# 解析命令行参数
parse_args() {
    # 第一个参数可能是动作
    case "$1" in
        run|start|stop|restart|rm|logs|exec|ps|stats|shell|clean)
            ACTION="$1"
            shift
            ;;
    esac

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                show_help
                exit 0
                ;;
            -n|--name)
                CONTAINER_NAME="$2"
                shift 2
                ;;
            -i|--image)
                IMAGE_NAME="$2"
                shift 2
                ;;
            -p|--port)
                PORT="$2"
                shift 2
                ;;
            -v|--volume)
                if [[ -n "$VOLUME_MAPPING" ]]; then
                    VOLUME_MAPPING="$VOLUME_MAPPING -v $2"
                else
                    VOLUME_MAPPING="-v $2"
                fi
                shift 2
                ;;
            -e|--env)
                if [[ -n "$ENV_VARS" ]]; then
                    ENV_VARS="$ENV_VARS -e $2"
                else
                    ENV_VARS="-e $2"
                fi
                shift 2
                ;;
            --network)
                NETWORK="--network $2"
                shift 2
                ;;
            -c|--command)
                COMMAND="$2"
                shift 2
                ;;
            -d|--detach)
                DETACH=true
                shift
                ;;
            -it|--interactive)
                INTERACTIVE=true
                DETACH=false
                shift
                ;;
            -f|--follow)
                FOLLOW_LOGS=true
                shift
                ;;
            --clean)
                CLEAN=true
                shift
                ;;
            *)
                echo -e "${RED}错误: 未知选项 $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
}

# 检查Docker是否运行
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}错误: Docker未安装${NC}"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}错误: Docker守护进程未运行${NC}"
        exit 1
    fi
}

# 运行容器
run_container() {
    echo -e "${GREEN}启动容器: ${CONTAINER_NAME}${NC}"
    
    local run_cmd="docker run"
    
    # 基本参数
    run_cmd="$run_cmd --name $CONTAINER_NAME"
    
    # 端口映射
    if [[ "$PORT" == *":"* ]]; then
        run_cmd="$run_cmd -p $PORT"
    else
        run_cmd="$run_cmd -p $PORT:5000"
    fi
    
    # 卷映射
    if [[ -n "$VOLUME_MAPPING" ]]; then
        run_cmd="$run_cmd $VOLUME_MAPPING"
    else
        # 默认卷映射
        run_cmd="$run_cmd -v $(pwd)/instance:/app/instance"
        run_cmd="$run_cmd -v $(pwd)/logs:/app/logs"
        run_cmd="$run_cmd -v $(pwd)/data:/app/data"
    fi
    
    # 环境变量
    if [[ -n "$ENV_VARS" ]]; then
        run_cmd="$run_cmd $ENV_VARS"
    fi
    
    # 网络
    if [[ -n "$NETWORK" ]]; then
        run_cmd="$run_cmd $NETWORK"
    fi
    
    # 后台/交互模式
    if [[ "$DETACH" == true ]]; then
        run_cmd="$run_cmd -d"
    elif [[ "$INTERACTIVE" == true ]]; then
        run_cmd="$run_cmd -it"
    fi
    
    # 命令
    if [[ -n "$COMMAND" ]]; then
        run_cmd="$run_cmd $IMAGE_NAME $COMMAND"
    else
        run_cmd="$run_cmd $IMAGE_NAME"
    fi
    
    echo -e "${YELLOW}执行命令: $run_cmd${NC}"
    eval $run_cmd
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ 容器启动成功${NC}"
        
        # 显示容器信息
        sleep 2
        show_container_info
    else
        echo -e "${RED}❌ 容器启动失败${NC}"
    fi
}

# 显示容器信息
show_container_info() {
    echo -e "${BLUE}容器信息:${NC}"
    
    # 基本信息
    docker ps -f "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}\t{{.Image}}"
    
    # IP地址
    local ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$CONTAINER_NAME" 2>/dev/null)
    if [[ -n "$ip" ]]; then
        echo -e "IP地址: $ip"
    fi
    
    # 健康状态
    local health=$(docker inspect -f '{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null)
    if [[ -n "$health" ]]; then
        echo -e "健康状态: $health"
    fi
    
    # 使用说明
    echo -e "${YELLOW}使用说明:${NC}"
    echo -e "查看日志: docker logs $CONTAINER_NAME"
    echo -e "进入容器: docker exec -it $CONTAINER_NAME bash"
    echo -e "停止容器: docker stop $CONTAINER_NAME"
    
    # API端点信息
    local host_port=$(echo "$PORT" | cut -d: -f1)
    echo -e "${GREEN}API端点: http://localhost:$host_port${NC}"
    echo -e "健康检查: http://localhost:$host_port/api/health"
}

# 启动容器
start_container() {
    echo -e "${GREEN}启动容器: $CONTAINER_NAME${NC}"
    docker start "$CONTAINER_NAME"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ 容器启动成功${NC}"
        show_container_info
    else
        echo -e "${RED}❌ 容器启动失败${NC}"
    fi
}

# 停止容器
stop_container() {
    echo -e "${YELLOW}停止容器: $CONTAINER_NAME${NC}"
    docker stop "$CONTAINER_NAME"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ 容器停止成功${NC}"
    else
        echo -e "${RED}❌ 容器停止失败${NC}"
    fi
}

# 重启容器
restart_container() {
    echo -e "${YELLOW}重启容器: $CONTAINER_NAME${NC}"
    docker restart "$CONTAINER_NAME"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ 容器重启成功${NC}"
        show_container_info
    else
        echo -e "${RED}❌ 容器重启失败${NC}"
    fi
}

# 删除容器
remove_container() {
    echo -e "${YELLOW}删除容器: $CONTAINER_NAME${NC}"
    
    # 先停止容器
    docker stop "$CONTAINER_NAME" 2>/dev/null
    
    # 删除容器
    docker rm "$CONTAINER_NAME"
    
    if [[ $? -eq 0 ]]; then
        echo -e "${GREEN}✅ 容器删除成功${NC}"
    else
        echo -e "${RED}❌ 容器删除失败${NC}"
    fi
}

# 查看日志
show_logs() {
    echo -e "${GREEN}容器日志: $CONTAINER_NAME${NC}"
    
    local log_cmd="docker logs"
    
    if [[ "$FOLLOW_LOGS" == true ]]; then
        log_cmd="$log_cmd -f"
    fi
    
    log_cmd="$log_cmd $CONTAINER_NAME"
    eval $log_cmd
}

# 执行命令
exec_command() {
    if [[ -z "$COMMAND" ]]; then
        echo -e "${RED}错误: 需要指定命令${NC}"
        show_help
        exit 1
    fi
    
    echo -e "${GREEN}在容器中执行命令: $COMMAND${NC}"
    docker exec "$CONTAINER_NAME" sh -c "$COMMAND"
}

# 进入容器shell
enter_shell() {
    echo -e "${GREEN}进入容器shell: $CONTAINER_NAME${NC}"
    
    # 检查容器是否运行
    if ! docker ps -f "name=$CONTAINER_NAME" --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        echo -e "${YELLOW}容器未运行，正在启动...${NC}"
        docker start "$CONTAINER_NAME"
        sleep 2
    fi
    
    docker exec -it "$CONTAINER_NAME" bash
}

# 查看容器状态
show_status() {
    echo -e "${GREEN}容器状态:${NC}"
    docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.CreatedAt}}" | head -1
    docker ps -a --format "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.CreatedAt}}" | grep -E "(pythoncode|$CONTAINER_NAME)"
}

# 查看容器资源使用
show_stats() {
    echo -e "${GREEN}容器资源使用:${NC}"
    docker stats --no-stream "$CONTAINER_NAME" 2>/dev/null || echo -e "${YELLOW}容器未运行${NC}"
}

# 清理所有相关容器和镜像
clean_all() {
    echo -e "${RED}⚠️  警告: 这将清理所有相关容器和镜像${NC}"
    read -p "确定要继续吗? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}操作取消${NC}"
        exit 0
    fi
    
    # 停止并删除所有pythoncode容器
    echo -e "${YELLOW}停止并删除容器...${NC}"
    docker ps -a --filter "name=pythoncode" --format "{{.Names}}" | while read container; do
        echo "删除容器: $container"
        docker stop "$container" 2>/dev/null
        docker rm "$container" 2>/dev/null
    done
    
    # 删除pythoncode镜像
    echo -e "${YELLOW}删除镜像...${NC}"
    docker images --filter "reference=pythoncode*" --format "{{.Repository}}:{{.Tag}}" | while read image; do
        echo "删除镜像: $image"
        docker rmi "$image" 2>/dev/null
    done
    
    # 清理未使用的资源
    echo -e "${YELLOW}清理未使用的资源...${NC}"
    docker system prune -f
    
    echo -e "${GREEN}✅ 清理完成${NC}"
}

# 主函数
main() {
    parse_args "$@"
    check_docker
    
    case "$ACTION" in
        run)
            run_container
            ;;
        start)
            start_container
            ;;
        stop)
            stop_container
            ;;
        restart)
            restart_container
            ;;
        rm)
            remove_container
            ;;
        logs)
            show_logs
            ;;
        exec)
            exec_command
            ;;
        ps)
            show_status
            ;;
        stats)
            show_stats
            ;;
        shell)
            enter_shell
            ;;
        clean)
            clean_all
            ;;
        *)
            echo -e "${RED}错误: 未知动作 $ACTION${NC}"
            show_help
            exit 1
            ;;
    esac
}

# 运行主函数
main "$@"