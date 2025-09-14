# Kerberos.io Multi-Agent CLI Installer for Windows PowerShell
# Run this from PowerShell with: .\install.ps1

Write-Host "[KERBEROS] Installing Kerberos.io Multi-Agent CLI for Windows" -ForegroundColor Blue
Write-Host ""

# Check Python installation
try {
    $pythonVersion = python --version 2>$null
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host "[INFO] Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python not found. Please install Python 3.7+ from https://python.org/downloads/" -ForegroundColor Red
    Write-Host "Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check pip
try {
    python -m pip --version | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "pip not found"
    }
    Write-Host "[INFO] pip found" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] pip not found" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Install dependencies
Write-Host "[INFO] Installing dependencies..." -ForegroundColor Blue

try {
    if (Test-Path "requirements.txt") {
        python -m pip install -r requirements.txt
    } else {
        python -m pip install click PyYAML rich docker ipaddress
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
    
    Write-Host "[SUCCESS] Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Try global installation
Write-Host "[INFO] Attempting global installation..." -ForegroundColor Blue

try {
    if (Test-Path "setup.py") {
        python -m pip install -e .
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[SUCCESS] CLI installed globally as 'kerberos' command" -ForegroundColor Green
            Write-Host "[INFO] Test with: kerberos --help" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "[KERBEROS] Installation completed!" -ForegroundColor Blue
            Write-Host "[INFO] Configure your cameras in config.yml" -ForegroundColor Cyan
            Write-Host "[INFO] Then run: kerberos generate" -ForegroundColor Cyan
            Read-Host "Press Enter to exit"
            exit 0
        }
    }
} catch {
    # Continue to batch file creation
}

# Create batch wrapper as fallback
Write-Host "[INFO] Creating batch wrapper..." -ForegroundColor Blue

$batchContent = @"
@echo off
python "%~dp0kerberos_lite.py" %*
"@

Set-Content -Path "kerberos.bat" -Value $batchContent

$psContent = @"
#!/usr/bin/env pwsh
& python "$PSScriptRoot\kerberos_lite.py" $args
"@

Set-Content -Path "kerberos.ps1" -Value $psContent

Write-Host "[SUCCESS] Windows batch file created: kerberos.bat" -ForegroundColor Green
Write-Host "[SUCCESS] PowerShell script created: kerberos.ps1" -ForegroundColor Green
Write-Host "[INFO] You can now use: kerberos --help" -ForegroundColor Cyan
Write-Host "[INFO] Or: python kerberos_lite.py --help" -ForegroundColor Cyan

Write-Host ""
Write-Host "[KERBEROS] Installation completed!" -ForegroundColor Blue
Write-Host "[INFO] Configure your cameras in config.yml" -ForegroundColor Cyan
Write-Host "[INFO] Then run: kerberos generate" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
