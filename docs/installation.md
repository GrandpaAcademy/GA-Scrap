# 🔧 Installation Guide

<div align="center">

**Get GA-Scrap Running in Minutes**  
*Complete setup guide for all platforms*

</div>

---

## 📋 System Requirements

- **Python 3.8+** (Python 3.9+ recommended)
- **Git** for cloning the repository
- **4GB RAM** minimum (8GB+ recommended)
- **1GB disk space** for browsers and dependencies
- **Internet connection** for downloading browsers

### Supported Platforms
- ✅ **Windows** 10/11
- ✅ **macOS** 10.15+
- ✅ **Linux** (Ubuntu 18.04+, CentOS 7+, etc.)

---

## ⚡ Quick Installation

### 1. Clone Repository
```bash
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install
```

### 4. Verify Installation
```bash
# Test GA-Scrap
python -c "from ga_scrap import SyncGAScrap; print('✅ GA-Scrap installed successfully!')"

# Test browser installation
playwright --version
```

---

## 🖥️ Platform-Specific Instructions

### Windows Installation

#### Prerequisites
```powershell
# Install Python from python.org or Microsoft Store
# Install Git from git-scm.com

# Verify installations
python --version
git --version
```

#### Installation Steps
```powershell
# Clone repository
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install

# Test installation
python -c "from ga_scrap import SyncGAScrap; print('✅ Windows installation complete!')"
```

#### Windows-Specific Issues
```powershell
# If you get execution policy errors:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# If pip is not found:
python -m pip install --upgrade pip

# If playwright install fails:
python -m playwright install
```

### macOS Installation

#### Prerequisites
```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python and Git
brew install python git
```

#### Installation Steps
```bash
# Clone repository
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install

# Test installation
python -c "from ga_scrap import SyncGAScrap; print('✅ macOS installation complete!')"
```

#### macOS-Specific Issues
```bash
# If you get SSL certificate errors:
/Applications/Python\ 3.x/Install\ Certificates.command

# If permission denied errors:
sudo xcode-select --install

# If browser installation fails:
playwright install --with-deps
```

### Linux Installation

#### Ubuntu/Debian
```bash
# Update package list
sudo apt update

# Install Python and Git
sudo apt install python3 python3-pip python3-venv git

# Install system dependencies for browsers
sudo apt install -y \
    libnss3 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libgtk-3-0 \
    libgbm1

# Clone and install GA-Scrap
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps
```

#### CentOS/RHEL/Fedora
```bash
# Install Python and Git
sudo dnf install python3 python3-pip git

# Install system dependencies
sudo dnf install -y \
    nss \
    atk \
    at-spi2-atk \
    gtk3 \
    libdrm \
    libxkbcommon \
    mesa-libgbm

# Clone and install GA-Scrap
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install --with-deps
```

---

## 🐳 Docker Installation

### Using Docker
```dockerfile
# Dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Clone GA-Scrap
WORKDIR /app
RUN git clone https://github.com/GrandpaAcademy/GA-Scrap.git .

# Install Python dependencies
RUN pip install -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps

# Set entrypoint
CMD ["python", "-c", "from ga_scrap import SyncGAScrap; print('GA-Scrap ready!')"]
```

### Build and Run
```bash
# Build Docker image
docker build -t ga-scrap .

# Run container
docker run -it --rm ga-scrap

# Run with volume mount for your scripts
docker run -it --rm -v $(pwd)/scripts:/app/scripts ga-scrap
```

---

## 🔧 Development Installation

### For Contributors
```bash
# Clone with development setup
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
pip install -r requirements-dev.txt  # If exists

# Install pre-commit hooks
pre-commit install  # If using pre-commit

# Run tests
python -m pytest tests/
```

### IDE Setup

#### VS Code
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
}
```

#### PyCharm
1. Open project in PyCharm
2. Go to **File > Settings > Project > Python Interpreter**
3. Select **Add Interpreter > Existing Environment**
4. Choose `venv/bin/python` (or `venv\Scripts\python.exe` on Windows)

---

## 🧪 Testing Installation

### Basic Test
```python
# test_installation.py
from ga_scrap import SyncGAScrap

def test_basic_functionality():
    try:
        with SyncGAScrap(headless=True) as scraper:
            scraper.goto("https://httpbin.org/html")
            title = scraper.get_text("h1")
            assert title is not None
            print("✅ Basic functionality test passed")
            return True
    except Exception as e:
        print(f"❌ Basic functionality test failed: {e}")
        return False

def test_sandbox_mode():
    try:
        with SyncGAScrap(sandbox_mode=True, headless=True) as scraper:
            scraper.goto("https://httpbin.org/html")
            scraper.click("#non-existent-element")  # Should not crash
            scraper.screenshot("test.png")
            print("✅ Sandbox mode test passed")
            return True
    except Exception as e:
        print(f"❌ Sandbox mode test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing GA-Scrap installation...")
    basic_ok = test_basic_functionality()
    sandbox_ok = test_sandbox_mode()
    
    if basic_ok and sandbox_ok:
        print("🎉 All tests passed! GA-Scrap is ready to use.")
    else:
        print("❌ Some tests failed. Check the error messages above.")
```

### Run Test
```bash
python test_installation.py
```

---

## 🆘 Troubleshooting

### Common Issues

#### ❓ "ModuleNotFoundError: No module named 'playwright'"
```bash
# Solution: Install Playwright
pip install playwright
playwright install
```

#### ❓ "Browser executable not found"
```bash
# Solution: Install browsers
playwright install chromium firefox webkit

# Or install with system dependencies
playwright install --with-deps
```

#### ❓ "Permission denied" errors on Linux
```bash
# Solution: Install system dependencies
sudo apt install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgtk-3-0 libgbm1

# Or use with-deps flag
playwright install --with-deps
```

#### ❓ "SSL certificate verify failed" on macOS
```bash
# Solution: Install certificates
/Applications/Python\ 3.x/Install\ Certificates.command

# Or update certificates
pip install --upgrade certifi
```

#### ❓ Virtual environment activation fails
```bash
# Windows PowerShell solution:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Alternative activation:
python -m venv venv
venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Getting Help

#### Check Installation
```bash
# Verify Python version
python --version

# Verify pip
pip --version

# Verify Playwright
playwright --version

# Check installed browsers
playwright show-trace --help
```

#### Diagnostic Script
```python
# diagnostic.py
import sys
import subprocess

def run_diagnostics():
    print("🔍 GA-Scrap Installation Diagnostics")
    print("=" * 40)
    
    # Python version
    print(f"Python version: {sys.version}")
    
    # Try importing GA-Scrap
    try:
        from ga_scrap import SyncGAScrap
        print("✅ GA-Scrap import successful")
    except ImportError as e:
        print(f"❌ GA-Scrap import failed: {e}")
    
    # Try importing Playwright
    try:
        from playwright.sync_api import sync_playwright
        print("✅ Playwright import successful")
    except ImportError as e:
        print(f"❌ Playwright import failed: {e}")
    
    # Check browser installation
    try:
        result = subprocess.run(["playwright", "--version"], 
                              capture_output=True, text=True)
        print(f"✅ Playwright CLI: {result.stdout.strip()}")
    except FileNotFoundError:
        print("❌ Playwright CLI not found")

if __name__ == "__main__":
    run_diagnostics()
```

### Support Resources

- 📖 **[GitHub Issues](https://github.com/GrandpaAcademy/GA-Scrap/issues)** - Report bugs
- 💬 **[Discussions](https://github.com/GrandpaAcademy/GA-Scrap/discussions)** - Ask questions
- 📚 **[Playwright Docs](https://playwright.dev)** - Playwright-specific issues
- 🐍 **[Python.org](https://python.org)** - Python installation help

---

<div align="center">

**🎉 Installation Complete!**

**Next:** [🚀 Getting Started](getting-started.md) • [🎯 Examples](examples.md)

</div>
