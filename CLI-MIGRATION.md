# CLI Migration Guide

## Shell Scripts → Python CLI

We've upgraded from shell scripts to a modern, cross-platform Python CLI. Here's how the commands map:

### Command Comparison

| Old Shell Script | New CLI Command | Notes |
|------------------|-----------------|-------|
| `./check-deps.sh` | `kerberos check` | Enhanced dependency checking |
| `./generate-compose.sh` | `kerberos generate` | Better error handling, progress bars |
| `./manage.sh start` | `kerberos start` | Cross-platform, rich output |
| `./manage.sh stop` | `kerberos stop` | Same functionality |
| `./manage.sh restart` | `kerberos restart` | Same functionality |
| `./manage.sh status` | `kerberos status` | Improved formatting |
| `./manage.sh logs` | `kerberos logs` | More options (--follow, --service) |
| `./manage.sh update` | `kerberos update` | Same functionality |
| `./manage.sh redeploy` | `kerberos redeploy` | Same functionality |
| `./manage.sh cleanup` | `kerberos cleanup` | Added confirmation prompts |
| `./start.sh` | `kerberos start` | Combined generate + start |
| `./stop.sh` | `kerberos stop` | Same functionality |
| `./overview.sh` | `kerberos info` | Enhanced information display |

### New Features in CLI

✅ **Cross-platform compatibility** (Windows, macOS, Linux)  
✅ **Rich terminal output** with colors and progress bars  
✅ **Better error handling** and user feedback  
✅ **Configuration validation** built-in  
✅ **Programmatic usage** possible via Python imports  
✅ **Global installation** as `kerberos` command  
✅ **Multiple installation methods** (pip, batch, shell)  

### Migration Steps

1. **Install the CLI:**
   ```bash
   # Windows
   install.bat
   
   # macOS/Linux  
   ./install.sh
   ```

2. **Update your workflows:**
   ```bash
   # Old way
   ./generate-compose.sh && ./manage.sh start
   
   # New way
   kerberos start
   ```

3. **Use new features:**
   ```bash
   # Check everything at once
   kerberos check
   
   # Get detailed info
   kerberos info
   
   # Follow logs in real-time
   kerberos logs --follow
   ```

### Backwards Compatibility

The original shell scripts are still included and functional:
- ✅ All shell scripts work as before
- ✅ Same configuration file (`config.yml`)
- ✅ Same Docker Compose output
- ✅ Same directory structure

### Why Migrate?

| Feature | Shell Scripts | Python CLI |
|---------|---------------|------------|
| **Windows Support** | ❌ (WSL only) | ✅ Native |
| **macOS Support** | ✅ | ✅ |
| **Linux Support** | ✅ | ✅ |
| **Dependencies** | bash, yq, docker | Python, docker |
| **Error Handling** | Basic | Advanced |
| **User Interface** | Plain text | Rich colors/formatting |
| **Progress Feedback** | None | Progress bars |
| **Global Installation** | Manual | Automatic |
| **Programmatic Use** | Difficult | Easy |

### Getting Help

```bash
# CLI help
kerberos --help
kerberos COMMAND --help

# Legacy scripts help  
./manage.sh help
./overview.sh
```

The Python CLI is the recommended approach going forward, but you can continue using shell scripts if preferred.
