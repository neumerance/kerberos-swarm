#!/bin/bash

# Cross-platform installer for Kerberos.io Multi-Agent CLI
# Works on macOS, Linux, and Windows (via WSL/Git Bash)

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[KERBEROS]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[i]${NC} $1"
}

# Detect OS
detect_os() {
    case "$(uname -s)" in
        Darwin*)    OS="macOS";;
        Linux*)     OS="Linux";;
        CYGWIN*|MINGW32*|MSYS*|MINGW*)    OS="Windows";;
        *)          OS="Unknown";;
    esac
}

# Check Python installation
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        python_version=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
        print_status "Python found: $python_version"
    elif command -v python &> /dev/null; then
        python_version=$(python --version 2>&1)
        if [[ $python_version == *"Python 3"* ]]; then
            PYTHON_CMD="python"
            print_status "Python found: $python_version"
        else
            print_error "Python 3.7+ required, found: $python_version"
            exit 1
        fi
    else
        print_error "Python not found"
        print_info "Install Python 3.7+ from: https://python.org/downloads/"
        exit 1
    fi
}

# Check pip installation
check_pip() {
    if command -v pip3 &> /dev/null; then
        PIP_CMD="pip3"
    elif command -v pip &> /dev/null; then
        PIP_CMD="pip"
    else
        print_error "pip not found"
        print_info "Install pip or use: $PYTHON_CMD -m pip"
        exit 1
    fi
    print_status "pip found: $PIP_CMD"
}

# Install Python dependencies
install_dependencies() {
    print_info "Installing Python dependencies..."
    
    if [[ -f "requirements.txt" ]]; then
        $PIP_CMD install -r requirements.txt
    else
        $PIP_CMD install click PyYAML rich docker ipaddress
    fi
    
    print_status "Dependencies installed"
}

# Install the CLI globally
install_cli() {
    print_info "Installing Kerberos CLI globally..."
    
    # Try pip installation first
    if [[ -f "setup.py" ]]; then
        if $PIP_CMD install -e . 2>/dev/null; then
            print_status "CLI installed globally as 'kerberos' command via pip"
            return 0
        else
            print_warning "Pip installation failed, falling back to manual installation"
        fi
    fi
    
    # Manual installation - create wrapper script
    if [[ "$OS" == "Windows" ]]; then
        create_windows_wrapper
    else
        create_unix_wrapper
    fi
}

# Create Unix wrapper (macOS/Linux)
create_unix_wrapper() {
    local install_dir
    local project_dir="$(pwd)"
    
    # Try to find a good installation directory
    if [[ -d "$HOME/.local/bin" ]]; then
        install_dir="$HOME/.local/bin"
    elif [[ -d "/usr/local/bin" ]] && [[ -w "/usr/local/bin" ]]; then
        install_dir="/usr/local/bin"
    else
        install_dir="$HOME/bin"
        mkdir -p "$install_dir"
    fi
    
    print_info "Installing to: $install_dir"
    
    # Create the global kerberos script
    cat > "$install_dir/kerberos" << EOF
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Project directory (where the actual CLI files are)
PROJECT_DIR = Path("$project_dir")
KERBEROS_LITE = PROJECT_DIR / "kerberos_lite.py"

if KERBEROS_LITE.exists():
    # Run the CLI with all arguments
    subprocess.run([sys.executable, str(KERBEROS_LITE)] + sys.argv[1:])
else:
    print("Error: Kerberos CLI not found at $project_dir")
    print("Please ensure the kerberos-swarms project is at the expected location")
    sys.exit(1)
EOF
    
    chmod +x "$install_dir/kerberos"
    print_status "CLI wrapper created: $install_dir/kerberos"
    
    # Check if directory is in PATH
    if [[ ":$PATH:" == *":$install_dir:"* ]]; then
        print_status "Directory is in PATH - you can use 'kerberos' command"
    else
        print_warning "Add $install_dir to your PATH:"
        echo ""
        echo "  # Add this to your ~/.bashrc or ~/.zshrc:"
        echo "  export PATH=\"$install_dir:\$PATH\""
        echo ""
        echo "  # Then reload your shell:"
        echo "  source ~/.bashrc   # or source ~/.zshrc"
        echo ""
        print_info "Or use full path: $install_dir/kerberos"
    fi
}

# Create Windows wrapper
create_windows_wrapper() {
    local project_dir="$(pwd)"
    
    # Create batch file
    cat > "kerberos.bat" << EOF
@echo off
$PYTHON_CMD "%~dp0kerberos_lite.py" %*
EOF
    
    print_status "Windows batch file created: kerberos.bat"
    print_info "You can now use: kerberos --help"
    print_info "Add this directory to your PATH to use 'kerberos' globally"
    
    # Also create PowerShell script
    cat > "kerberos.ps1" << EOF
#!/usr/bin/env pwsh
& $PYTHON_CMD "\$PSScriptRoot\\kerberos_lite.py" \$args
EOF
    
    print_status "PowerShell script created: kerberos.ps1"
}

# Create development setup
setup_development() {
    print_info "Setting up development environment..."
    
    # Make Python file executable
    chmod +x kerberos_cli.py
    
    # Create virtual environment (optional)
    if [[ "$1" == "--venv" ]]; then
        print_info "Creating virtual environment..."
        $PYTHON_CMD -m venv venv
        
        if [[ "$OS" == "Windows" ]]; then
            source venv/Scripts/activate
        else
            source venv/bin/activate
        fi
        
        print_status "Virtual environment activated"
    fi
    
    install_dependencies
}

# Main installation
main() {
    print_header "Kerberos.io Multi-Agent CLI Installer"
    print_info "Detected OS: $OS"
    echo ""
    
    check_python
    check_pip
    
    # Parse arguments
    case "${1:-install}" in
        "install")
            install_dependencies
            install_cli
            ;;
        "dev"|"development")
            setup_development "$2"
            ;;
        "deps"|"dependencies")
            install_dependencies
            ;;
        *)
            echo "Usage: $0 [install|dev|deps]"
            echo ""
            echo "  install      - Install CLI globally (default)"
            echo "  dev          - Setup for development"
            echo "  deps         - Install dependencies only"
            echo ""
            exit 1
            ;;
    esac
    
    echo ""
    print_header "Installation completed!"
    print_info "Kerberos.io Multi-Agent CLI is ready!"
    echo ""
    print_status "Next steps:"
    print_info "1. Test the CLI: kerberos --help (or use full path if not in PATH)"
    print_info "2. Check system: kerberos check"  
    print_info "3. Configure cameras in config.yml"
    print_info "4. Deploy agents: kerberos start"
    echo ""
    print_info "For help: kerberos --help"
    print_info "Documentation: cat README.md"
}

# Detect OS and run
detect_os
main "$@"
