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
    
    if [[ -f "setup.py" ]]; then
        $PIP_CMD install -e .
        print_status "CLI installed globally as 'kerberos' command"
    else
        print_warning "setup.py not found, creating manual installation..."
        
        # Create a wrapper script
        if [[ "$OS" == "Windows" ]]; then
            create_windows_wrapper
        else
            create_unix_wrapper
        fi
    fi
}

# Create Unix wrapper (macOS/Linux)
create_unix_wrapper() {
    local install_dir
    
    # Try to find a good installation directory
    if [[ -d "$HOME/.local/bin" ]]; then
        install_dir="$HOME/.local/bin"
    elif [[ -d "/usr/local/bin" ]] && [[ -w "/usr/local/bin" ]]; then
        install_dir="/usr/local/bin"
    else
        install_dir="$HOME/bin"
        mkdir -p "$install_dir"
    fi
    
    cat > "$install_dir/kerberos" << EOF
#!/bin/bash
$PYTHON_CMD "$(pwd)/kerberos_cli.py" "\$@"
EOF
    
    chmod +x "$install_dir/kerberos"
    print_status "CLI wrapper created: $install_dir/kerberos"
    
    # Check if directory is in PATH
    if [[ ":$PATH:" == *":$install_dir:"* ]]; then
        print_status "Directory is in PATH"
    else
        print_warning "Add $install_dir to your PATH:"
        echo "export PATH=\"$install_dir:\$PATH\""
    fi
}

# Create Windows wrapper
create_windows_wrapper() {
    cat > "kerberos.bat" << EOF
@echo off
$PYTHON_CMD "%~dp0kerberos_cli.py" %*
EOF
    
    print_status "Windows batch file created: kerberos.bat"
    print_info "Add this directory to your PATH to use 'kerberos' globally"
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
    print_info "Test the CLI with: kerberos --help"
    print_info "Or run directly: python3 kerberos_cli.py --help"
}

# Detect OS and run
detect_os
main "$@"
