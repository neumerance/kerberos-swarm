#!/bin/bash

# Kerberos CLI Global Installer
# This script installs the kerberos command globally

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Get current directory (where the project is)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Find a suitable installation directory
find_install_dir() {
    local install_dirs=(
        "$HOME/.local/bin"
        "$HOME/bin"
        "/usr/local/bin"
    )
    
    for dir in "${install_dirs[@]}"; do
        if [[ -d "$dir" ]] && [[ -w "$dir" ]]; then
            echo "$dir"
            return 0
        fi
    done
    
    # Create ~/.local/bin if it doesn't exist
    mkdir -p "$HOME/.local/bin"
    echo "$HOME/.local/bin"
}

# Install the CLI globally
install_cli() {
    local install_dir
    install_dir=$(find_install_dir)
    
    print_info "Installing kerberos CLI to: $install_dir"
    
    # Create the global kerberos script
    cat > "$install_dir/kerberos" << EOF
#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path

# Project directory (where the actual CLI files are)
PROJECT_DIR = Path("$PROJECT_DIR")
KERBEROS_LITE = PROJECT_DIR / "kerberos_lite.py"

if KERBEROS_LITE.exists():
    # Run the CLI with all arguments
    subprocess.run([sys.executable, str(KERBEROS_LITE)] + sys.argv[1:])
else:
    print("Error: Kerberos CLI not found at $PROJECT_DIR")
    print("Please run this installer from the kerberos-swarms directory")
    sys.exit(1)
EOF
    
    # Make it executable
    chmod +x "$install_dir/kerberos"
    
    print_status "Kerberos CLI installed to: $install_dir/kerberos"
    
    # Check if directory is in PATH
    if [[ ":$PATH:" == *":$install_dir:"* ]]; then
        print_status "Directory is already in PATH"
        print_info "You can now use: kerberos --help"
    else
        print_warning "Directory not in PATH. Add this line to your ~/.bashrc or ~/.zshrc:"
        echo "export PATH=\"$install_dir:\$PATH\""
        print_info "Then run: source ~/.bashrc (or ~/.zshrc)"
        print_info "Or use full path: $install_dir/kerberos --help"
    fi
}

# Uninstall function
uninstall_cli() {
    local install_dirs=(
        "$HOME/.local/bin/kerberos"
        "$HOME/bin/kerberos"
        "/usr/local/bin/kerberos"
    )
    
    local removed=0
    for file in "${install_dirs[@]}"; do
        if [[ -f "$file" ]]; then
            rm "$file"
            print_status "Removed: $file"
            ((removed++))
        fi
    done
    
    if [[ $removed -eq 0 ]]; then
        print_info "No kerberos CLI installations found"
    else
        print_status "Uninstall completed"
    fi
}

# Main script
case "${1:-install}" in
    install)
        echo -e "${BLUE}[KERBEROS] Installing Global CLI${NC}"
        echo ""
        install_cli
        echo ""
        print_status "Installation completed!"
        print_info "Test with: kerberos --help"
        ;;
    uninstall)
        echo -e "${BLUE}[KERBEROS] Uninstalling Global CLI${NC}"
        echo ""
        uninstall_cli
        ;;
    *)
        echo "Usage: $0 [install|uninstall]"
        echo ""
        echo "  install    - Install kerberos command globally (default)"
        echo "  uninstall  - Remove kerberos command"
        ;;
esac
