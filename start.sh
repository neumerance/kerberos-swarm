#!/bin/bash

# Quick start script for Kerberos.io Multi-Agent deployment
# This script generates the compose file and starts all agents

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[KERBEROS]${NC} $1"
}

print_header "Kerberos.io Multi-Agent Quick Start"

print_status "Step 1: Generating docker-compose file..."
./generate-compose.sh

print_status "Step 2: Starting all agents..."
./manage.sh start

print_header "Quick start completed!"
print_status "Use './manage.sh status' to check agent status"
print_status "Use './manage.sh logs' to view logs"
