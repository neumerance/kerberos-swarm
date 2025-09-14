@echo off
REM Kerberos.io Multi-Agent CLI Installer for Windows
REM Run this from Command Prompt or PowerShell

echo [KERBEROS] Installing Kerberos.io Multi-Agent CLI for Windows
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.7+ from https://python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

echo [INFO] Python found
python --version

REM Check if pip is available
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] pip not found
    pause
    exit /b 1
)

echo [INFO] pip found

REM Install dependencies
echo [INFO] Installing dependencies...
if exist requirements.txt (
    python -m pip install -r requirements.txt
) else (
    python -m pip install click PyYAML rich docker ipaddress
)

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies
    pause
    exit /b 1
)

echo [SUCCESS] Dependencies installed

REM Try global installation first
echo [INFO] Attempting global installation...
if exist setup.py (
    python -m pip install -e .
    if %errorlevel% eq 0 (
        echo [SUCCESS] CLI installed globally as 'kerberos' command
        echo [INFO] Test with: kerberos --help
        goto :end
    )
)

REM Create batch wrapper as fallback
echo [INFO] Creating batch wrapper...
echo @echo off > kerberos.bat
echo python "%%~dp0kerberos_lite.py" %%* >> kerberos.bat

echo [SUCCESS] Windows batch file created: kerberos.bat
echo [INFO] You can now use: kerberos --help
echo [INFO] Or: python kerberos_lite.py --help

REM Also create PowerShell script
echo #!/usr/bin/env pwsh > kerberos.ps1
echo ^& python "$PSScriptRoot\kerberos_lite.py" $args >> kerberos.ps1

echo [SUCCESS] PowerShell script created: kerberos.ps1

:end
echo.
echo [KERBEROS] Installation completed!
echo [INFO] Configure your cameras in config.yml
echo [INFO] Then run: kerberos generate
pause
