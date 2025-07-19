# ⚡ Hot Reload

<div align="center">

**Faster Development with Instant Feedback**  
*Edit code, see changes immediately*

</div>

---

## 🎯 What is Hot Reload?

Hot reload automatically restarts your scraper when you edit your code, while keeping the browser session active. This dramatically speeds up development by eliminating manual restarts.

### 🆚 Traditional vs Hot Reload Development

<table>
<tr>
<td width="50%">

### 😴 **Traditional Development**
1. Write code
2. Run script
3. Test in browser
4. Stop script
5. Edit code
6. **Repeat from step 2** 😫

**Time per iteration: ~30-60 seconds**

</td>
<td width="50%">

### ⚡ **Hot Reload Development**
1. Write code
2. Run with hot reload
3. Edit code
4. **Changes applied instantly** ✨

**Time per iteration: ~2-5 seconds**

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Using CLI Command
```bash
# Start any script with hot reload
ga-scrap run my_scraper.py

# Start development server
ga-scrap dev

# Run with specific app directory
ga-scrap dev --app-dir ./my-scraper
```

### Using Python API
```python
from ga_scrap.hot_reload import HotReloadScraper

# Enable hot reload for your scraper
scraper = HotReloadScraper("my_scraper.py")
scraper.start()
```

---

## 🛠️ CLI Commands

### Basic Hot Reload
```bash
# Run any Python file with hot reload
ga-scrap run scraper.py

# Run with custom configuration
ga-scrap run scraper.py --headless --timeout 60000

# Run with sandbox mode
ga-scrap run scraper.py --sandbox
```

### Development Server
```bash
# Start development server (looks for main.py)
ga-scrap dev

# Specify custom entry point
ga-scrap dev --entry custom_scraper.py

# Run in specific directory
ga-scrap dev --app-dir ./my-project

# Development with custom browser
ga-scrap dev --browser firefox
```

### Advanced Options
```bash
# Watch specific file patterns
ga-scrap run scraper.py --watch "*.py,*.json,*.yaml"

# Exclude patterns from watching
ga-scrap run scraper.py --exclude "*.log,__pycache__/*"

# Set custom restart delay
ga-scrap run scraper.py --delay 2000  # 2 second delay
```

---

## 📁 Project Structure for Hot Reload

### Recommended Structure
```
my-scraper/
├── main.py              # Entry point
├── config.yaml          # Configuration
├── scrapers/
│   ├── __init__.py
│   ├── product_scraper.py
│   └── news_scraper.py
├── utils/
│   ├── __init__.py
│   └── helpers.py
└── data/
    └── output/
```

### Example main.py
```python
# main.py
from ga_scrap import SyncGAScrap
from scrapers.product_scraper import scrape_products
from utils.helpers import save_data

def main():
    """Main scraper function - hot reload will restart this"""
    print("🚀 Starting scraper...")
    
    with SyncGAScrap(sandbox_mode=True) as scraper:
        # Your scraping logic here
        data = scrape_products(scraper)
        save_data(data, "products.json")
        
        print(f"✅ Scraped {len(data)} products")

if __name__ == "__main__":
    main()
```

### Example config.yaml
```yaml
# config.yaml
app:
  name: "Product Scraper"
  version: "1.0.0"

browser:
  headless: false
  timeout: 30000
  sandbox_mode: true

scraping:
  base_url: "https://example.com"
  delay: 1000
  max_pages: 10

hot_reload:
  watch_patterns: ["*.py", "*.yaml", "*.json"]
  exclude_patterns: ["*.log", "__pycache__/*"]
  restart_delay: 1000
```

---

## 🔧 Configuration

### Hot Reload Settings
```python
from ga_scrap.hot_reload import HotReloadScraper

scraper = HotReloadScraper(
    script_path="my_scraper.py",
    watch_patterns=["*.py", "*.yaml"],  # Files to watch
    exclude_patterns=["*.log"],         # Files to ignore
    restart_delay=1000,                 # Delay before restart (ms)
    browser_persist=True,               # Keep browser open
    debug=True                          # Show reload messages
)
```

### Environment Variables
```bash
# Set hot reload preferences
export GA_SCRAP_HOT_RELOAD=true
export GA_SCRAP_WATCH_PATTERNS="*.py,*.json"
export GA_SCRAP_RESTART_DELAY=2000

# Run your scraper
python my_scraper.py
```

---

## 🎯 Development Workflow

### Typical Development Session
```bash
# 1. Start development server
ga-scrap dev

# 2. Edit your code in your favorite editor
# 3. Save file
# 4. See changes instantly in browser
# 5. Repeat steps 2-4
```

### Example Development Flow
```python
# main.py - Version 1
from ga_scrap import SyncGAScrap

def main():
    with SyncGAScrap(sandbox_mode=True) as scraper:
        scraper.goto("https://quotes.toscrape.com")
        quotes = scraper.get_all_text(".quote .text")
        print(f"Found {len(quotes)} quotes")

if __name__ == "__main__":
    main()
```

**Save file → Hot reload triggers → See results**

```python
# main.py - Version 2 (add authors)
from ga_scrap import SyncGAScrap

def main():
    with SyncGAScrap(sandbox_mode=True) as scraper:
        scraper.goto("https://quotes.toscrape.com")
        quotes = scraper.get_all_text(".quote .text")
        authors = scraper.get_all_text(".quote .author")  # Added this line
        
        for quote, author in zip(quotes, authors):
            print(f'"{quote}" - {author}')

if __name__ == "__main__":
    main()
```

**Save file → Hot reload triggers → See enhanced results**

---

## 🧪 Advanced Features

### Conditional Hot Reload
```python
import os
from ga_scrap import SyncGAScrap

def main():
    # Enable hot reload only in development
    is_dev = os.getenv("ENVIRONMENT") == "development"
    
    scraper_config = {
        "sandbox_mode": is_dev,
        "headless": not is_dev,
        "debug": is_dev
    }
    
    with SyncGAScrap(**scraper_config) as scraper:
        # Your scraping logic
        pass

if __name__ == "__main__":
    main()
```

### State Persistence
```python
import json
import os
from ga_scrap import SyncGAScrap

def load_state():
    """Load previous state if exists"""
    if os.path.exists("scraper_state.json"):
        with open("scraper_state.json", "r") as f:
            return json.load(f)
    return {"page": 1, "scraped_urls": []}

def save_state(state):
    """Save current state for hot reload"""
    with open("scraper_state.json", "w") as f:
        json.dump(state, f)

def main():
    # Load previous state
    state = load_state()
    
    with SyncGAScrap(sandbox_mode=True) as scraper:
        # Continue from where we left off
        start_page = state.get("page", 1)
        scraped_urls = state.get("scraped_urls", [])
        
        for page in range(start_page, 11):  # Pages 1-10
            url = f"https://example.com/page/{page}"
            
            if url in scraped_urls:
                continue  # Skip already scraped pages
            
            scraper.goto(url)
            data = scraper.get_all_text(".content")
            
            # Update state
            scraped_urls.append(url)
            state = {"page": page + 1, "scraped_urls": scraped_urls}
            save_state(state)
            
            print(f"Scraped page {page}")

if __name__ == "__main__":
    main()
```

### Multi-File Watching
```python
# scraper_manager.py
from ga_scrap.hot_reload import HotReloadScraper

class ScraperManager:
    def __init__(self):
        self.scraper = HotReloadScraper(
            script_path="main.py",
            watch_patterns=[
                "*.py",           # Python files
                "config/*.yaml",  # Configuration files
                "templates/*.html", # Template files
                "data/*.json"     # Data files
            ],
            exclude_patterns=[
                "*.log",
                "__pycache__/*",
                "*.pyc",
                "output/*"
            ]
        )
    
    def start(self):
        print("🔥 Starting hot reload scraper manager...")
        self.scraper.start()

if __name__ == "__main__":
    manager = ScraperManager()
    manager.start()
```

---

## 🎨 IDE Integration

### VS Code Setup
```json
// .vscode/tasks.json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "GA-Scrap Hot Reload",
            "type": "shell",
            "command": "ga-scrap",
            "args": ["run", "${file}"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "new"
            }
        }
    ]
}
```

### PyCharm Setup
1. Go to **Run > Edit Configurations**
2. Add new **Python** configuration
3. Set **Script path** to `ga-scrap`
4. Set **Parameters** to `run your_script.py`
5. Set **Working directory** to your project folder

---

## 🔍 Debugging with Hot Reload

### Debug Mode
```bash
# Enable debug output
ga-scrap run scraper.py --debug

# Show file watching events
ga-scrap run scraper.py --verbose
```

### Debug Output Example
```
🔥 Hot reload started for: scraper.py
📁 Watching patterns: *.py, *.yaml
🚫 Excluding patterns: *.log, __pycache__/*
🚀 Starting scraper...

📝 File changed: scraper.py
⏳ Waiting 1000ms before restart...
🔄 Restarting scraper...
🚀 Starting scraper...

📝 File changed: config.yaml
⏳ Waiting 1000ms before restart...
🔄 Restarting scraper...
🚀 Starting scraper...
```

### Troubleshooting
```python
# Check if hot reload is working
import os
print(f"Hot reload enabled: {os.getenv('GA_SCRAP_HOT_RELOAD', 'false')}")

# Manual reload trigger
from ga_scrap.hot_reload import trigger_reload
trigger_reload()
```

---

## 🎯 Best Practices

### ✅ Do's
- **Use sandbox mode** during development
- **Keep browser visible** to see changes
- **Save frequently** to trigger reloads
- **Use meaningful print statements** for debugging
- **Structure code in modules** for better organization

### ❌ Don'ts
- **Don't use hot reload in production**
- **Don't watch too many files** (performance impact)
- **Don't forget to handle state** for long-running scrapers
- **Don't rely on hot reload for critical data**

### Example Best Practice Setup
```python
# main.py
import os
from ga_scrap import SyncGAScrap

def main():
    # Development configuration
    is_dev = os.getenv("ENVIRONMENT", "development") == "development"
    
    config = {
        "sandbox_mode": is_dev,
        "headless": not is_dev,
        "debug": is_dev,
        "timeout": 10000 if is_dev else 30000
    }
    
    with SyncGAScrap(**config) as scraper:
        if is_dev:
            print("🔥 Development mode with hot reload")
        
        # Your scraping logic here
        scraper.goto("https://example.com")
        data = scraper.get_text(".content")
        print(f"Scraped: {data[:100]}...")

if __name__ == "__main__":
    main()
```

---

<div align="center">

**⚡ Hot Reload: Supercharge Your Development!**

**Next:** [🔧 Architecture](architecture.md) • [🤝 Contributing](contributing.md)

</div>
