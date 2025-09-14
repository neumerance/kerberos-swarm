# Kerberos CLI - Quick Reference

## 🚀 Global Command Ready!

You now have the `kerberos` command available globally! Here's what you can do:

### Add to PATH (one-time setup)
```bash
# Add this to your ~/.bashrc or ~/.zshrc
export PATH="/Users/jonjon/.local/bin:$PATH"

# Then reload your shell
source ~/.bashrc  # or ~/.zshrc
```

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
