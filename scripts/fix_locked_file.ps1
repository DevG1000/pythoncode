# PowerShell 脚本解决文件锁定问题
Write-Host "解决文件锁定问题" -ForegroundColor Cyan
Write-Host "==============================" -ForegroundColor Cyan

$workflowDir = ".github\workflows"
$oldFile = Join-Path $workflowDir "ci-cd.yml"
$newFile = Join-Path $workflowDir "ci-cd-new.yml"
$backupFile = Join-Path $workflowDir "ci-cd-backup-$(Get-Date -Format 'yyyyMMdd-HHmmss').yml"

# 检查新文件是否存在
if (-not (Test-Path $newFile)) {
    Write-Host "错误: $newFile 不存在" -ForegroundColor Red
    exit 1
}

# 尝试查找锁定文件的进程
Write-Host "`n检查锁定文件的进程..." -ForegroundColor Yellow
try {
    $lockedBy = Get-Process | Where-Object {
        $_.Modules | Where-Object {
            $_.FileName -like "*ci-cd.yml*"
        }
    } | Select-Object Name, Id, Path
    
    if ($lockedBy) {
        Write-Host "找到锁定文件的进程:" -ForegroundColor Yellow
        $lockedBy | Format-Table -AutoSize
        Write-Host "`n请关闭这些进程后重试" -ForegroundColor Red
    } else {
        Write-Host "未找到明显锁定文件的进程" -ForegroundColor Green
    }
} catch {
    Write-Host "无法检查进程: $_" -ForegroundColor Yellow
}

# 方案1: 尝试直接重命名
Write-Host "`n方案1: 尝试直接重命名..." -ForegroundColor Yellow
if (Test-Path $oldFile) {
    try {
        Rename-Item -Path $oldFile -NewName $backupFile -Force -ErrorAction Stop
        Write-Host "成功重命名旧文件为: $backupFile" -ForegroundColor Green
    } catch {
        Write-Host "无法重命名旧文件: $_" -ForegroundColor Red
        Write-Host "尝试方案2..." -ForegroundColor Yellow
    }
}

# 方案2: 复制内容而不是重命名
Write-Host "`n方案2: 复制文件内容..." -ForegroundColor Yellow
try {
    # 读取新文件内容
    $newContent = Get-Content -Path $newFile -Raw
    
    # 写入到目标文件
    Set-Content -Path $oldFile -Value $newContent -Force -ErrorAction Stop
    
    Write-Host "成功将新内容写入 $oldFile" -ForegroundColor Green
    
    # 可选: 删除新文件
    Remove-Item -Path $newFile -Force
    Write-Host "已删除 $newFile" -ForegroundColor Green
    
} catch {
    Write-Host "无法写入文件: $_" -ForegroundColor Red
    Write-Host "`n方案3: 创建替代文件..." -ForegroundColor Yellow
    
    # 方案3: 创建临时替代文件
    $tempFile = Join-Path $workflowDir "ci-cd-temp.yml"
    Set-Content -Path $tempFile -Value $newContent -Force
    Write-Host "创建了临时文件: $tempFile" -ForegroundColor Yellow
    Write-Host "请手动重命名或替换原文件" -ForegroundColor Yellow
}

# 验证结果
Write-Host "`n验证结果:" -ForegroundColor Cyan
if (Test-Path $oldFile) {
    $fileSize = (Get-Item $oldFile).Length
    $lineCount = (Get-Content $oldFile).Count
    Write-Host "SUCCESS: $oldFile exists ($fileSize bytes, $lineCount lines)" -ForegroundColor Green
    
    # 检查是否包含质量门
    $content = Get-Content $oldFile -Raw
    if ($content -match "quality-gates-assessment") {
        Write-Host "SUCCESS: Contains quality gates assessment job" -ForegroundColor Green
    } else {
        Write-Host "ERROR: Does not contain quality gates assessment job" -ForegroundColor Red
    }
} else {
    Write-Host "ERROR: $oldFile does not exist" -ForegroundColor Red
}

Write-Host "`nDone!" -ForegroundColor Cyan
Write-Host "If problems persist, try:" -ForegroundColor Yellow
Write-Host "1. Restart computer" -ForegroundColor Yellow
Write-Host "2. Close all IDEs and editors" -ForegroundColor Yellow
Write-Host "3. Manually copy file content" -ForegroundColor Yellow