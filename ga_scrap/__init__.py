"""
GA-Scrap: A powerful Playwright-based scraper helper
"""

__version__ = "1.0.0"
__author__ = "Grandpa Academy"

from .core import GAScrap
from .app_manager import AppManager
from .hot_reload import HotReloader
from .simple import SimpleScraper, scrape, scrape_all, scrape_data
from .translator import SyncGAScrap, create_scraper

__all__ = ["GAScrap", "SyncGAScrap", "create_scraper", "AppManager", "HotReloader", "SimpleScraper", "scrape", "scrape_all", "scrape_data"]
