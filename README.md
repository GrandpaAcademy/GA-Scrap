# GA-Scrap 🚀

A powerful Playwright-based scraper helper that makes web scraping easy and enjoyable!

## ✨ Features

### 🚀 Core Features
- **🖥️ Always runs browser by default** - See what you're scraping in real-time
- **📱 Create multiple scraper apps** - Organize your scrapers with templates
- **🔥 Hot reload support** - Edit your code and see changes instantly
- **🎯 Easy configuration** - YAML/JSON configuration files
- **🛠️ Built-in utilities** - Data export, logging, error handling
- **🎨 Beautiful CLI** - Colorful command-line interface
- **📋 Multiple templates** - Basic, Advanced, E-commerce, Social media

### 🌟 EVERY Playwright Feature Included
- **🌐 Complete Network Control** - Request/response interception, HAR recording, network throttling
- **📱 Full Device Emulation** - iPhone, Android, tablets with touch simulation
- **🎥 Video Recording** - Record your scraping sessions automatically
- **📊 Performance Monitoring** - Track Core Web Vitals, coverage analysis
- **♿ Accessibility Testing** - Built-in accessibility checks and ARIA support
- **🔧 Advanced Interactions** - Drag & drop, smooth mouse movement, keyboard shortcuts
- **📁 File Operations** - Upload/download files, PDF generation
- **💾 Storage Management** - Cookies, localStorage, sessionStorage, IndexedDB
- **🖼️ Frame Support** - Handle iframes and nested frames
- **⏳ Smart Waiting** - Network idle, custom functions, element visibility
- **🔐 Security Features** - Permission management, geolocation, secure contexts
- **🌍 Internationalization** - Locale, timezone, currency formatting
- **📋 Clipboard Operations** - Copy/paste functionality
- **🔄 Event Monitoring** - Comprehensive event capture and handling
- **🎨 Visual Features** - CSS injection, style computation, theming
- **👷 Worker Support** - Web Workers, Service Workers, background pages
- **🔌 WebSocket Support** - Real-time communication monitoring
- **🔍 Advanced Locators** - Text, role, label, placeholder-based selection
- **📜 Infinite Scroll** - Automatic content loading detection
- **🛠️ Developer Tools** - Console capture, error tracking, debugging

### 📈 200+ Playwright Features
See [PLAYWRIGHT_FEATURES.md](PLAYWRIGHT_FEATURES.md) for the complete list of all implemented features.

### 🎯 Two Interfaces Available

#### 1. Synchronous Interface (Recommended for beginners)
```python
from ga_scrap import SyncGAScrap

with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    print(f"Title: {title}")
```

#### 2. Async Interface (For advanced users)
```python
import asyncio
from ga_scrap import GAScrap

async def scrape():
    async with GAScrap() as scraper:
        await scraper.goto("https://example.com")
        title = await scraper.get_text("h1")
        return title

result = asyncio.run(scrape())
```

See [SYNC_USAGE.md](SYNC_USAGE.md) for complete synchronous interface documentation.

## 🚀 Quick Start

### 🎯 Super Simple Syntax (No async/await needed!)

```python
from ga_scrap import SyncGAScrap

# Create scraper - no async needed!
with SyncGAScrap() as scraper:
    scraper.goto("https://example.com")
    title = scraper.get_text("h1")
    scraper.screenshot("page.png")
    print(f"Title: {title}")
```

**That's it!** No `async`/`await`, no `asyncio.run()` - just simple, clean Python code!

### 🔗 Method Chaining Support

```python
with SyncGAScrap() as scraper:
    (scraper
     .goto("https://example.com")
     .scroll_to_bottom()
     .screenshot("bottom.png")
     .input("input[name='q']", "search term")
     .click("button[type='submit']")
     .screenshot("results.png"))
```

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/GrandpaAcademy/GA-Scrap.git
   cd GA-Scrap
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   playwright install
   ```

4. **Install GA-Scrap:**
   ```bash
   pip install -e .
   ```

### 🚀 SUPER QUICK - One-liner scraping!

```bash
# Get page title instantly
ga-scrap quick "https://example.com" "h1"

# Get all quotes from a page
ga-scrap quick "https://quotes.toscrape.com" ".quote .text" --all
```

### Create Your First Scraper

```bash
# Create a new scraper app
ga-scrap new my-first-scraper

# Navigate to the app directory
cd ga_scrap_apps/my-first-scraper

# Start development with hot reload
ga-scrap dev
```

That's it! Your browser will open and you can start scraping. Edit `main.py` to customize your scraper.

## 📖 Usage

### CLI Commands

```bash
# 🚀 SUPER QUICK SCRAPING
ga-scrap quick "URL" "selector"              # Get single element
ga-scrap quick "URL" "selector" --all        # Get all matching elements
ga-scrap quick "URL" "selector" --headless   # Run without visible browser

# Create a new app
ga-scrap new <app_name> [--template basic|advanced|ecommerce|social]

# List all apps
ga-scrap list

# Start development server with hot reload
ga-scrap dev [--app-dir <directory>]

# Run any script with hot reload
ga-scrap run <script.py>

# Show app information
ga-scrap info <app_name>

# Delete an app
ga-scrap delete <app_name>

# Show available templates
ga-scrap templates

# Show usage examples
ga-scrap examples

# Check installation
ga-scrap doctor
```

### Super Simple Usage

```python
import asyncio
from ga_scrap import SimpleScraper

async def main():
    async with SimpleScraper() as scraper:
        # Navigate to website
        await scraper.go("https://quotes.toscrape.com")

        # Get page title (super easy!)
        title = await scraper.get("title")
        scraper.log(f"Title: {title}")

        # Get all quotes (even easier!)
        quotes = await scraper.get_all(".quote .text")
        scraper.log(f"Found {len(quotes)} quotes")

        # Take a screenshot
        await scraper.screenshot()

asyncio.run(main())
```

### One-liner Functions

```python
from ga_scrap import scrape, scrape_all, scrape_data

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
```

## 🎯 Templates

### Basic Template
- Simple scraper setup
- Visible browser by default
- Basic navigation and extraction
- Configuration file

### Advanced Template
- All basic features
- Data export (JSON/CSV)
- Multiple page handling
- Advanced utilities

### E-commerce Template
- Product detail extraction
- Category page scraping
- Price monitoring
- Image collection

### Social Media Template
- Post extraction
- Profile scraping
- Engagement metrics
- Media collection

## 🔥 Hot Reload

GA-Scrap includes powerful hot reload functionality:

```bash
# Start any script with hot reload
ga-scrap run my_script.py

# Or use the development server
ga-scrap dev
```

When you edit your Python files, the scraper automatically restarts while keeping your browser session active.

## ⚙️ Configuration

Create a `config.yaml` file in your app directory:

```yaml
app:
  name: "my-scraper"
  version: "1.0.0"

browser:
  headless: false
  browser_type: "chromium"
  viewport:
    width: 1920
    height: 1080
  timeout: 30000

scraping:
  delay_between_requests: 1000
  max_retries: 3

targets:
  - name: "example"
    url: "https://example.com"
    selectors:
      title: "h1"
      links: "a"
```

## 📁 Project Structure

```
ga-scrap/
├── ga_scrap/
│   ├── __init__.py
│   ├── core.py          # Main GAScrap class
│   ├── app_manager.py   # App creation and management
│   ├── hot_reload.py    # Hot reload functionality
│   └── cli.py           # Command-line interface
├── examples/
│   ├── basic_example.py
│   ├── advanced_example.py
│   └── hot_reload_example.py
├── ga_scrap_apps/       # Your scraper apps go here
├── requirements.txt
├── setup.py
└── README.md
```

## 🎨 Examples

### Super Simple Scraping
```python
from ga_scrap import SimpleScraper

async def scrape_quotes():
    async with SimpleScraper() as scraper:
        await scraper.go("https://quotes.toscrape.com/")

        # Get all quotes in one line!
        quotes = await scraper.get_all(".quote .text")
        authors = await scraper.get_all(".quote .author")

        for quote, author in zip(quotes, authors):
            print(f'"{quote}" - {author}')
```

### One-liner Examples
```python
from ga_scrap import scrape, scrape_all, scrape_data

# Get page title
title = await scrape("https://example.com", "h1")

# Get all quotes
quotes = await scrape_all("https://quotes.toscrape.com", ".quote .text")

# Get structured data
data = await scrape_data("https://quotes.toscrape.com", {
    "title": "title",
    "quotes": ".quote .text[]",
    "authors": ".quote .author[]"
})
```

### CLI One-liners
```bash
# Get page title instantly
ga-scrap quick "https://example.com" "h1"

# Get all quotes
ga-scrap quick "https://quotes.toscrape.com" ".quote .text" --all

# Get product names
ga-scrap quick "https://example-shop.com" ".product-name" --all
```

## 🛠️ Advanced Features

### Multiple Pages
```python
# Create additional pages
page2 = await scraper.new_page()
await page2.goto("https://another-site.com")

# Work with multiple pages simultaneously
await asyncio.gather(
    scraper.goto("https://site1.com"),
    page2.goto("https://site2.com")
)
```

### Data Export
```python
from ga_scrap.utils import DataExporter

exporter = DataExporter()
exporter.to_json(scraped_data, "results")
exporter.to_csv(scraped_data, "results")
```

### Custom Configuration
```python
scraper = GAScrap(
    headless=False,
    browser_type="firefox",
    viewport={"width": 1366, "height": 768},
    user_agent="Custom User Agent",
    timeout=60000,
    slow_mo=1000  # Slow down for debugging
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📚 Documentation

- **[Quick Start Guide](QUICK_START.md)** - Get started in minutes
- **[Examples Directory](examples/)** - Sample scraper applications
- **CLI Help**: Run `ga-scrap examples` for usage examples
- **GitHub Issues**: [Report bugs or request features](https://github.com/GrandpaAcademy/GA-Scrap/issues)

## 🆘 Support

- Check `ga-scrap doctor` for installation issues
- Use `ga-scrap examples` for usage examples
- Enable debug mode: `SimpleScraper(debug=True)`
- Check the [examples directory](examples/) for sample code
- Read the [Quick Start Guide](QUICK_START.md)

## 🤝 Contributing

1. Fork the repository: https://github.com/GrandpaAcademy/GA-Scrap
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add amazing feature'`
5. Push to the branch: `git push origin feature/amazing-feature`
6. Submit a pull request

## 🎉 Why GA-Scrap?

- **🚀 Super Easy**: One-liner functions and CLI commands
- **👀 Beginner Friendly**: See your scraper in action with visible browser
- **⚡ Developer Friendly**: Hot reload for faster development
- **🔧 Production Ready**: Easy to switch to headless mode
- **📱 Organized**: Template system keeps your scrapers organized
- **💪 Powerful**: Built on Playwright for modern web scraping
- **🎯 Instant Results**: Get data with single commands

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Credits

Created by [Grandpa Academy](https://github.com/GrandpaAcademy) with ❤️

Happy Scraping! 🕷️✨
