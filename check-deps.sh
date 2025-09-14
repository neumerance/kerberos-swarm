#!/bin/bash

# Dependency checker for Kerberos.io Multi-Agent project

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

check_docker() {
    if command -v docker &> /dev/null; then
        local docker_version=$(docker --version | cut -d' ' -f3 | cut -d',' -f1)
        print_status "Docker found (version: $docker_version)"
        
        # Check if Docker daemon is running
        if docker info &> /dev/null; then
            print_status "Docker daemon is running"
        else
            print_error "Docker daemon is not running"
            print_info "Start Docker daemon and try again"
            return 1
        fi
    else
        print_error "Docker not found"
        print_info "Install Docker from: https://docs.docker.com/get-docker/"
        return 1
    fi
}

check_docker_compose() {
    if command -v docker-compose &> /dev/null; then
        local compose_version=$(docker-compose --version | cut -d' ' -f3 | cut -d',' -f1)
        print_status "Docker Compose found (version: $compose_version)"
    elif docker compose version &> /dev/null 2>&1; then
        local compose_version=$(docker compose version --short)
        print_status "Docker Compose (plugin) found (version: $compose_version)"
        print_info "Consider using 'docker compose' instead of 'docker-compose'"
    else
        print_error "Docker Compose not found"
        print_info "Install Docker Compose from: https://docs.docker.com/compose/install/"
        return 1
    fi
}

check_yq() {
    if command -v yq &> /dev/null; then
        local yq_version=$(yq --version | cut -d' ' -f4)
        print_status "yq found (version: $yq_version)"
    else
        print_error "yq not found"
        print_info "Install yq:"
        print_info "  macOS: brew install yq"
        print_info "  Linux: snap install yq"
        print_info "  Or download from: https://github.com/mikefarah/yq/releases"
        return 1
    fi
}

check_network_connectivity() {
    print_info "Checking network connectivity..."
    
    # Test if we can reach Docker Hub
    if curl -s --connect-timeout 5 https://index.docker.io/v1/ &> /dev/null; then
        print_status "Docker Hub connectivity: OK"
    else
        print_warning "Cannot reach Docker Hub - image pulls may fail"
    fi
}

check_permissions() {
    print_info "Checking file permissions..."
    
    local current_dir=$(pwd)
    if [[ -w "$current_dir" ]]; then
        print_status "Write permissions: OK"
    else
        print_error "No write permissions in current directory"
        return 1
    fi
}

check_config_file() {
    if [[ -f "config.yml" ]]; then
        print_status "Configuration file found: config.yml"
        
        # Basic YAML validation
        if command -v yq &> /dev/null; then
            if yq eval '.' config.yml &> /dev/null; then
                print_status "Configuration file is valid YAML"
            else
                print_error "Configuration file has YAML syntax errors"
                return 1
            fi
        fi
    else
        print_warning "Configuration file not found: config.yml"
        if [[ -f "config.example.yml" ]]; then
            print_info "Example file available: config.example.yml"
            print_info "Copy it to config.yml and modify for your setup"
        fi
    fi
}

check_system_resources() {
    print_info "Checking system resources..."
    
    # Check available disk space
    local available_space=$(df . | tail -1 | awk '{print $4}')
    local available_gb=$((available_space / 1024 / 1024))
    
    if [[ $available_gb -gt 10 ]]; then
        print_status "Disk space: ${available_gb}GB available"
    else
        print_warning "Low disk space: only ${available_gb}GB available"
        print_info "Consider freeing up space for recordings"
    fi
    
    # Check memory (Linux/macOS)
    if command -v free &> /dev/null; then
        local total_mem=$(free -g | awk '/^Mem:/{print $2}')
        if [[ $total_mem -gt 4 ]]; then
            print_status "Memory: ${total_mem}GB total"
        else
            print_warning "Limited memory: ${total_mem}GB total"
            print_info "Consider reducing agent resource limits"
        fi
    fi
}

show_summary() {
    print_header "System Check Summary"
    echo ""
    print_info "If all checks passed, you're ready to:"
    print_info "1. Configure cameras in config.yml"
    print_info "2. Run ./start.sh to deploy agents"
    print_info "3. Access web interfaces starting from port 8080"
    echo ""
    print_info "For help: ./manage.sh help"
}

# Main execution
print_header "Kerberos.io Multi-Agent System Check"
echo ""

error_count=0

check_docker || ((error_count++))
check_docker_compose || ((error_count++))
check_yq || ((error_count++))
check_network_connectivity
check_permissions || ((error_count++))
check_config_file
check_system_resources

echo ""

if [[ $error_count -eq 0 ]]; then
    print_header "✓ All critical dependencies satisfied!"
    show_summary
else
    print_error "$error_count critical issue(s) found"
    print_info "Please resolve the issues above before proceeding"
    exit 1
fi
