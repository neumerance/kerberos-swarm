# Kerberos.io Multi-Agent Deployment

A configurable, cross-platform CLI tool for deploying multiple Kerberos.io agents using Docker Compose, designed to monitor multiple CCTV cameras with automated configuration based on IP ranges.

## Overview

This project allows you to:
- **Cross-platform CLI tool** - Works on Windows, macOS, and Linux
- Configure multiple Kerberos.io agents using a single YAML configuration file
- Automatically generate Docker Compose configurations for IP address ranges
- Manage all camera agents with a modern CLI interface
- Organize configurations and recordings in structured directories
- Rich terminal output with colors and progress indicators

## Prerequisites

- **Python 3.7+** - Download from [python.org](https://python.org/downloads/)
- **Docker** and **Docker Compose** installed
- **pip** (Python package installer)

## Quick Start

### Option 1: Automated Installation

**Windows:**
```cmd
# Command Prompt
install.bat

# PowerShell
.\install.ps1
```

**macOS/Linux:**
```bash
./install.sh
```

### Option 2: Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Install CLI globally
pip install -e .

# Or run directly
python kerberos_cli.py --help
```

### Quick Deploy

1. **Configure your cameras** in `config.yml`
2. **Deploy all agents:**
   ```bash
   kerberos start
   ```

That's it! Your agents will be running and accessible via web interfaces.

## Project Structure

```
kerberos-swarms/
├── config.yml              # Main configuration file
├── kerberos_cli.py         # Cross-platform CLI tool
├── requirements.txt        # Python dependencies
├── setup.py               # Package configuration
├── install.sh             # Unix installer (macOS/Linux)
├── install.bat            # Windows installer (Command Prompt)
├── install.ps1            # Windows installer (PowerShell)
├── configs/               # Generated agent configurations
├── recordings/            # Agent recordings storage
├── scripts/               # Legacy shell scripts (deprecated)
├── templates/             # Configuration templates
└── docker-compose.yml     # Generated compose file (after running kerberos generate)
```

## Configuration

### Basic Configuration (`config.yml`)

The main configuration file defines your camera setup:

```yaml
# Global settings
global:
  config_base_path: "./configs"
  recordings_base_path: "./recordings"
  network_name: "kerberos-network"
  kerberos_image: "kerberos/agent:latest"

# Camera configuration
cameras:
  ip_range:
    start: "10.19.19.30"    # Starting IP address
    end: "10.19.19.38"      # Ending IP address (inclusive)
  
  connection:
    protocol: "rtsp"        # rtsp, http, https
    port: 554
    username: "admin"
    password: "password"
    stream_path: "/stream1"

# Docker settings
docker:
  restart_policy: "unless-stopped"
  web_port_start: 8080     # Web UI ports start from 8080
  rtmp_port_start: 1935    # RTMP ports start from 1935
  limits:
    memory: "512m"         # Memory limit per container
    cpus: "0.5"           # CPU limit per container

# Custom environment
custom_environment:
  TZ: "Asia/Manila"        # Timezone setting
```

### IP Range Configuration

The system automatically calculates camera IPs from the range:
- `start: "10.19.19.30"` and `end: "10.19.19.38"` creates 9 cameras
- Generates: 10.19.19.30, 10.19.19.31, 10.19.19.32, ... 10.19.19.38

### Port Assignment

Ports are automatically assigned incrementally:
- Camera `10.19.19.30` → Web: 8080, RTMP: 1935
- Camera `10.19.19.31` → Web: 8081, RTMP: 1936
- Camera `10.19.19.32` → Web: 8082, RTMP: 1937
- And so on...

## CLI Commands

The modern CLI interface provides rich, colorful output and comprehensive management:

### Core Commands

```bash
# Show all available commands
kerberos --help

# Check system dependencies
kerberos check

# Show configuration information
kerberos info

# Generate docker-compose.yml from config
kerberos generate

# Start all agents
kerberos start

# Stop all agents
kerberos stop

# Restart all agents
kerberos restart

# Show agent status
kerberos status

# View logs (all agents)
kerberos logs

# View logs (specific agent)
kerberos logs --service camera-10-19-19-30

# Follow logs in real-time
kerberos logs --follow

# Update agents to latest version
kerberos update

# Regenerate configuration and restart
kerberos redeploy

# Clean up (with confirmation)
kerberos cleanup

# Clean up including volumes
# Clean up including volumes
kerberos cleanup --volumes
```

### Installation Options

| Platform | Method | Command |
|----------|---------|---------|
| **Windows** | Command Prompt | `install.bat` |
| **Windows** | PowerShell | `.\install.ps1` |
| **macOS/Linux** | Bash | `./install.sh` |
| **Any Platform** | Python pip | `pip install -e .` |
| **Development** | Dev setup | `./install.sh dev` |

### Legacy Shell Scripts

The original shell scripts are still available for compatibility:
- `generate-compose.sh` - Generate Docker Compose
- `manage.sh` - Management interface  
- `start.sh` / `stop.sh` - Quick start/stop

**Note:** The new Python CLI is recommended for cross-platform compatibility and better features.

## Accessing Your Cameras
```

### Advanced Usage

```bash
# Use custom configuration file
kerberos --config production.yml generate
kerberos --config production.yml start

# Run without detaching (see output)
kerberos start --no-detach
```

## Accessing Your Cameras

After starting the agents:

1. **Web Interfaces**: Access via browser
   - First camera: http://localhost:8080
   - Second camera: http://localhost:8081
   - Third camera: http://localhost:8082
   - etc.

2. **RTMP Streams**: For streaming applications
   - First camera: rtmp://localhost:1935/live
   - Second camera: rtmp://localhost:1936/live
   - etc.

## Directory Structure After Deployment

```
kerberos-swarms/
├── configs/
│   ├── camera-10-19-19-30/    # Agent config for first camera
│   ├── camera-10-19-19-31/    # Agent config for second camera
│   └── ...
├── recordings/
│   ├── camera-10-19-19-30/    # Recordings for first camera
│   ├── camera-10-19-19-31/    # Recordings for second camera
│   └── ...
└── docker-compose.yml
```

## Advanced Configuration

### Individual Camera Settings

For cameras with different credentials:

```yaml
cameras:
  individual_configs:
    - ip: "10.19.19.30"
      username: "admin1"
      password: "pass1"
      stream_path: "/stream1"
    - ip: "10.19.19.31"
      username: "admin2"
      password: "pass2"
      stream_path: "/live"
```

### Integration Options

```yaml
integrations:
  # Webhook notifications
  webhook:
    enabled: true
    url: "https://your-webhook-url.com/notify"
    
  # MQTT integration
  mqtt:
    enabled: true
    broker: "mqtt://localhost:1883"
    topic_prefix: "kerberos/cameras"
    
  # Cloud storage
  cloud_storage:
    enabled: true
    provider: "s3"
    bucket: "your-recordings-bucket"
    region: "us-west-2"
```

### Agent Settings

Fine-tune detection and recording:

```yaml
cameras:
  agent_settings:
    detection:
      enabled: true
      threshold: 20              # Motion sensitivity
      roi: "100,100,800,600"     # Region of interest
    
    recording:
      enabled: true
      duration: 30               # Recording length in seconds
      pre_recording: 5           # Pre-trigger recording
      post_recording: 5          # Post-trigger recording
      format: "mp4"
      quality: 80               # Video quality (1-100)
    
    stream:
      enabled: true
      quality: 60               # Stream quality
      fps: 15                   # Stream frame rate
```

## Troubleshooting

### Common Issues

1. **"Python not found"**
   ```bash
   # Install Python 3.7+
   # Windows: Download from python.org
   # macOS: brew install python3
   # Linux: sudo apt install python3 python3-pip
   ```

2. **"Module not found" errors**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Or install manually
   pip install click PyYAML rich docker
   ```

3. **"Docker not found"**
   ```bash
   # Check Docker installation
   docker --version
   docker-compose --version
   
   # Start Docker service
   kerberos check  # Check all dependencies
   ```

4. **Permission denied**
   ```bash
   # Unix systems
   chmod +x install.sh kerberos_cli.py
   
   # Windows - Run as Administrator if needed
   ```

5. **Port conflicts**
   ```bash
   # Change starting ports in config.yml
   docker:
     web_port_start: 9080
     rtmp_port_start: 2935
   ```

### Debugging

```bash
# Check system and dependencies
kerberos check

# View configuration
kerberos info

# Detailed logs
kerberos logs --follow

# Check Docker status
kerberos status

# Run with Python directly (for debugging)
python kerberos_cli.py --help
```

## Camera Connection Testing

Test your camera streams before deployment:

```bash
# Test RTSP stream
ffmpeg -i rtsp://admin:password@10.19.19.30:554/stream1 -t 10 -f null -

# Test with VLC
vlc rtsp://admin:password@10.19.19.30:554/stream1
```

## Performance Optimization

### For Multiple Cameras

1. **Adjust resource limits** in config.yml:
   ```yaml
   docker:
     limits:
       memory: "256m"    # Reduce if needed
       cpus: "0.3"       # Adjust based on CPU cores
   ```

2. **Use external storage** for recordings:
   ```yaml
   global:
     recordings_base_path: "/mnt/external/recordings"
   ```

3. **Optimize video quality**:
   ```yaml
   cameras:
     agent_settings:
       recording:
         quality: 60     # Lower quality = less storage
       stream:
         quality: 40     # Lower stream quality
         fps: 10         # Reduce frame rate
   ```

## Backup and Recovery

### Backup Configuration
```bash
# Backup configs
tar -czf kerberos-backup-$(date +%Y%m%d).tar.gz configs/ recordings/ config.yml

# Restore
tar -xzf kerberos-backup-20231215.tar.gz
```

### Migration
```bash
# Stop current deployment
./manage.sh stop

# Update configuration
# Edit config.yml

# Redeploy
./manage.sh redeploy
```

## Contributing

1. Fork this repository
2. Make your changes
3. Test with your camera setup
4. Submit a pull request

## License

This project is open source. Kerberos.io agents have their own licensing terms.

## Support

- Kerberos.io Documentation: https://doc.kerberos.io/
- Kerberos.io GitHub: https://github.com/kerberos-io/agent
- Issues: Create an issue in this repository

---

**Happy monitoring! 📹🔒**
