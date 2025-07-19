# GA-Scrap Quick Start Guide 🚀

Welcome to GA-Scrap! This guide will get you up and running in minutes.

## What is GA-Scrap?

GA-Scrap is a powerful Playwright-based scraper helper that:
- **Always runs browser by default** - See what you're scraping!
- **Creates multiple scraper apps** - Organize your projects
- **Hot reload support** - Edit code and see changes instantly
- **Easy configuration** - YAML/JSON config files
- **Beautiful CLI** - Colorful command-line interface

## Installation

### Option 1: Clone from GitHub

```bash
git clone https://github.com/GrandpaAcademy/GA-Scrap.git
cd GA-Scrap
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
playwright install
pip install -e .
```

### Option 2: If you already have it

```bash
source venv/bin/activate
```

## Your First Scraper

### 🚀 SUPER QUICK - One-liner scraping!

```bash
# Get page title instantly
ga-scrap quick "https://example.com" "h1"

# Get all quotes from a page
ga-scrap quick "https://quotes.toscrape.com" ".quote .text" --all
```

### 1. Create a New App (Traditional way)

```bash
ga-scrap create my-first-scraper
```

This creates a new scraper app with:
- `main.py` - Your main scraper script (now super simple!)
- `config.yaml` - Configuration file
- `README.md` - Documentation

### 2. Start Development

```bash
cd ga_scrap_apps/my-first-scraper
ga-scrap dev
```

This starts your scraper with hot reload. Edit `main.py` and watch it restart automatically!

### 3. Super Simple Scraping

The new `main.py` uses the ultra-easy `SimpleScraper`:

```python
import asyncio
from ga_scrap import SimpleScraper

async def main():
    async with SimpleScraper() as scraper:
        # Navigate to your target site
        await scraper.go("https://quotes.toscrape.com")

        # Get page title (super easy!)
        title = await scraper.get("title")
        scraper.log(f"Title: {title}")

        # Get all quotes (even easier!)
        quotes = await scraper.get_all(".quote .text")
        scraper.log(f"Found {len(quotes)} quotes")

        # Take a screenshot
        await scraper.screenshot()

        # Pause to see the browser
        await scraper.pause("Press Enter to continue...")

asyncio.run(main())
```

### 4. One-liner Functions

For super quick scraping:

```python
import asyncio
from ga_scrap import scrape, scrape_all, scrape_data

async def quick_examples():
    # Get single element
    title = await scrape("https://example.com", "h1")

    # Get multiple elements
    quotes = await scrape_all("https://quotes.toscrape.com", ".quote .text")

    # Get structured data
    data = await scrape_data("https://quotes.toscrape.com", {
        "title": "title",
        "quotes": ".quote .text[]",  # [] means get all
        "authors": ".quote .author[]"
    })

asyncio.run(quick_examples())
```

## Available Templates

```bash
ga-scrap templates
```

- **basic** - Simple scraper setup
- **advanced** - Data export, utilities
- **ecommerce** - Product scraping
- **social** - Social media scraping

## Common Commands

```bash
# 🚀 SUPER QUICK SCRAPING
ga-scrap quick "URL" "selector"              # Get single element
ga-scrap quick "URL" "selector" --all        # Get all matching elements
ga-scrap quick "URL" "selector" --headless   # Run without visible browser

# Create apps
ga-scrap create my-scraper --template advanced
ga-scrap create shop-scraper --template ecommerce

# Manage apps
ga-scrap list                    # List all apps
ga-scrap info my-scraper        # App details
ga-scrap delete old-scraper     # Delete app

# Development
ga-scrap dev                    # Start with hot reload
ga-scrap run script.py          # Run any script with hot reload

# Help
ga-scrap examples              # Usage examples
ga-scrap doctor               # Check installation
```

## Examples

Try the included examples:

```bash
# Basic scraping example
python examples/basic_example.py

# Advanced features
python examples/advanced_example.py

# Hot reload demo
ga-scrap run examples/hot_reload_example.py
```

## Key Features

### 1. Visible Browser by Default
- See exactly what your scraper is doing
- Perfect for development and debugging
- Easy to switch to headless for production

### 2. Hot Reload
- Edit your code and see changes instantly
- No need to manually restart
- Keeps browser session active

### 3. App Management
- Organize scrapers into separate apps
- Templates for different use cases
- Easy project structure

### 4. Configuration
Edit `config.yaml` in your app:

```yaml
browser:
  headless: false
  browser_type: "chromium"
  viewport:
    width: 1920
    height: 1080

scraping:
  delay_between_requests: 1000
  max_retries: 3
```

## Tips

1. **Start with visible browser** - Use `headless=False` during development
2. **Use hot reload** - Run `ga-scrap dev` for faster development
3. **Check examples** - Look at `examples/` directory for inspiration
4. **Use templates** - Start with appropriate template for your use case
5. **Configure properly** - Edit `config.yaml` for your needs

## Troubleshooting

```bash
# Check installation
ga-scrap doctor

# If browsers not installed
playwright install

# If dependencies missing
pip install -r requirements.txt
```

## Next Steps

1. **Create your first scraper**: `ga-scrap create my-scraper`
2. **Start development**: `ga-scrap dev`
3. **Edit main.py** to scrape your target site
4. **Check examples** for inspiration
5. **Read the full README.md** for advanced features

Happy Scraping! 🕷️✨

---

**Need help?**
- Run `ga-scrap examples` for usage examples
- Check [examples/](https://github.com/GrandpaAcademy/GA-Scrap/tree/main/examples) directory for sample code
- Use `ga-scrap doctor` to diagnose issues
- Read the full [README.md](https://github.com/GrandpaAcademy/GA-Scrap/blob/main/README.md)
- Report issues: [GitHub Issues](https://github.com/GrandpaAcademy/GA-Scrap/issues)
