"""
GA-Scrap CLI Interface
Command-line interface for easy usage and app management
"""

import click
import sys
import os
from pathlib import Path
from colorama import Fore, Style, init
from .app_manager import AppManager
from .hot_reload import DevServer, run_with_hot_reload
from .config_manager import config

# Initialize colorama
init(autoreset=True)

def print_banner():
    """Print GA-Scrap banner"""
    banner = f"""
{Fore.CYAN}╔═══════════════════════════════════════╗
║              GA-SCRAP                 ║
║     Playwright Scraper Helper         ║
║                                       ║
║  🚀 Always runs browser by default    ║
║  📱 Create multiple scraper apps      ║
║  🔥 Hot reload support               ║
║  🎯 Easy configuration               ║
╚═══════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def check_first_run():
    """Check if this is the first run and offer setup"""
    if not config.config_file.exists():
        print(f"{Fore.YELLOW}👋 Welcome to GA-Scrap!{Style.RESET_ALL}")
        print(f"{Fore.CYAN}It looks like this is your first time using GA-Scrap.{Style.RESET_ALL}")

        if click.confirm("Would you like to run the setup now?", default=True):
            from .post_install import run_post_install
            run_post_install()
        else:
            print(f"{Fore.YELLOW}💡 You can run 'ga-scrap setup' anytime to configure GA-Scrap{Style.RESET_ALL}")

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """GA-Scrap: A powerful Playwright-based scraper helper"""
    # Check for first run on certain commands
    ctx = click.get_current_context()
    if ctx.invoked_subcommand in ['new', 'create', 'quick', 'dev']:
        check_first_run()

@cli.command()
@click.argument('app_name')
@click.option('--template', '-t', default='basic',
              type=click.Choice(['basic', 'advanced', 'ecommerce', 'social']),
              help='Template to use for the new app')
@click.option('--description', '-d', default='', help='App description')
@click.option('--overwrite', is_flag=True, help='Overwrite existing app')
def new(app_name, template, description, overwrite):
    """Create a new scraper app"""
    print_banner()

    manager = AppManager()
    success = manager.create_app(
        app_name=app_name,
        template=template,
        description=description,
        overwrite=overwrite
    )

    if success:
        print(f"\n{Fore.GREEN}🎉 Next steps:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. cd ga_scrap_apps/{app_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. ga-scrap dev  # Start with hot reload{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Edit main.py to customize your scraper{Style.RESET_ALL}")

# Keep 'create' as an alias for backward compatibility
@cli.command()
@click.argument('app_name')
@click.option('--template', '-t', default='basic',
              type=click.Choice(['basic', 'advanced', 'ecommerce', 'social']),
              help='Template to use for the new app')
@click.option('--description', '-d', default='', help='App description')
@click.option('--overwrite', is_flag=True, help='Overwrite existing app')
def create(app_name, template, description, overwrite):
    """Create a new scraper app (alias for 'new')"""
    print(f"{Fore.YELLOW}💡 'create' is deprecated, use 'ga-scrap new' instead{Style.RESET_ALL}")

    manager = AppManager()
    success = manager.create_app(
        app_name=app_name,
        template=template,
        description=description,
        overwrite=overwrite
    )

    if success:
        print(f"\n{Fore.GREEN}🎉 Next steps:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}1. cd ga_scrap_apps/{app_name}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}2. ga-scrap dev  # Start with hot reload{Style.RESET_ALL}")
        print(f"{Fore.CYAN}3. Edit main.py to customize your scraper{Style.RESET_ALL}")

@cli.command()
def list():
    """List all created apps"""
    print_banner()
    
    manager = AppManager()
    apps = manager.list_apps()
    
    if not apps:
        print(f"{Fore.YELLOW}No apps found. Create one with: ga-scrap create <app_name>{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}📱 Your GA-Scrap Apps:{Style.RESET_ALL}\n")
    
    for app in apps:
        status_color = Fore.GREEN if app['status'] == 'created' else Fore.YELLOW
        print(f"{Fore.CYAN}📁 {app['name']}{Style.RESET_ALL}")
        print(f"   Template: {app['template']}")
        print(f"   Description: {app['description'] or 'No description'}")
        print(f"   Status: {status_color}{app['status']}{Style.RESET_ALL}")
        print(f"   Created: {app['created_at'][:19]}")
        print(f"   Path: {app['path']}")
        print()

@cli.command()
@click.argument('app_name')
def info(app_name):
    """Show detailed information about an app"""
    manager = AppManager()
    app_info = manager.get_app_info(app_name)
    
    if not app_info:
        print(f"{Fore.RED}❌ App '{app_name}' not found{Style.RESET_ALL}")
        return
    
    print(f"{Fore.GREEN}📱 App Information: {app_name}{Style.RESET_ALL}\n")
    
    for key, value in app_info.items():
        if key == 'name':
            continue
        print(f"{Fore.CYAN}{key.replace('_', ' ').title()}:{Style.RESET_ALL} {value}")

@cli.command()
@click.argument('app_name')
@click.confirmation_option(prompt='Are you sure you want to delete this app?')
def delete(app_name):
    """Delete an app"""
    manager = AppManager()
    manager.delete_app(app_name)

@cli.command()
@click.option('--app-dir', '-d', default='.', help='App directory (default: current directory)')
def dev(app_dir):
    """Start development server with hot reload"""
    app_path = Path(app_dir).resolve()
    
    # Check if we're in an app directory
    main_py = app_path / "main.py"
    if not main_py.exists():
        print(f"{Fore.RED}❌ main.py not found in {app_path}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Make sure you're in a GA-Scrap app directory{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Or create a new app with: ga-scrap create <app_name>{Style.RESET_ALL}")
        return
    
    try:
        dev_server = DevServer(str(app_path))
        dev_server.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Development server stopped{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error starting dev server: {e}{Style.RESET_ALL}")

@cli.command()
@click.argument('script_path')
@click.option('--watch-dir', '-w', multiple=True, help='Additional directories to watch')
def run(script_path, watch_dir):
    """Run a Python script with hot reload"""
    script = Path(script_path)
    
    if not script.exists():
        print(f"{Fore.RED}❌ Script not found: {script_path}{Style.RESET_ALL}")
        return
    
    watch_dirs = list(watch_dir) if watch_dir else None
    
    try:
        print(f"{Fore.GREEN}🔥 Running {script_path} with hot reload{Style.RESET_ALL}")
        run_with_hot_reload(str(script), watch_dirs)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}👋 Script stopped{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Error running script: {e}{Style.RESET_ALL}")

@cli.command()
def templates():
    """Show available app templates"""
    print_banner()
    
    templates_info = {
        'basic': {
            'description': 'Simple scraper with basic functionality',
            'features': ['Visible browser', 'Basic navigation', 'Element extraction', 'Logging']
        },
        'advanced': {
            'description': 'Advanced scraper with data export and utilities',
            'features': ['All basic features', 'Data export (JSON/CSV)', 'Table extraction', 'Advanced utilities']
        },
        'ecommerce': {
            'description': 'E-commerce focused scraper',
            'features': ['All advanced features', 'Product detail extraction', 'Category scraping', 'Price monitoring']
        },
        'social': {
            'description': 'Social media scraper template',
            'features': ['All advanced features', 'Post extraction', 'Profile scraping', 'Engagement metrics']
        }
    }
    
    print(f"{Fore.GREEN}📋 Available Templates:{Style.RESET_ALL}\n")
    
    for template, info in templates_info.items():
        print(f"{Fore.CYAN}🎯 {template.upper()}{Style.RESET_ALL}")
        print(f"   {info['description']}")
        print(f"   Features: {', '.join(info['features'])}")
        print()

@cli.command()
def examples():
    """Show usage examples"""
    print_banner()
    
    examples_text = f"""
{Fore.GREEN}🚀 GA-Scrap Usage Examples:{Style.RESET_ALL}

{Fore.CYAN}🚀 SUPER QUICK SCRAPING:{Style.RESET_ALL}
   ga-scrap quick "https://quotes.toscrape.com" ".quote .text" --all
   ga-scrap quick "https://example.com" "h1"

{Fore.CYAN}🛠️  SETUP & CONFIGURATION:{Style.RESET_ALL}
   ga-scrap setup                    # Set up GA-Scrap environment
   ga-scrap doctor                   # Check installation health
   ga-scrap config show              # Show current configuration
   ga-scrap config set browser.headless true

{Fore.CYAN}📱 APP MANAGEMENT:{Style.RESET_ALL}
   ga-scrap new my-scraper           # Create basic scraper
   ga-scrap new shop-scraper --template ecommerce
   ga-scrap list                     # List all apps
   ga-scrap info my-scraper          # Get app details
   ga-scrap delete my-scraper        # Delete an app

{Fore.CYAN}🔥 DEVELOPMENT:{Style.RESET_ALL}
   cd ga_scrap_apps/my-scraper
   ga-scrap dev                      # Start with hot reload
   ga-scrap run my_script.py         # Run any script with hot reload

{Fore.YELLOW}💡 Tips:{Style.RESET_ALL}
- Use 'ga-scrap quick' for instant scraping
- Use 'ga-scrap new' to create apps (shorter than 'create')
- All scrapers run with visible browser by default
- Use hot reload for faster development
- Check out different templates for specific use cases
- Edit config.yaml to customize scraper behavior
"""
    
    print(examples_text)

@cli.command()
@click.argument('url')
@click.argument('selector')
@click.option('--headless', is_flag=True, help='Run in headless mode')
@click.option('--all', 'get_all', is_flag=True, help='Get all matching elements')
def quick(url, selector, headless, get_all):
    """Quick scrape - get text from a website instantly"""
    import asyncio
    from .simple import scrape, scrape_all

    async def do_scrape():
        try:
            if get_all:
                results = await scrape_all(url, selector, headless)
                for i, result in enumerate(results, 1):
                    print(f"{Fore.CYAN}{i}. {result}{Style.RESET_ALL}")
            else:
                result = await scrape(url, selector, headless)
                print(f"{Fore.GREEN}{result}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")

    asyncio.run(do_scrape())

@cli.group()
def config_cmd():
    """Manage GA-Scrap configuration"""
    pass

@config_cmd.command('show')
def config_show():
    """Show current configuration"""
    config.show_config()

@config_cmd.command('get')
@click.argument('key')
def config_get(key):
    """Get a configuration value"""
    value = config.get(key)
    if value is not None:
        print(f"{Fore.CYAN}{key}:{Style.RESET_ALL} {value}")
    else:
        print(f"{Fore.RED}Key '{key}' not found{Style.RESET_ALL}")

@config_cmd.command('set')
@click.argument('key')
@click.argument('value')
def config_set(key, value):
    """Set a configuration value"""
    # Try to parse value as appropriate type
    if value.lower() in ('true', 'false'):
        value = value.lower() == 'true'
    elif value.isdigit():
        value = int(value)
    elif value.replace('.', '').isdigit():
        value = float(value)

    if config.set(key, value):
        print(f"{Fore.GREEN}✅ Set {key} = {value}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Failed to set {key}{Style.RESET_ALL}")

@config_cmd.command('reset')
@click.confirmation_option(prompt='Are you sure you want to reset all configuration to defaults?')
def config_reset():
    """Reset configuration to defaults"""
    if config.reset_to_defaults():
        print(f"{Fore.GREEN}✅ Configuration reset to defaults{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Failed to reset configuration{Style.RESET_ALL}")

@config_cmd.command('validate')
def config_validate():
    """Validate current configuration"""
    config.validate_config()

# Add config command to main CLI
cli.add_command(config_cmd, name='config')

@cli.command()
@click.option('--force', is_flag=True, help='Force reinstall browsers and recreate workspace')
def setup(force):
    """Set up GA-Scrap environment (browsers, workspace, etc.)"""
    print_banner()

    print(f"{Fore.GREEN}🚀 Setting up GA-Scrap environment...{Style.RESET_ALL}\n")

    try:
        # Install Playwright browsers
        print(f"{Fore.CYAN}📦 Installing Playwright browsers...{Style.RESET_ALL}")
        import subprocess

        if force:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "--force"])
        else:
            subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])

        print(f"{Fore.GREEN}✅ Playwright browsers installed{Style.RESET_ALL}")

        # Create workspace directory
        workspace_dir = config.get_workspace_dir()
        if force and workspace_dir.exists():
            import shutil
            shutil.rmtree(workspace_dir)
            print(f"{Fore.YELLOW}🗑️  Removed existing workspace{Style.RESET_ALL}")

        if not workspace_dir.exists():
            workspace_dir.mkdir(parents=True, exist_ok=True)
            print(f"{Fore.GREEN}✅ Created workspace: {workspace_dir}{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}✅ Workspace exists: {workspace_dir}{Style.RESET_ALL}")

        # Create a welcome example if enabled
        if config.get("auto_setup.create_welcome_app", True):
            welcome_dir = workspace_dir / "welcome-example"
            if force or not welcome_dir.exists():
                manager = AppManager()
                manager.create_app(
                    app_name="welcome-example",
                    template="basic",
                    description="Welcome example to get you started",
                    overwrite=force,
                    workspace_dir=str(workspace_dir)
                )
                print(f"{Fore.GREEN}✅ Created welcome example app{Style.RESET_ALL}")

        # Save configuration (this will create the config file if it doesn't exist)
        if force or not config.config_file.exists():
            config.save_config()
            print(f"{Fore.GREEN}✅ Created configuration: {config.config_file}{Style.RESET_ALL}")

        print(f"\n{Fore.GREEN}🎉 Setup complete! Try these commands:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   ga-scrap quick 'https://quotes.toscrape.com' '.quote .text' --all{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   ga-scrap new my-scraper{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   ga-scrap list{Style.RESET_ALL}")
        print(f"{Fore.CYAN}   ga-scrap doctor{Style.RESET_ALL}")

    except Exception as e:
        print(f"{Fore.RED}❌ Setup failed: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}💡 Try running with --force or check your internet connection{Style.RESET_ALL}")

@cli.command()
def doctor():
    """Check GA-Scrap installation and dependencies"""
    print_banner()

    print(f"{Fore.GREEN}🔍 GA-Scrap Health Check:{Style.RESET_ALL}\n")

    # Check Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"{Fore.GREEN}✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}❌ Python {python_version.major}.{python_version.minor}.{python_version.micro} (requires 3.8+){Style.RESET_ALL}")

    # Check dependencies
    dependencies = ['playwright', 'watchdog', 'click', 'colorama', 'yaml']

    for dep in dependencies:
        try:
            __import__(dep)
            print(f"{Fore.GREEN}✅ {dep}{Style.RESET_ALL}")
        except ImportError:
            print(f"{Fore.RED}❌ {dep} (not installed){Style.RESET_ALL}")

    # Check Playwright browsers
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browsers = ['chromium', 'firefox', 'webkit']
            for browser in browsers:
                try:
                    browser_obj = getattr(p, browser)
                    # This will fail if browser is not installed
                    executable_path = browser_obj.executable_path
                    print(f"{Fore.GREEN}✅ Playwright {browser}{Style.RESET_ALL}")
                except Exception:
                    print(f"{Fore.YELLOW}⚠️  Playwright {browser} (not installed){Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}❌ Playwright browser check failed: {e}{Style.RESET_ALL}")

    # Check workspace
    workspace = config.get_workspace_dir()
    if workspace.exists():
        app_count = len([d for d in workspace.iterdir() if d.is_dir()])
        print(f"{Fore.GREEN}✅ Workspace: {workspace} ({app_count} apps){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Workspace: {workspace} (will be created when needed){Style.RESET_ALL}")

    # Check config
    if config.config_file.exists():
        print(f"{Fore.GREEN}✅ Config: {config.config_file}{Style.RESET_ALL}")
        # Validate configuration
        if not config.validate_config():
            print(f"{Fore.YELLOW}⚠️  Configuration has issues (see above){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Config: {config.config_file} (will be created when needed){Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}💡 If you see any issues, try:{Style.RESET_ALL}")
    print(f"   ga-scrap setup --force")
    print(f"   pip install --upgrade ga-scrap")

def main():
    """Main CLI entry point"""
    try:
        cli()
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
