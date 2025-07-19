"""
GA-Scrap Configuration Manager
Handles global configuration and user preferences
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from colorama import Fore, Style

class ConfigManager:
    """
    Manages GA-Scrap global configuration
    
    Features:
    - Global settings management
    - User preferences
    - Workspace configuration
    - Browser settings
    """
    
    def __init__(self):
        """Initialize configuration manager"""
        self.config_dir = Path.home() / ".ga_scrap"
        self.config_file = self.config_dir / "config.yaml"
        self.config_dir.mkdir(exist_ok=True)
        
        # Default configuration
        self.default_config = {
            "workspace_dir": "~/ga_scrap_apps",
            "default_template": "basic",
            "browser": {
                "headless": False,
                "slow_mo": 500,
                "timeout": 30000,
                "viewport": {
                    "width": 1280,
                    "height": 720
                }
            },
            "dev_server": {
                "port": 8000,
                "auto_reload": True,
                "watch_extensions": [".py", ".yaml", ".json"]
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "auto_setup": {
                "install_browsers": True,
                "create_workspace": True,
                "create_welcome_app": True
            }
        }
        
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = yaml.safe_load(f) or {}
                
                # Merge with defaults
                config = self.default_config.copy()
                config.update(user_config)
                return config
                
            except Exception as e:
                print(f"{Fore.YELLOW}Warning: Could not load config: {e}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Using default configuration{Style.RESET_ALL}")
        
        return self.default_config.copy()
    
    def save_config(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            print(f"{Fore.RED}Error: Could not save config: {e}{Style.RESET_ALL}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> bool:
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
        return self.save_config()
    
    def get_workspace_dir(self) -> Path:
        """Get workspace directory path"""
        workspace = self.get("workspace_dir", "~/ga_scrap_apps")
        return Path(workspace).expanduser()
    
    def reset_to_defaults(self) -> bool:
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        return self.save_config()
    
    def show_config(self):
        """Display current configuration"""
        print(f"{Fore.GREEN}📋 GA-Scrap Configuration:{Style.RESET_ALL}\n")
        print(f"{Fore.CYAN}Config file: {self.config_file}{Style.RESET_ALL}\n")
        
        def print_dict(d, indent=0):
            for key, value in d.items():
                spaces = "  " * indent
                if isinstance(value, dict):
                    print(f"{spaces}{Fore.YELLOW}{key}:{Style.RESET_ALL}")
                    print_dict(value, indent + 1)
                else:
                    print(f"{spaces}{Fore.CYAN}{key}:{Style.RESET_ALL} {value}")
        
        print_dict(self.config)
    
    def validate_config(self) -> bool:
        """Validate configuration"""
        issues = []
        
        # Check workspace directory
        workspace = self.get_workspace_dir()
        if not workspace.parent.exists():
            issues.append(f"Workspace parent directory does not exist: {workspace.parent}")
        
        # Check browser settings
        timeout = self.get("browser.timeout", 30000)
        if not isinstance(timeout, int) or timeout < 1000:
            issues.append("Browser timeout must be an integer >= 1000ms")
        
        # Check dev server port
        port = self.get("dev_server.port", 8000)
        if not isinstance(port, int) or port < 1024 or port > 65535:
            issues.append("Dev server port must be between 1024 and 65535")
        
        if issues:
            print(f"{Fore.RED}❌ Configuration issues found:{Style.RESET_ALL}")
            for issue in issues:
                print(f"   • {issue}")
            return False
        
        print(f"{Fore.GREEN}✅ Configuration is valid{Style.RESET_ALL}")
        return True

# Global config instance
config = ConfigManager()
