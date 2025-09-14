#!/bin/bash

# Kerberos.io Multi-Agent Deployment Manager
# This script helps start, stop, and manage the Kerberos agents deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CONFIG_FILE="config.yml"
COMPOSE_FILE="docker-compose.yml"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[KERBEROS]${NC} $1"
}

# Function to check if docker-compose file exists
check_compose_file() {
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        print_error "Docker compose file '$COMPOSE_FILE' not found!"
        print_status "Run './generate-compose.sh' first to generate the compose file."
        exit 1
    fi
}

# Function to start all agents
start_agents() {
    print_header "Starting Kerberos Agents..."
    check_compose_file
    
    print_status "Starting all agents in background..."
    docker-compose up -d
    
    print_status "Waiting for services to be ready..."
    sleep 10
    
    print_status "Checking service status..."
    docker-compose ps
    
    # Get web port start from config
    if [[ -f "$CONFIG_FILE" ]] && command -v yq &> /dev/null; then
        local web_port_start=$(yq eval '.docker.web_port_start' "$CONFIG_FILE")
        print_header "Agents started successfully!"
        print_status "Web interfaces available starting from: http://localhost:$web_port_start"
    else
        print_header "Agents started successfully!"
        print_status "Check docker-compose ps for port mappings"
    fi
}

# Function to stop all agents
stop_agents() {
    print_header "Stopping Kerberos Agents..."
    check_compose_file
    
    print_status "Stopping all agents..."
    docker-compose down
    
    print_header "All agents stopped successfully!"
}

# Function to restart all agents
restart_agents() {
    print_header "Restarting Kerberos Agents..."
    stop_agents
    sleep 5
    start_agents
}

# Function to show status
show_status() {
    print_header "Kerberos Agents Status"
    check_compose_file
    
    print_status "Container status:"
    docker-compose ps
    
    echo ""
    print_status "Resource usage:"
    docker-compose top
}

# Function to show logs
show_logs() {
    local service="$1"
    check_compose_file
    
    if [[ -n "$service" ]]; then
        print_header "Logs for service: $service"
        docker-compose logs -f "$service"
    else
        print_header "Logs for all services"
        docker-compose logs -f
    fi
}

# Function to update agents
update_agents() {
    print_header "Updating Kerberos Agents..."
    check_compose_file
    
    print_status "Pulling latest images..."
    docker-compose pull
    
    print_status "Recreating containers with new images..."
    docker-compose up -d --force-recreate
    
    print_header "Update completed!"
}

# Function to clean up (remove containers and volumes)
cleanup() {
    print_header "Cleaning up Kerberos Agents..."
    check_compose_file
    
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Stopping and removing containers, networks, and volumes..."
        docker-compose down -v --remove-orphans
        
        print_status "Removing dangling images..."
        docker image prune -f
        
        print_header "Cleanup completed!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Function to regenerate compose file and restart
redeploy() {
    print_header "Redeploying Kerberos Agents..."
    
    print_status "Stopping current deployment..."
    if [[ -f "$COMPOSE_FILE" ]]; then
        docker-compose down
    fi
    
    print_status "Regenerating docker-compose file..."
    ./generate-compose.sh
    
    print_status "Starting new deployment..."
    start_agents
    
    print_header "Redeployment completed!"
}

# Function to display usage
usage() {
    echo "Kerberos.io Multi-Agent Deployment Manager"
    echo ""
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start                 Start all Kerberos agents"
    echo "  stop                  Stop all Kerberos agents"
    echo "  restart               Restart all Kerberos agents"
    echo "  status                Show status of all agents"
    echo "  logs [SERVICE]        Show logs (optionally for specific service)"
    echo "  update                Update agents to latest version"
    echo "  cleanup               Remove all containers and volumes"
    echo "  redeploy              Regenerate compose file and restart"
    echo "  help                  Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start all agents"
    echo "  $0 logs camera-10-19-19-30  # Show logs for specific camera"
    echo "  $0 status                   # Show status of all agents"
}

# Main execution
case "${1:-}" in
    start)
        start_agents
        ;;
    stop)
        stop_agents
        ;;
    restart)
        restart_agents
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    update)
        update_agents
        ;;
    cleanup)
        cleanup
        ;;
    redeploy)
        redeploy
        ;;
    help|--help|-h)
        usage
        ;;
    "")
        print_error "No command specified."
        echo ""
        usage
        exit 1
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        usage
        exit 1
        ;;
esac
