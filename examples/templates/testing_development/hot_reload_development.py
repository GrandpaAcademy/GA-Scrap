"""
Hot Reload Development Template
Development environment with hot reload capabilities for rapid scraper development
"""

import sys
import os
import json
import time
import threading
from datetime import datetime
from typing import Dict, Any, Callable, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class ScraperConfigHandler(FileSystemEventHandler):
    """File system event handler for scraper configuration changes"""
    
    def __init__(self, reload_callback: Callable):
        """
        Initialize config handler
        
        Args:
            reload_callback: Function to call when config changes
        """
        self.reload_callback = reload_callback
        self.last_reload = 0
        self.reload_delay = 1  # Minimum seconds between reloads
        
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
            
        # Only reload for JSON config files
        if event.src_path.endswith('.json'):
            current_time = time.time()
            if current_time - self.last_reload > self.reload_delay:
                self.last_reload = current_time
                print(f"🔄 Config file changed: {event.src_path}")
                self.reload_callback(event.src_path)

class HotReloadScraper:
    """Development scraper with hot reload capabilities"""
    
    def __init__(self, config_file: str = "scraper_config.json", watch_dir: str = "."):
        """
        Initialize hot reload scraper
        
        Args:
            config_file: Path to scraper configuration file
            watch_dir: Directory to watch for config changes
        """
        self.config_file = config_file
        self.watch_dir = watch_dir
        self.config = self._load_config()
        self.is_running = False
        self.observer = None
        self.scraper_instance = None
        
        # Development state
        self.dev_state = {
            "last_reload": datetime.now().isoformat(),
            "reload_count": 0,
            "last_results": {},
            "errors": []
        }
        
    def _load_config(self) -> Dict[str, Any]:
        """Load scraper configuration"""
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                print(f"✅ Loaded config from {self.config_file}")
                return config
        except FileNotFoundError:
            print(f"⚠️ Config file not found, creating default: {self.config_file}")
            return self._create_default_config()
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in config file: {e}")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default development configuration"""
        default_config = {
            "target_url": "https://httpbin.org/html",
            "selectors": {
                "title": "title",
                "heading": "h1",
                "paragraphs": "p[]",
                "links": "a@href[]"
            },
            "actions": [
                {
                    "type": "navigate",
                    "url": "https://httpbin.org/html"
                },
                {
                    "type": "extract",
                    "name": "page_data"
                },
                {
                    "type": "log_results"
                }
            ],
            "dev_settings": {
                "auto_reload": True,
                "show_browser": True,
                "debug_mode": True,
                "save_screenshots": True,
                "reload_interval": 2
            }
        }
        
        with open(self.config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        
        print(f"📝 Created default config: {self.config_file}")
        return default_config
    
    def start_development_mode(self):
        """Start development mode with hot reload"""
        print("🚀 Starting hot reload development mode...")
        print(f"📁 Watching directory: {self.watch_dir}")
        print(f"⚙️ Config file: {self.config_file}")
        print("Press Ctrl+C to stop")
        
        # Setup file watcher
        event_handler = ScraperConfigHandler(self._on_config_change)
        self.observer = Observer()
        self.observer.schedule(event_handler, self.watch_dir, recursive=True)
        self.observer.start()
        
        self.is_running = True
        
        try:
            # Initial run
            self._execute_scraper()
            
            # Keep running and watching for changes
            while self.is_running:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n👋 Stopping development mode...")
            self.stop_development_mode()
    
    def stop_development_mode(self):
        """Stop development mode"""
        self.is_running = False
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        if self.scraper_instance:
            try:
                self.scraper_instance.close()
            except:
                pass
    
    def _on_config_change(self, file_path: str):
        """Handle configuration file changes"""
        if file_path == os.path.abspath(self.config_file):
            print("🔄 Reloading scraper configuration...")
            
            # Reload config
            old_config = self.config.copy()
            self.config = self._load_config()
            
            # Update dev state
            self.dev_state["last_reload"] = datetime.now().isoformat()
            self.dev_state["reload_count"] += 1
            
            # Show what changed
            self._show_config_changes(old_config, self.config)
            
            # Re-execute scraper with new config
            if self.config.get("dev_settings", {}).get("auto_reload", True):
                self._execute_scraper()
    
    def _show_config_changes(self, old_config: Dict[str, Any], new_config: Dict[str, Any]):
        """Show what changed in the configuration"""
        changes = []
        
        # Check for changed selectors
        old_selectors = old_config.get("selectors", {})
        new_selectors = new_config.get("selectors", {})
        
        for key, value in new_selectors.items():
            if key not in old_selectors:
                changes.append(f"+ Added selector '{key}': {value}")
            elif old_selectors[key] != value:
                changes.append(f"~ Changed selector '{key}': {old_selectors[key]} → {value}")
        
        for key in old_selectors:
            if key not in new_selectors:
                changes.append(f"- Removed selector '{key}'")
        
        # Check for URL changes
        if old_config.get("target_url") != new_config.get("target_url"):
            changes.append(f"~ Changed URL: {old_config.get('target_url')} → {new_config.get('target_url')}")
        
        if changes:
            print("📝 Configuration changes:")
            for change in changes:
                print(f"  {change}")
        else:
            print("📝 Configuration reloaded (no changes detected)")
    
    def _execute_scraper(self):
        """Execute scraper with current configuration"""
        start_time = time.time()
        
        try:
            print(f"\n🕷️ Executing scraper (reload #{self.dev_state['reload_count']})...")
            
            dev_settings = self.config.get("dev_settings", {})
            
            with SyncGAScrap(
                headless=not dev_settings.get("show_browser", True),
                sandbox_mode=True,
                debug=dev_settings.get("debug_mode", True)
            ) as scraper:
                
                # Execute actions from config
                results = {}
                for action in self.config.get("actions", []):
                    action_result = self._execute_action(scraper, action)
                    if action_result:
                        results.update(action_result)
                
                # Save results
                self.dev_state["last_results"] = results
                
                # Take screenshot if enabled
                if dev_settings.get("save_screenshots", True):
                    self._save_development_screenshot(scraper)
                
                duration = time.time() - start_time
                print(f"✅ Scraper execution completed in {duration:.2f}s")
                
                # Show results summary
                self._show_results_summary(results)
                
        except Exception as e:
            duration = time.time() - start_time
            error_msg = f"Scraper execution failed after {duration:.2f}s: {str(e)}"
            print(f"❌ {error_msg}")
            
            self.dev_state["errors"].append({
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            })
    
    def _execute_action(self, scraper: SyncGAScrap, action: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute a single action"""
        action_type = action.get("type")
        
        try:
            if action_type == "navigate":
                url = action.get("url", self.config.get("target_url"))
                scraper.goto(url)
                print(f"🌐 Navigated to: {url}")
                return {"navigation_url": url}
                
            elif action_type == "extract":
                extracted_data = {}
                selectors = self.config.get("selectors", {})
                
                for field_name, selector in selectors.items():
                    try:
                        if selector.endswith("[]"):
                            # Multiple elements
                            selector = selector[:-2]
                            if selector.endswith("@href") or selector.endswith("@src"):
                                # Attribute extraction
                                attr_selector, attr_name = selector.split("@")
                                values = scraper.get_all_attributes(attr_selector, attr_name)
                            else:
                                values = scraper.get_all_text(selector)
                            extracted_data[field_name] = values
                        elif "@" in selector:
                            # Single attribute
                            attr_selector, attr_name = selector.split("@")
                            value = scraper.get_attribute(attr_selector, attr_name)
                            extracted_data[field_name] = value
                        else:
                            # Single element text
                            value = scraper.get_text(selector)
                            extracted_data[field_name] = value
                            
                    except Exception as e:
                        extracted_data[field_name] = f"ERROR: {str(e)}"
                        print(f"⚠️ Failed to extract {field_name}: {e}")
                
                action_name = action.get("name", "extracted_data")
                print(f"📊 Extracted {len(extracted_data)} fields")
                return {action_name: extracted_data}
                
            elif action_type == "click":
                selector = action.get("selector")
                scraper.click(selector)
                print(f"👆 Clicked: {selector}")
                return {"clicked": selector}
                
            elif action_type == "input":
                selector = action.get("selector")
                value = action.get("value")
                scraper.input(selector, value)
                print(f"⌨️ Input '{value}' into: {selector}")
                return {"input": {"selector": selector, "value": value}}
                
            elif action_type == "wait":
                duration = action.get("duration", 1)
                time.sleep(duration)
                print(f"⏳ Waited {duration} seconds")
                return {"waited": duration}
                
            elif action_type == "log_results":
                # This is handled in _show_results_summary
                return None
                
            else:
                print(f"⚠️ Unknown action type: {action_type}")
                return None
                
        except Exception as e:
            print(f"❌ Action '{action_type}' failed: {e}")
            return {"error": str(e)}
    
    def _save_development_screenshot(self, scraper: SyncGAScrap):
        """Save screenshot for development reference"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = f"dev_screenshot_{timestamp}.png"
        
        try:
            scraper.screenshot(screenshot_path)
            print(f"📸 Screenshot saved: {screenshot_path}")
        except Exception as e:
            print(f"⚠️ Could not save screenshot: {e}")
    
    def _show_results_summary(self, results: Dict[str, Any]):
        """Show summary of extraction results"""
        print("\n📊 Results Summary:")
        print("-" * 30)
        
        for key, value in results.items():
            if isinstance(value, dict):
                print(f"📂 {key}:")
                for subkey, subvalue in value.items():
                    if isinstance(subvalue, list):
                        print(f"  📋 {subkey}: {len(subvalue)} items")
                        if subvalue:
                            print(f"      First: {str(subvalue[0])[:50]}...")
                    else:
                        print(f"  📄 {subkey}: {str(subvalue)[:50]}...")
            elif isinstance(value, list):
                print(f"📋 {key}: {len(value)} items")
            else:
                print(f"📄 {key}: {str(value)[:50]}...")
        
        print("-" * 30)
    
    def get_development_status(self) -> Dict[str, Any]:
        """Get current development status"""
        return {
            "is_running": self.is_running,
            "config_file": self.config_file,
            "dev_state": self.dev_state,
            "current_config": self.config
        }
    
    def manual_reload(self):
        """Manually trigger a reload"""
        print("🔄 Manual reload triggered...")
        self._execute_scraper()

# Example usage and development scenarios
def example_interactive_development():
    """Example: Interactive development with hot reload"""
    print("🚀 Interactive Development Example")
    print("=" * 50)
    
    # Create a development scraper
    dev_scraper = HotReloadScraper("dev_config.json")
    
    print("\n📝 Development Instructions:")
    print("1. Edit the 'dev_config.json' file to change scraping behavior")
    print("2. Modify selectors, URLs, or actions")
    print("3. Save the file to see changes applied automatically")
    print("4. The scraper will re-run with your new configuration")
    
    # Start development mode
    try:
        dev_scraper.start_development_mode()
    except KeyboardInterrupt:
        print("\n👋 Development session ended")

def example_selector_testing():
    """Example: Test different selectors interactively"""
    print("🎯 Selector Testing Example")
    print("=" * 50)
    
    # Create config for selector testing
    test_config = {
        "target_url": "https://httpbin.org/html",
        "selectors": {
            "title": "title",
            "heading": "h1",
            "all_text": "body"
        },
        "actions": [
            {"type": "navigate"},
            {"type": "extract", "name": "test_data"},
            {"type": "log_results"}
        ],
        "dev_settings": {
            "auto_reload": True,
            "show_browser": False,
            "debug_mode": True,
            "save_screenshots": False
        }
    }
    
    # Save test config
    with open("selector_test_config.json", "w") as f:
        json.dump(test_config, f, indent=2)
    
    print("📝 Created selector_test_config.json")
    print("Try modifying the selectors in the config file:")
    print("  - Change 'title' to 'h1'")
    print("  - Add new selectors like 'paragraphs': 'p[]'")
    print("  - Test different CSS selectors")
    
    # Start development mode
    dev_scraper = HotReloadScraper("selector_test_config.json")
    
    try:
        dev_scraper.start_development_mode()
    except KeyboardInterrupt:
        print("\n👋 Selector testing ended")

def main():
    """Main function to demonstrate hot reload development"""
    print("🔥 GA-Scrap Hot Reload Development Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Interactive development with hot reload")
    print("2. Selector testing environment")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        example_interactive_development()
    elif choice == "2":
        example_selector_testing()
    else:
        print("Invalid choice. Running interactive development...")
        example_interactive_development()

if __name__ == "__main__":
    main()
