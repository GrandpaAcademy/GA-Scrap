"""
GA-Scrap Post-Installation Setup
Automatically configures GA-Scrap after installation
"""

import sys
import subprocess
import os
from pathlib import Path
from colorama import Fore, Style, init

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print setup banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════╗
║           GA-SCRAP SETUP              ║
║     Automatic Configuration          ║
╚═══════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version < (3, 8):
        print(f"{Fore.RED}❌ Python {version.major}.{version.minor} is not supported{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 GA-Scrap requires Python 3.8 or higher{Style.RESET_ALL}")
        return False
    
    print(f"{Fore.GREEN}✅ Python {version.major}.{version.minor}.{version.micro}{Style.RESET_ALL}")
    return True

def install_playwright_browsers():
    """Install Playwright browsers"""
    try:
        print(f"{Fore.CYAN}📦 Installing Playwright browsers...{Style.RESET_ALL}")
        
        # Install only Chromium by default for faster setup
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "chromium"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"{Fore.GREEN}✅ Playwright browsers installed{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  Playwright installation had issues:{Style.RESET_ALL}")
            print(f"   {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"{Fore.YELLOW}⚠️  Playwright installation timed out{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️  Could not install Playwright browsers: {e}{Style.RESET_ALL}")
        return False

def create_workspace():
    """Create workspace directory"""
    try:
        workspace_dir = Path.home() / "ga_scrap_apps"
        workspace_dir.mkdir(parents=True, exist_ok=True)
        print(f"{Fore.GREEN}✅ Created workspace: {workspace_dir}{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️  Could not create workspace: {e}{Style.RESET_ALL}")
        return False

def create_config():
    """Create default configuration"""
    try:
        config_dir = Path.home() / ".ga_scrap"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "config.yaml"
        if not config_file.exists():
            default_config = """# GA-Scrap Global Configuration
workspace_dir: ~/ga_scrap_apps
default_template: basic
browser:
  headless: false
  slow_mo: 500
  timeout: 30000
  viewport:
    width: 1280
    height: 720
dev_server:
  port: 8000
  auto_reload: true
  watch_extensions: [".py", ".yaml", ".json"]
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
auto_setup:
  install_browsers: true
  create_workspace: true
  create_welcome_app: true
"""
            config_file.write_text(default_config)
            print(f"{Fore.GREEN}✅ Created configuration: {config_file}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Configuration exists: {config_file}{Style.RESET_ALL}")
        
        return True
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️  Could not create configuration: {e}{Style.RESET_ALL}")
        return False

def show_next_steps():
    """Show next steps to the user"""
    print(f"\n{Fore.GREEN}🎉 GA-Scrap setup complete!{Style.RESET_ALL}")
    print(f"\n{Fore.CYAN}🚀 Quick start commands:{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}ga-scrap quick 'https://quotes.toscrape.com' '.quote .text' --all{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}ga-scrap new my-first-scraper{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}ga-scrap list{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}ga-scrap doctor{Style.RESET_ALL}")
    
    print(f"\n{Fore.CYAN}📚 Learn more:{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}ga-scrap examples{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}ga-scrap templates{Style.RESET_ALL}")
    print(f"   {Fore.WHITE}ga-scrap config show{Style.RESET_ALL}")

def run_post_install():
    """Run the complete post-installation setup"""
    print_banner()
    
    print(f"{Fore.GREEN}🚀 Setting up GA-Scrap...{Style.RESET_ALL}\n")
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Create configuration
    create_config()
    
    # Create workspace
    create_workspace()
    
    # Install Playwright browsers (optional, can fail)
    install_playwright_browsers()
    
    # Show next steps
    show_next_steps()
    
    return True

if __name__ == "__main__":
    try:
        run_post_install()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Setup interrupted by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}Setup failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 You can run 'ga-scrap setup' manually later{Style.RESET_ALL}")
