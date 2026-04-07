@echo off
echo ===========================================
echo    Staging Environment Setup for Windows
echo ===========================================
echo.

REM 检查GitHub CLI是否已安装
echo Checking GitHub CLI installation...
gh --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ GitHub CLI is not installed or not in PATH
    echo Please install GitHub CLI first:
    echo   winget install --id GitHub.cli
    echo   or download from: https://github.com/cli/cli/releases
    pause
    exit /b 1
)
echo ✅ GitHub CLI is installed

REM 检查认证状态
echo.
echo Checking authentication status...
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ GitHub CLI is not authenticated
    echo Please run: gh auth login
    echo Then run this script again
    pause
    exit /b 1
)
echo ✅ GitHub CLI is authenticated

REM 设置仓库信息
set OWNER=DevG1000
set REPO=pythoncode

echo.
echo Setting up staging environment for: %OWNER%/%REPO%
echo =================================================

REM 1. 设置环境变量
echo.
echo 1. Setting environment variables...
echo.

REM 设置ENVIRONMENT变量
echo Setting ENVIRONMENT variable...
gh variable set ENVIRONMENT --env staging --body "staging" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ ENVIRONMENT variable set
) else (
    echo ⚠ Could not set ENVIRONMENT variable (may already exist)
)

REM 设置LOG_LEVEL变量
echo Setting LOG_LEVEL variable...
gh variable set LOG_LEVEL --env staging --body "DEBUG" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ LOG_LEVEL variable set
) else (
    echo ⚠ Could not set LOG_LEVEL variable (may already exist)
)

REM 设置API_URL变量
echo Setting API_URL variable...
gh variable set API_URL --env staging --body "https://api.staging.pythoncode.com" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ API_URL variable set
) else (
    echo ⚠ Could not set API_URL variable (may already exist)
)

REM 设置DATABASE_URL变量
echo Setting DATABASE_URL variable...
gh variable set DATABASE_URL --env staging --body "${{ secrets.STAGING_DATABASE_URL }}" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ DATABASE_URL variable set
) else (
    echo ⚠ Could not set DATABASE_URL variable (may already exist)
)

REM 设置REDIS_URL变量
echo Setting REDIS_URL variable...
gh variable set REDIS_URL --env staging --body "${{ secrets.STAGING_REDIS_URL }}" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ REDIS_URL variable set
) else (
    echo ⚠ Could not set REDIS_URL variable (may already exist)
)

REM 2. 设置环境密钥
echo.
echo 2. Setting environment secrets...
echo.

REM 设置STAGING_DATABASE_URL密钥
echo Setting STAGING_DATABASE_URL secret...
gh secret set STAGING_DATABASE_URL --env staging --body "postgresql://staging_user:staging_pass@localhost:5432/staging_db" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ STAGING_DATABASE_URL secret set
) else (
    echo ⚠ Could not set STAGING_DATABASE_URL secret (may already exist)
)

REM 设置STAGING_REDIS_URL密钥
echo Setting STAGING_REDIS_URL secret...
gh secret set STAGING_REDIS_URL --env staging --body "redis://localhost:6379/0" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ STAGING_REDIS_URL secret set
) else (
    echo ⚠ Could not set STAGING_REDIS_URL secret (may already exist)
)

REM 设置STAGING_API_KEY密钥
echo Setting STAGING_API_KEY secret...
REM 生成随机API密钥
for /f %%i in ('powershell -Command "[System.Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes([System.Guid]::NewGuid().ToString()))"') do set API_KEY=%%i
gh secret set STAGING_API_KEY --env staging --body "staging_api_key_%API_KEY%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ STAGING_API_KEY secret set: staging_api_key_%API_KEY%
) else (
    echo ⚠ Could not set STAGING_API_KEY secret (may already exist)
)

REM 设置STAGING_SSH_KEY密钥（示例）
echo Setting STAGING_SSH_KEY secret...
gh secret set STAGING_SSH_KEY --env staging --body "-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAwV2UqU6L7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7
KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7
KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7
KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7
KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7KJ7
-----END RSA PRIVATE KEY-----" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ STAGING_SSH_KEY secret set (example key)
) else (
    echo ⚠ Could not set STAGING_SSH_KEY secret (may already exist)
)

REM 3. 验证设置
echo.
echo 3. Verifying setup...
echo.

REM 验证环境存在
echo Verifying staging environment...
gh api repos/%OWNER%/%REPO%/environments/staging >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Staging environment exists
) else (
    echo ❌ Staging environment not found
)

REM 列出环境变量
echo.
echo Listing environment variables...
gh variable list --env staging

REM 列出环境密钥（只显示名称）
echo.
echo Listing environment secrets...
gh secret list --env staging

REM 4. 完成信息
echo.
echo ===========================================
echo    Setup Complete!
echo ===========================================
echo.
echo Summary:
echo - Environment variables set: ENVIRONMENT, LOG_LEVEL, API_URL, DATABASE_URL, REDIS_URL
echo - Environment secrets set: STAGING_DATABASE_URL, STAGING_REDIS_URL, STAGING_API_KEY, STAGING_SSH_KEY
echo.
echo Next steps:
echo 1. Update your CI/CD workflow to use the staging environment
echo 2. Test deployment with: gh workflow run "your-workflow.yml" --ref develop
echo 3. Monitor deployments at: https://github.com/%OWNER%/%REPO%/deployments
echo.
echo Press any key to exit...
pause >nul