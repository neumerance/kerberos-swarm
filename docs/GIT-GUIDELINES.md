# Git Repository Guidelines

## 📁 What's Tracked in Git

### ✅ Source Code & Configuration
- **Python CLI tools** (`kerberos_cli.py`, `kerberos_lite.py`)
- **Installation scripts** (`install.sh`, `install.bat`, `install.ps1`) 
- **Legacy shell scripts** (`*.sh` files)
- **Configuration templates** (`config.yml`, `config.example.yml`)
- **Documentation** (`README.md`, `*.md` files)
- **Package configuration** (`setup.py`, `requirements.txt`)

### 📄 Example Files Included
- `config.yml` - Default configuration with Philippines timezone
- `config.example.yml` - Example configuration for reference

## 🚫 What's NOT Tracked (Gitignored)

### 🐳 Generated Files
- `docker-compose.yml` - Generated from your config.yml
- `configs/` - Runtime agent configurations  
- `recordings/` - Camera recordings storage

### 🛠️ Runtime & Build Files  
- Python bytecode (`__pycache__/`, `*.pyc`)
- Virtual environments (`venv/`, `.env`)
- Build artifacts (`build/`, `dist/`, `*.egg-info/`)

### 💻 Local Environment
- IDE files (`.vscode/`, `.idea/`)
- OS files (`.DS_Store`, `Thumbs.db`)
- Log files (`*.log`, `logs/`)
- Temporary files (`tmp/`, `*.bak`)

### 🔧 Generated Wrappers
- `kerberos.bat` - Windows batch wrapper
- `kerberos.ps1` - PowerShell wrapper

## 📝 Best Practices

### Configuration Management
```bash
# Keep your main config tracked
git add config.yml

# Use local configs for environment-specific settings
cp config.yml production.yml
# (production.yml is gitignored)
```

### Safe Development
```bash
# Always check what you're committing
git status
git diff --cached

# Never commit sensitive data
# Review config.yml for passwords before commit
```

### Clean Repository
```bash
# Remove accidentally committed generated files
git rm --cached docker-compose.yml
git rm --cached -r configs/
git commit -m "Remove generated files"
```

## 🔄 Workflow Example

```bash
# 1. Modify configuration
nano config.yml

# 2. Test locally (generates files)
kerberos generate
kerberos start

# 3. Commit only source changes
git add config.yml
git commit -m "Update camera configuration"

# 4. Generated files stay local
# docker-compose.yml, configs/, recordings/ are ignored
```

This keeps your repository clean while preserving all the important source code and documentation! 🧹✨
