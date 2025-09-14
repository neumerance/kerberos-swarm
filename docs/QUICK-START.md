# Kerberos CLI - Quick Start Guide

## 🚀 Installation

Choose your installation method:

### Option 1: Automated Installation (Recommended)
```bash
# macOS/Linux
./install.sh

# Windows Command Prompt
install.bat

# Windows PowerShell
.\install.ps1
```

### Option 2: Manual Installation
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install CLI globally
pip install -e .
```

## ⚡ Quick Commands

After installation, the `kerberos` command is available globally:

### Quick Commands
```bash
# Check system status
kerberos check

# View configuration
kerberos info

# Generate Docker Compose (without starting)
kerberos generate

# Start all cameras (generates compose if needed)
kerberos start

# Check status
kerberos status

# View logs
kerberos logs

# Stop everything
kerberos stop
```

### Next Steps

1. **Install Docker** (if you want to actually deploy):
   ```bash
   # Linux
   sudo apt update && sudo apt install docker.io docker-compose
   # or use Docker Desktop
   ```

2. **Configure your cameras** in `config.yml`:
   ```yaml
   cameras:
     ip_range:
       start: "YOUR_START_IP"
       end: "YOUR_END_IP"
   ```

3. **Test the system**:
   ```bash
   kerberos check        # Verify dependencies
   kerberos generate     # Generate Docker Compose
   kerberos start        # Deploy cameras
   ```

### Project Features ✅

- ✅ Cross-platform CLI (works on Windows, macOS, Linux)
- ✅ Global `kerberos` command (no more `python3 kerberos_lite.py`)
- ✅ IP range automation (10.19.19.30-38 = 9 cameras)
- ✅ Philippines timezone (Asia/Manila)
- ✅ Auto port assignment (Web: 8080+, RTMP: 1935+)
- ✅ Organized storage (configs/, recordings/)
- ✅ Legacy shell scripts (backwards compatible)
- ✅ Complete documentation

## 🎯 Ready for Production!

Your Kerberos.io multi-agent system is complete and ready to deploy multiple CCTV cameras with a simple `kerberos start` command! 📹🔒
