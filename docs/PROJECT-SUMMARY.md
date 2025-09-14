# Kerberos.io Multi-Agent Deployment System

## Project Overview

This project provides a complete solution for deploying multiple Kerberos.io agents for CCTV monitoring. It started as a shell script-based system and evolved into a cross-platform Python CLI tool with rich features.

## 🎯 What We Built

### Core Features
- **Cross-platform compatibility** - Works on Windows, macOS, and Linux
- **IP range-based configuration** - Define start/end IPs, automatically generate agents
- **YAML-based configuration** - Single file to configure all cameras
- **Docker Compose automation** - Generates compose files automatically  
- **Modern CLI interface** - Rich terminal output with colors and progress
- **Legacy shell script support** - Backwards compatible with original scripts

### Project Structure

```
kerberos-swarms/
├── 📄 Configuration Files
│   ├── config.yml              # Main configuration file
│   └── config.example.yml      # Example configuration
├── 🐍 Python CLI Tools
│   ├── kerberos_cli.py         # Full-featured CLI (requires rich, click, etc.)
│   ├── kerberos_lite.py        # Minimal dependencies CLI
│   ├── requirements.txt        # Python dependencies
│   ├── setup.py               # Package configuration
│   └── demo.py                # Usage demonstration script
├── 🛠️ Installation Scripts  
│   ├── install.sh             # Unix installer (macOS/Linux)
│   ├── install-cli.sh         # Alternative CLI installer
│   ├── install.bat            # Windows installer (Command Prompt)
│   └── install.ps1            # Windows installer (PowerShell)
├── 📜 Legacy Shell Scripts (Deprecated but functional)
│   ├── generate-compose.sh    # Generate docker-compose.yml
│   ├── manage.sh             # Management interface
│   ├── start.sh              # Quick start
│   ├── stop.sh               # Quick stop
│   ├── check-deps.sh         # Dependency checker
│   └── overview.sh           # Help/overview
├── � Documentation
│   ├── README.md             # Main project guide (root)
│   └── docs/                 # Organized documentation
│       ├── INDEX.md          # Documentation navigation
│       ├── QUICK-START.md    # Fast setup guide
│       ├── PROJECT-SUMMARY.md # This file
│       ├── CLI-MIGRATION.md  # Evolution history
│       ├── DEVELOPMENT-CHECKLIST.md # Feature tracking
│       └── GIT-GUIDELINES.md # Repository best practices
├── 🔧 Project Configuration
│   ├── .gitignore           # Git ignore rules
│   └── .tool-versions       # Tool version management
└── 🐳 Generated Files (Gitignored)
    ├── docker-compose.yml   # Auto-generated compose file
    ├── configs/             # Agent configurations
    ├── recordings/          # Camera recordings
    └── kerberos_swarms.egg-info/ # Python package metadata
```

## 📋 Configuration System

### Main Configuration (`config.yml`)

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
    start: "10.19.19.30"
    end: "10.19.19.38"    # Generates 9 cameras
  
  connection:
    protocol: "rtsp"
    port: 554
    username: "admin"
    password: "password"
    stream_path: "/stream1"

# Docker settings  
docker:
  restart_policy: "unless-stopped"
  web_port_start: 8080     # Web UIs: 8080, 8081, 8082...
  rtmp_port_start: 1935    # RTMP: 1935, 1936, 1937...
  limits:
    memory: "512m"
    cpus: "0.5"

# Custom environment
custom_environment:
  TZ: "Asia/Manila"        # Philippines timezone
```

### Key Configuration Features

- **IP Range Generation**: `10.19.19.30` → `10.19.19.38` creates 9 camera agents
- **Automatic Port Assignment**: Web interfaces start from 8080, RTMP from 1935
- **Directory Organization**: Each camera gets its own config and recording directories
- **Resource Limits**: Configurable memory and CPU limits per container
- **Timezone Support**: Set to Philippines (Asia/Manila) as requested

## 🚀 CLI Tools

### Modern Python CLI

Two versions were created:

#### 1. Full-Featured CLI (`kerberos_cli.py`)
- **Dependencies**: click, PyYAML, rich, docker
- **Features**: Rich terminal output, progress bars, colored text
- **Commands**: All management functions with advanced options

#### 2. Lite CLI (`kerberos_lite.py`)  
- **Dependencies**: Only PyYAML (auto-installs if missing)
- **Features**: Basic terminal output, minimal system requirements
- **Commands**: All core functionality with simple interface

### Available Commands

```bash
# Core operations
kerberos generate              # Generate docker-compose.yml
kerberos start                 # Start all agents
kerberos stop                  # Stop all agents
kerberos restart               # Restart all agents

# Monitoring
kerberos status                # Show agent status
kerberos logs                  # View all logs
kerberos logs --service camera-10-19-19-30  # Specific camera
kerberos logs --follow         # Real-time logs

# Management
kerberos update                # Update to latest versions
kerberos redeploy              # Regenerate config and restart
kerberos cleanup               # Remove containers
kerberos cleanup --volumes     # Remove containers and data

# Information
kerberos check                 # Check dependencies
kerberos info                  # Show configuration summary
```

## 🛠️ Installation Options

### Cross-Platform Installers

| Platform | Method | Command |
|----------|---------|---------|
| **Windows** | Command Prompt | `install.bat` |
| **Windows** | PowerShell | `.\install.ps1` |
| **macOS/Linux** | Bash | `./install.sh` |
| **Any Platform** | Python pip | `pip install -e .` |
| **Development** | Dev setup | `./install.sh dev` |

### Installation Features

- **Automatic dependency installation**
- **Global CLI command setup**
- **Virtual environment support** (optional)
- **Cross-platform compatibility checks**
- **Fallback wrapper creation** if global install fails

## 🐚 Legacy Shell Scripts

Original shell scripts are preserved for compatibility:

### Script Functions

| Script | Purpose | Status |
|--------|---------|--------|
| `generate-compose.sh` | Generate Docker Compose | ✅ Functional |
| `manage.sh` | Full management interface | ✅ Functional |
| `start.sh` / `stop.sh` | Quick start/stop | ✅ Functional |
| `check-deps.sh` | Dependency checker | ✅ Functional |
| `overview.sh` | Help and information | ✅ Functional |

### Dependencies for Shell Scripts
- **bash** shell
- **yq** (YAML processor)
- **docker** and **docker-compose**

## 🐳 Docker Integration

### Generated Docker Compose Structure

```yaml
version: '3.8'
networks:
  kerberos-network:
    driver: bridge

services:
  camera-10-19-19-30:
    image: kerberos/agent:latest
    container_name: camera-10-19-19-30
    restart: unless-stopped
    ports:
      - "8080:80"      # Web interface
      - "1935:1935"    # RTMP stream
    volumes:
      - "./configs/camera-10-19-19-30:/home/agent/data/config"
      - "./recordings/camera-10-19-19-30:/home/agent/data/recordings"
    environment:
      - AGENT_NAME=camera-10-19-19-30
      - AGENT_CAPTURE_IPCAMERA_RTSP=rtsp://admin:password@10.19.19.30:554/stream1
      - TZ=Asia/Manila
  # ... (additional cameras follow same pattern)
```

### Automatic Features

- **Network creation**: Dedicated Docker network for agents
- **Port management**: Sequential port assignment 
- **Volume mounting**: Organized config and recording storage
- **Environment variables**: Camera-specific configuration
- **Resource limits**: Optional memory/CPU constraints

## 📁 Directory Organization

### After Deployment

```
kerberos-swarms/
├── configs/
│   ├── camera-10-19-19-30/    # Camera 1 configuration
│   ├── camera-10-19-19-31/    # Camera 2 configuration
│   ├── camera-10-19-19-32/    # Camera 3 configuration
│   └── ... (up to camera-10-19-19-38)
├── recordings/
│   ├── camera-10-19-19-30/    # Camera 1 recordings
│   ├── camera-10-19-19-31/    # Camera 2 recordings  
│   └── ... (matching structure)
└── docker-compose.yml         # Generated compose file
```

## 🌐 Network Access

### Web Interfaces
- Camera 1: `http://localhost:8080`
- Camera 2: `http://localhost:8081`
- Camera 3: `http://localhost:8082`
- ... (continues sequentially)

### RTMP Streams
- Camera 1: `rtmp://localhost:1935/live`
- Camera 2: `rtmp://localhost:1936/live`
- Camera 3: `rtmp://localhost:1937/live`
- ... (continues sequentially)

## 🔧 System Requirements

### Minimum Requirements
- **Python 3.7+** (for CLI tools)
- **Docker** and **Docker Compose**
- **Operating System**: Windows 10+, macOS 10.14+, or Linux

### Optional Requirements
- **bash** (for legacy shell scripts)
- **yq** (for shell script YAML processing)
- **Git** (for development)

## 🎛️ Usage Examples

### Quick Start
```bash
# 1. Configure cameras in config.yml
# 2. Deploy everything
kerberos start

# 3. Check status
kerberos status

# 4. View logs  
kerberos logs
```

### Production Deployment
```bash
# Custom configuration
kerberos --config production.yml generate
kerberos --config production.yml start

# Monitor deployment
kerberos status
kerberos logs --follow
```

### Maintenance
```bash
# Update to latest versions
kerberos update

# Backup and redeploy
kerberos cleanup
kerberos redeploy
```

## 🐛 Troubleshooting

### Common Issues

1. **Python/Xcode Tools Required**
   - Install Xcode command line tools on macOS
   - Use `kerberos_lite.py` for minimal dependencies

2. **Port Conflicts**
   - Modify `web_port_start` and `rtmp_port_start` in config.yml
   - Check for existing services on ports

3. **Docker Issues**
   - Ensure Docker service is running
   - Check Docker Compose installation

4. **YAML Syntax Errors**
   - Validate config.yml syntax
   - Use provided example files as reference

## 🔄 Migration Path

### From Shell Scripts to Python CLI

| Old Command | New Command |
|-------------|-------------|
| `./start.sh` | `kerberos start` |
| `./manage.sh status` | `kerberos status` |
| `./generate-compose.sh` | `kerberos generate` |
| `./check-deps.sh` | `kerberos check` |

## 🎯 Key Achievements

### ✅ What We Accomplished

1. **Cross-Platform CLI Tool**
   - Works on Windows, macOS, and Linux
   - Two versions: full-featured and lite
   - Professional installation scripts

2. **IP Range Automation**
   - Automatic camera discovery from IP ranges
   - Sequential port assignment
   - Organized directory structure

3. **Configuration Management**
   - YAML-based configuration
   - Validation and error handling
   - Example configurations

4. **Docker Integration**
   - Automatic Compose file generation
   - Resource management
   - Network isolation

5. **Legacy Compatibility**
   - Original shell scripts preserved
   - Same configuration format
   - Backwards compatibility

6. **Documentation**
   - Comprehensive README
   - Migration guides
   - Usage examples

## 🚀 Next Steps for Development

### Recommended Improvements

1. **Configuration Validation**
   - JSON Schema validation for config.yml
   - Better error messages for invalid configs

2. **Web Interface**
   - Management dashboard
   - Camera status monitoring
   - Configuration editor

3. **Cloud Integration**
   - Cloud storage adapters
   - Remote monitoring
   - Notification systems

4. **Security Enhancements**
   - Certificate management
   - Secure credential storage
   - Access control

5. **Monitoring & Alerting**
   - Health checks
   - Performance metrics
   - Alert notifications

## 📞 Support & Resources

### Documentation Files
- `README.md` - Complete user guide
- `CLI-MIGRATION.md` - Migration from shell scripts
- `config.example.yml` - Example configuration

### Testing
- `demo.py` - CLI usage demonstration
- `kerberos check` - System validation
- `kerberos info` - Configuration summary

### Community Resources
- Kerberos.io Documentation: https://doc.kerberos.io/
- Docker Documentation: https://docs.docker.com/
- Python Click Framework: https://click.palletsprojects.com/

---

**Project Status**: ✅ **Complete and Ready for Use**

This system provides a production-ready solution for deploying multiple Kerberos.io agents with modern tooling, cross-platform support, and comprehensive documentation. The combination of Python CLI tools and legacy shell script compatibility ensures flexibility for different environments and use cases.
