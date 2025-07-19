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

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """GA-Scrap: A powerful Playwright-based scraper helper"""
    pass

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

{Fore.CYAN}1. Create a new basic scraper:{Style.RESET_ALL}
   ga-scrap new my-scraper

{Fore.CYAN}2. Create an e-commerce scraper:{Style.RESET_ALL}
   ga-scrap new shop-scraper --template ecommerce

{Fore.CYAN}3. Start development with hot reload:{Style.RESET_ALL}
   cd ga_scrap_apps/my-scraper
   ga-scrap dev

{Fore.CYAN}4. Run any Python script with hot reload:{Style.RESET_ALL}
   ga-scrap run my_script.py

{Fore.CYAN}5. List all your apps:{Style.RESET_ALL}
   ga-scrap list

{Fore.CYAN}6. Get app information:{Style.RESET_ALL}
   ga-scrap info my-scraper

{Fore.CYAN}7. Delete an app:{Style.RESET_ALL}
   ga-scrap delete my-scraper

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
    dependencies = ['playwright', 'watchdog', 'click', 'colorama', 'pyyaml']

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
    workspace = Path("ga_scrap_apps")
    if workspace.exists():
        app_count = len([d for d in workspace.iterdir() if d.is_dir()])
        print(f"{Fore.GREEN}✅ Workspace: {workspace} ({app_count} apps){Style.RESET_ALL}")
    else:
        print(f"{Fore.YELLOW}⚠️  Workspace: {workspace} (will be created when needed){Style.RESET_ALL}")

    print(f"\n{Fore.CYAN}💡 If you see any issues, try:{Style.RESET_ALL}")
    print(f"   pip install playwright watchdog click colorama pyyaml")
    print(f"   playwright install")

def main():
    """Main CLI entry point"""
    try:
        cli()
    except Exception as e:
        print(f"{Fore.RED}❌ Error: {e}{Style.RESET_ALL}")
        sys.exit(1)

if __name__ == '__main__':
    main()
