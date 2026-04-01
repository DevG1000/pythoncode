@echo off
REM Docker构建脚本 - Windows版本
REM 用于构建Python项目Docker镜像

setlocal enabledelayedexpansion

REM 颜色定义（Windows CMD不支持ANSI颜色，使用文本替代）
set RED=[ERROR]
set GREEN=[OK]
set YELLOW=[INFO]
set BLUE=[=====]

REM 默认值
set IMAGE_NAME=pythoncode
set IMAGE_TAG=latest
set REGISTRY=
set PUSH_TO_REGISTRY=false
set BUILD_PLATFORM=linux/amd64
set CLEAN_BUILD=false
set TEST_IMAGE=false

REM 显示帮助信息
:show_help
echo %BLUE%========================================
echo Docker构建脚本 - Python项目容器镜像构建工具
echo ========================================
echo.
echo 用法: build-docker.bat [选项]
echo.
echo 选项:
echo   -h, --help            显示此帮助信息
echo   -n, --name NAME       镜像名称 (默认: pythoncode)
echo   -t, --tag TAG         镜像标签 (默认: latest)
echo   -r, --registry REG    镜像仓库地址 (例如: docker.io/username)
echo   -p, --push            构建后推送到镜像仓库
echo   --platform PLATFORM   构建平台 (默认: linux/amd64)
echo   -c, --clean           清理构建缓存
echo   --test                构建后测试镜像
echo.
echo 示例:
echo   build-docker.bat                   构建默认镜像
echo   build-docker.bat -n myapp -t v1.0  构建指定名称和标签的镜像
echo   build-docker.bat -r docker.io/user -p  构建并推送到Docker Hub
echo.
goto :eof

REM 解析命令行参数
:parse_args
if "%1"=="" goto :args_done

if "%1"=="-h" goto show_help
if "%1"=="--help" goto show_help

if "%1"=="-n" (
    set IMAGE_NAME=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--name" (
    set IMAGE_NAME=%2
    shift
    shift
    goto parse_args
)

if "%1"=="-t" (
    set IMAGE_TAG=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--tag" (
    set IMAGE_TAG=%2
    shift
    shift
    goto parse_args
)

if "%1"=="-r" (
    set REGISTRY=%2
    shift
    shift
    goto parse_args
)
if "%1"=="--registry" (
    set REGISTRY=%2
    shift
    shift
    goto parse_args
)

if "%1"=="-p" (
    set PUSH_TO_REGISTRY=true
    shift
    goto parse_args
)
if "%1"=="--push" (
    set PUSH_TO_REGISTRY=true
    shift
    goto parse_args
)

if "%1"=="--platform" (
    set BUILD_PLATFORM=%2
    shift
    shift
    goto parse_args
)

if "%1"=="-c" (
    set CLEAN_BUILD=true
    shift
    goto parse_args
)
if "%1"=="--clean" (
    set CLEAN_BUILD=true
    shift
    goto parse_args
)

if "%1"=="--test" (
    set TEST_IMAGE=true
    shift
    goto parse_args
)

echo %RED%错误: 未知选项 %1%
goto show_help

:args_done

REM 构建完整镜像名称
if "%REGISTRY%"=="" (
    set FULL_IMAGE_NAME=%IMAGE_NAME%:%IMAGE_TAG%
) else (
    set FULL_IMAGE_NAME=%REGISTRY%/%IMAGE_NAME%:%IMAGE_TAG%
)

REM 打印构建信息
echo %BLUE%========================================
echo %GREEN%开始构建Docker镜像
echo %BLUE%========================================
echo 镜像名称: %FULL_IMAGE_NAME%
echo 构建平台: %BUILD_PLATFORM%
echo 项目目录: %CD%
echo 构建时间: %DATE% %TIME%
echo %BLUE%========================================

REM 清理构建缓存
if "%CLEAN_BUILD%"=="true" (
    echo %YELLOW%清理Docker构建缓存...
    docker builder prune -f
    docker image prune -f
)

REM 检查Docker是否安装
where docker >nul 2>nul
if errorlevel 1 (
    echo %RED%错误: Docker未安装
    exit /b 1
)

REM 检查Docker守护进程是否运行
docker info >nul 2>nul
if errorlevel 1 (
    echo %RED%错误: Docker守护进程未运行
    exit /b 1
)

REM 构建镜像
echo %GREEN%开始构建镜像...
docker build --platform %BUILD_PLATFORM% -t %FULL_IMAGE_NAME% .

REM 检查构建是否成功
if errorlevel 1 (
    echo %RED%❌ 镜像构建失败
    exit /b 1
) else (
    echo %GREEN%✅ 镜像构建成功: %FULL_IMAGE_NAME%
    
    REM 显示镜像信息
    echo %BLUE%镜像信息:
    for /f "tokens=*" %%i in ('docker image inspect %FULL_IMAGE_NAME% --format^{{^.Size^}^}') do (
        set size=%%i
        set /a size_mb=!size!/1024/1024
        echo 大小: !size_mb! MB
    )
    
    for /f "tokens=*" %%i in ('docker image inspect %FULL_IMAGE_NAME% --format^{{^.Created^}^}') do (
        echo 创建时间: %%i
    )
)

REM 测试镜像（如果启用）
if "%TEST_IMAGE%"=="true" (
    echo %YELLOW%测试镜像...
    
    REM 创建测试容器
    set TEST_CONTAINER_NAME=test-%IMAGE_NAME%-%TIME::=%
    set TEST_CONTAINER_NAME=%TEST_CONTAINER_NAME:.=%
    
    REM 运行健康检查
    echo %BLUE%运行健康检查...
    docker run -d --name %TEST_CONTAINER_NAME% -p 5001:5000 %FULL_IMAGE_NAME%
    
    REM 等待应用启动
    echo %YELLOW%等待应用启动...
    timeout /t 10 /nobreak >nul
    
    REM 检查健康端点（使用curl或powershell）
    where curl >nul 2>nul
    if errorlevel 1 (
        REM 使用powershell检查
        powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:5001/api/health' -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }"
    ) else (
        curl -f http://localhost:5001/api/health >nul 2>nul
    )
    
    if errorlevel 1 (
        echo %RED%❌ 健康检查失败
        docker logs %TEST_CONTAINER_NAME%
    ) else (
        echo %GREEN%✅ 健康检查通过
    )
    
    REM 清理测试容器
    docker stop %TEST_CONTAINER_NAME% >nul 2>nul
    docker rm %TEST_CONTAINER_NAME% >nul 2>nul
    echo %GREEN%✅ 镜像测试完成
)

REM 推送到镜像仓库（如果启用）
if "%PUSH_TO_REGISTRY%"=="true" (
    echo %YELLOW%推送镜像到仓库...
    
    REM 推送镜像
    docker push %FULL_IMAGE_NAME%
    
    if errorlevel 1 (
        echo %RED%❌ 镜像推送失败
        exit /b 1
    ) else (
        echo %GREEN%✅ 镜像推送成功
    )
)

REM 显示使用说明
echo %BLUE%========================================
echo %GREEN%构建完成！
echo %BLUE%========================================
echo %YELLOW%使用说明:
echo 1. 运行容器: docker run -p 5000:5000 %FULL_IMAGE_NAME%
echo 2. 使用docker-compose: docker-compose up -d
echo 3. 查看运行容器: docker ps
echo 4. 查看日志: docker logs ^<container_name^>
echo 5. 进入容器: docker exec -it ^<container_name^> bash
echo %BLUE%========================================

REM 保存构建信息
echo # Docker构建信息 > .docker-build-info.txt
echo 构建时间: %DATE% %TIME% >> .docker-build-info.txt
echo 镜像名称: %FULL_IMAGE_NAME% >> .docker-build-info.txt
echo 构建平台: %BUILD_PLATFORM% >> .docker-build-info.txt

echo %GREEN%构建信息已保存到: .docker-build-info.txt

endlocal
pause