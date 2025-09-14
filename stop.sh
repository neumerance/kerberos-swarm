#!/bin/bash

# Quick stop script for Kerberos.io Multi-Agent deployment

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

print_header "Kerberos.io Multi-Agent Quick Stop"

./manage.sh stop

print_header "All agents stopped!"
