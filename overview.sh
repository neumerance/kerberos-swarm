#!/bin/bash

# Project overview and help script

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}[KERBEROS]${NC} $1"
}

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_command() {
    echo -e "${YELLOW}$1${NC}"
}

clear

print_header "🔒 Kerberos.io Multi-Agent Deployment System"
echo ""
echo "This project helps you deploy multiple Kerberos.io agents for CCTV monitoring"
echo "based on IP address ranges defined in YAML configuration."
echo ""

print_header "📁 Available Files:"
echo ""
print_info "Configuration:"
echo "  • config.yml           - Main configuration file (customize your cameras)"
echo "  • config.example.yml   - Example configuration for reference"
echo ""
print_info "Scripts:"
echo "  • generate-compose.sh  - Generate docker-compose.yml from config"
echo "  • manage.sh           - Full management interface"
echo "  • start.sh            - Quick start (generate + deploy)"
echo "  • stop.sh             - Quick stop all agents"
echo "  • check-deps.sh       - Check system dependencies"
echo "  • overview.sh         - This help screen"
echo ""
print_info "Documentation:"
echo "  • README.md           - Complete documentation"
echo ""

print_header "🚀 Quick Start Guide:"
echo ""
echo "1. Check dependencies:"
print_command "   ./check-deps.sh"
echo ""
echo "2. Configure your cameras in config.yml (example provided)"
print_command "   nano config.yml"
echo ""
echo "3. Deploy all agents:"
print_command "   ./start.sh"
echo ""
echo "4. Check status:"
print_command "   ./manage.sh status"
echo ""
echo "5. Stop all agents:"
print_command "   ./stop.sh"
echo ""

print_header "📋 Management Commands:"
echo ""
print_command "  ./manage.sh start      " && echo " # Start all agents"
print_command "  ./manage.sh stop       " && echo " # Stop all agents"  
print_command "  ./manage.sh restart    " && echo " # Restart all agents"
print_command "  ./manage.sh status     " && echo " # Show status"
print_command "  ./manage.sh logs       " && echo " # View all logs"
print_command "  ./manage.sh update     " && echo " # Update to latest version"
print_command "  ./manage.sh redeploy   " && echo " # Regenerate config and restart"
print_command "  ./manage.sh cleanup    " && echo " # Remove everything"
echo ""

print_header "📹 Default Configuration:"
echo ""
if [[ -f "config.yml" ]] && command -v yq &> /dev/null; then
    local start_ip=$(yq eval '.cameras.ip_range.start' config.yml 2>/dev/null || echo "Not set")
    local end_ip=$(yq eval '.cameras.ip_range.end' config.yml 2>/dev/null || echo "Not set")
    local web_port=$(yq eval '.docker.web_port_start' config.yml 2>/dev/null || echo "8080")
    
    echo "  • Camera IP range: $start_ip → $end_ip"
    echo "  • Web interfaces start from: http://localhost:$web_port"
else
    echo "  • Configure your cameras in config.yml first"
fi
echo ""

print_header "🆘 Need Help?"
echo ""
echo "  • Read the full documentation: cat README.md"
echo "  • Check dependencies: ./check-deps.sh"
echo "  • View example config: cat config.example.yml"
echo "  • Command help: ./manage.sh help"
echo ""

print_header "Happy monitoring! 📹🔒"
