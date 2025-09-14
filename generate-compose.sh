#!/bin/bash

# Kerberos.io Multi-Agent Docker Compose Generator
# This script reads the config.yml file and generates a docker-compose.yml

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration file
CONFIG_FILE="config.yml"
OUTPUT_FILE="docker-compose.yml"

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

# Function to check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v yq &> /dev/null; then
        print_error "yq is required but not installed."
        print_status "Install yq with: brew install yq (macOS) or snap install yq (Linux)"
        exit 1
    fi
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is required but not installed."
        exit 1
    fi
    
    print_status "All dependencies found."
}

# Function to parse IP range and generate IP list
generate_ip_list() {
    local start_ip="$1"
    local end_ip="$2"
    
    # Extract the base IP and last octet
    local base_ip=$(echo "$start_ip" | cut -d. -f1-3)
    local start_octet=$(echo "$start_ip" | cut -d. -f4)
    local end_octet=$(echo "$end_ip" | cut -d. -f4)
    
    local ip_list=()
    for ((i=start_octet; i<=end_octet; i++)); do
        ip_list+=("${base_ip}.${i}")
    done
    
    echo "${ip_list[@]}"
}

# Function to generate docker-compose.yml
generate_compose() {
    local config_file="$1"
    
    print_status "Reading configuration from $config_file"
    
    # Check if config file exists
    if [[ ! -f "$config_file" ]]; then
        print_error "Configuration file '$config_file' not found!"
        exit 1
    fi
    
    # Extract configuration values
    local kerberos_image=$(yq eval '.global.kerberos_image' "$config_file")
    local network_name=$(yq eval '.global.network_name' "$config_file")
    local config_base_path=$(yq eval '.global.config_base_path' "$config_file")
    local recordings_base_path=$(yq eval '.global.recordings_base_path' "$config_file")
    
    local start_ip=$(yq eval '.cameras.ip_range.start' "$config_file")
    local end_ip=$(yq eval '.cameras.ip_range.end' "$config_file")
    
    local protocol=$(yq eval '.cameras.connection.protocol' "$config_file")
    local port=$(yq eval '.cameras.connection.port' "$config_file")
    local username=$(yq eval '.cameras.connection.username' "$config_file")
    local password=$(yq eval '.cameras.connection.password' "$config_file")
    local stream_path=$(yq eval '.cameras.connection.stream_path' "$config_file")
    
    local web_port_start=$(yq eval '.docker.web_port_start' "$config_file")
    local rtmp_port_start=$(yq eval '.docker.rtmp_port_start' "$config_file")
    local restart_policy=$(yq eval '.docker.restart_policy' "$config_file")
    
    # Optional resource limits
    local memory_limit=$(yq eval '.docker.limits.memory' "$config_file")
    local cpu_limit=$(yq eval '.docker.limits.cpus' "$config_file")
    
    # Custom environment variables
    local timezone=$(yq eval '.custom_environment.TZ // "UTC"' "$config_file")
    
    print_status "Generating IP list from $start_ip to $end_ip"
    local ip_array=($(generate_ip_list "$start_ip" "$end_ip"))
    local camera_count=${#ip_array[@]}
    
    print_status "Found $camera_count cameras to configure"
    
    # Start generating docker-compose.yml
    print_status "Generating $OUTPUT_FILE..."
    
    cat > "$OUTPUT_FILE" << EOF
# Generated docker-compose.yml for Kerberos.io Multi-Agent Setup
# Generated on: $(date)
# Camera count: $camera_count
# IP range: $start_ip - $end_ip

version: '3.8'

networks:
  $network_name:
    driver: bridge

services:
EOF
    
    # Generate each camera service
    local web_port=$web_port_start
    local rtmp_port=$rtmp_port_start
    
    for i in "${!ip_array[@]}"; do
        local camera_ip="${ip_array[i]}"
        local camera_name="camera-$(echo "$camera_ip" | tr '.' '-')"
        local rtsp_url="${protocol}://${username}:${password}@${camera_ip}:${port}${stream_path}"
        
        print_status "Configuring $camera_name ($camera_ip) - Web: $web_port, RTMP: $rtmp_port"
        
        cat >> "$OUTPUT_FILE" << EOF

  $camera_name:
    image: $kerberos_image
    container_name: $camera_name
    restart: $restart_policy
    networks:
      - $network_name
    ports:
      - "$web_port:80"
      - "$rtmp_port:1935"
    volumes:
      - "$config_base_path/$camera_name:/home/agent/data/config"
      - "$recordings_base_path/$camera_name:/home/agent/data/recordings"
    environment:
      - TZ=$timezone
      - AGENT_NAME=$camera_name
      - AGENT_CAPTURE_IPCAMERA_RTSP=$rtsp_url
      - AGENT_CAPTURE_IPCAMERA_SUB_RTSP=$rtsp_url
      - AGENT_STREAM_WEBRTC=true
      - AGENT_STREAM_RECORDING=true
EOF

        # Add resource limits if specified
        if [[ "$memory_limit" != "null" ]] || [[ "$cpu_limit" != "null" ]]; then
            cat >> "$OUTPUT_FILE" << EOF
    deploy:
      resources:
        limits:
EOF
            if [[ "$memory_limit" != "null" ]]; then
                cat >> "$OUTPUT_FILE" << EOF
          memory: $memory_limit
EOF
            fi
            if [[ "$cpu_limit" != "null" ]]; then
                cat >> "$OUTPUT_FILE" << EOF
          cpus: '$cpu_limit'
EOF
            fi
        fi
        
        ((web_port++))
        ((rtmp_port++))
    done
    
    print_status "Docker Compose file generated successfully!"
    print_status "Services created: $camera_count"
    print_status "Web ports: $web_port_start-$((web_port-1))"
    print_status "RTMP ports: $rtmp_port_start-$((rtmp_port-1))"
    
    # Create necessary directories
    print_status "Creating configuration and recording directories..."
    mkdir -p "$config_base_path" "$recordings_base_path"
    
    for i in "${!ip_array[@]}"; do
        local camera_ip="${ip_array[i]}"
        local camera_name="camera-$(echo "$camera_ip" | tr '.' '-')"
        mkdir -p "$config_base_path/$camera_name"
        mkdir -p "$recordings_base_path/$camera_name"
    done
}

# Function to display usage
usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --config FILE    Configuration file (default: config.yml)"
    echo "  -o, --output FILE    Output file (default: docker-compose.yml)"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                            # Use default config.yml"
    echo "  $0 -c my-config.yml          # Use custom config file"
    echo "  $0 -c config.yml -o compose.yml    # Custom output file"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--config)
            CONFIG_FILE="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FILE="$2"
            shift 2
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Main execution
print_header "Kerberos.io Multi-Agent Docker Compose Generator"
print_status "Configuration file: $CONFIG_FILE"
print_status "Output file: $OUTPUT_FILE"

check_dependencies
generate_compose "$CONFIG_FILE"

print_header "Generation completed!"
print_status "Next steps:"
print_status "1. Review the generated $OUTPUT_FILE"
print_status "2. Run: docker-compose up -d"
print_status "3. Access web interfaces starting from port $web_port_start"
