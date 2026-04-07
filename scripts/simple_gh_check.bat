@echo off
echo Checking GitHub CLI installation...
echo ===================================

where gh >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] GitHub CLI is installed
    echo.
    gh --version
    echo.
    
    echo Checking authentication...
    gh auth status
    if %errorlevel% equ 0 (
        echo [OK] GitHub CLI is authenticated
        echo.
        echo Next steps:
        echo 1. Apply branch protection rules
        echo 2. Set up environment secrets
        echo 3. Configure teams and permissions
        echo 4. Run test deployment
    ) else (
        echo [WARNING] GitHub CLI not authenticated
        echo.
        echo Please run: gh auth login
        echo Follow the prompts to authenticate
    )
) else (
    echo [ERROR] GitHub CLI not installed
    echo.
    echo Installation options:
    echo 1. Using winget: winget install --id GitHub.cli
    echo 2. Using Chocolatey: choco install gh -y
    echo 3. Manual download: https://github.com/cli/cli/releases
    echo.
    echo After installation, restart terminal and run: gh auth login
)

echo.
pause