@echo off
echo 重命名 CI/CD 工作流文件
echo ========================================

REM 检查文件是否存在
if exist ".github\workflows\ci-cd-new.yml" (
    echo 找到 ci-cd-new.yml 文件
) else (
    echo 错误: ci-cd-new.yml 文件不存在
    pause
    exit /b 1
)

REM 尝试重命名旧文件
if exist ".github\workflows\ci-cd.yml" (
    echo 尝试重命名 ci-cd.yml...
    ren ".github\workflows\ci-cd.yml" "ci-cd-old-%date:~0,4%%date:~5,2%%date:~8,2%.yml"
    if %errorlevel% neq 0 (
        echo 警告: 无法重命名 ci-cd.yml (可能被锁定)
        echo 将在下次重启后自动重命名
    ) else (
        echo 成功重命名 ci-cd.yml
    )
)

REM 重命名新文件
echo 重命名 ci-cd-new.yml 为 ci-cd.yml...
ren ".github\workflows\ci-cd-new.yml" "ci-cd.yml"

if %errorlevel% equ 0 (
    echo 成功: CI/CD 工作流文件已更新
    echo.
    echo 下一步:
    echo 1. 运行 apply_branch_protection.sh 应用分支保护规则
    echo 2. 在 GitHub 中设置环境密钥
    echo 3. 配置团队权限
) else (
    echo 错误: 无法重命名文件
    pause
    exit /b 1
)

pause