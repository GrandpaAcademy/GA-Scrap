# 🎯 Examples & Use Cases

<div align="center">

**Real-World Scraping Examples**  
*Learn by doing with practical examples*

</div>

---

## 🚀 Quick Examples

### 📰 News Scraper
```python
from ga_scrap import SyncGAScrap

with SyncGAScrap() as scraper:
    scraper.goto("https://news.ycombinator.com")
    
    # Extract headlines and scores
    titles = scraper.get_all_text(".titleline > a")
    scores = scraper.get_all_text(".score")
    
    # Display results
    for title, score in zip(titles, scores):
        print(f"{score}: {title}")
```

### 🛒 E-commerce Product Scraper
```python
with SyncGAScrap(sandbox_mode=True) as scraper:
    scraper.goto("https://example-shop.com/products")
    
    # Handle potential popups gracefully
    scraper.click(".cookie-accept")  # Won't crash if not found
    scraper.click(".popup-close")    # Won't crash if not found
    
    # Extract product data
    products = scraper.get_all_text(".product-name")
    prices = scraper.get_all_text(".product-price")
    ratings = scraper.get_all_text(".product-rating")
    
    # Save data
    for product, price, rating in zip(products, prices, ratings):
        print(f"{product}: {price} ({rating})")
```

### 📱 Mobile-First Scraper
```python
with SyncGAScrap(device="iPhone 12", sandbox_mode=True) as scraper:
    scraper.goto("https://mobile-site.com")
    
    # Mobile-specific interactions
    scraper.simulate_touch(100, 200)
    scraper.swipe(start_x=100, start_y=300, end_x=100, end_y=100)
    
    # Extract mobile content
    content = scraper.get_text(".mobile-content")
    scraper.screenshot("mobile-view.png")
```

---

## 🏢 Business Use Cases

### 📊 Market Research
```python
def scrape_competitor_prices():
    competitors = [
        "https://competitor1.com/products",
        "https://competitor2.com/products", 
        "https://competitor3.com/products"
    ]
    
    all_prices = {}
    
    with SyncGAScrap(sandbox_mode=True) as scraper:
        for url in competitors:
            scraper.goto(url)
            
            # Handle different site structures gracefully
            scraper.click(".cookie-accept")
            scraper.click(".age-verification-yes")
            
            # Extract pricing data
            products = scraper.get_all_text(".product-name")
            prices = scraper.get_all_text(".product-price")
            
            site_name = url.split("//")[1].split(".")[0]
            all_prices[site_name] = list(zip(products, prices))
            
            print(f"Scraped {len(products)} products from {site_name}")
    
    return all_prices

# Run market research
market_data = scrape_competitor_prices()
```

### 📈 Social Media Monitoring
```python
def monitor_brand_mentions():
    with SyncGAScrap(sandbox_mode=True) as scraper:
        # Twitter-like platform
        scraper.goto("https://social-platform.com/search?q=YourBrand")
        
        # Handle login if needed
        if scraper.get_text(".login-prompt"):
            scraper.input("#username", "your_username")
            scraper.input("#password", "your_password")
            scraper.click(".login-button")
            scraper.wait_for_selector(".feed")
        
        # Scroll to load more content
        for _ in range(5):
            scraper.scroll_to_bottom()
            scraper.wait(2000)  # Wait for content to load
        
        # Extract mentions
        posts = scraper.get_all_text(".post-content")
        authors = scraper.get_all_text(".post-author")
        timestamps = scraper.get_all_text(".post-time")
        
        mentions = []
        for post, author, time in zip(posts, authors, timestamps):
            if "YourBrand" in post:
                mentions.append({
                    "author": author,
                    "content": post,
                    "timestamp": time
                })
        
        return mentions

# Monitor mentions
brand_mentions = monitor_brand_mentions()
print(f"Found {len(brand_mentions)} brand mentions")
```

### 🏠 Real Estate Data Collection
```python
def scrape_property_listings():
    with SyncGAScrap(sandbox_mode=True) as scraper:
        base_url = "https://real-estate-site.com"
        scraper.goto(f"{base_url}/search?location=NewYork")
        
        all_properties = []
        page = 1
        
        while page <= 10:  # Scrape first 10 pages
            print(f"Scraping page {page}...")
            
            # Wait for listings to load
            scraper.wait_for_selector(".property-card")
            
            # Extract property data
            titles = scraper.get_all_text(".property-title")
            prices = scraper.get_all_text(".property-price")
            addresses = scraper.get_all_text(".property-address")
            details = scraper.get_all_text(".property-details")
            
            # Combine data
            for title, price, address, detail in zip(titles, prices, addresses, details):
                all_properties.append({
                    "title": title,
                    "price": price,
                    "address": address,
                    "details": detail,
                    "page": page
                })
            
            # Go to next page
            next_button = scraper.click(".next-page")
            if not next_button:  # No more pages
                break
                
            page += 1
            scraper.wait_for_selector(".property-card")
        
        return all_properties

# Collect property data
properties = scrape_property_listings()
print(f"Collected {len(properties)} property listings")
```

---

## 🧪 Advanced Techniques

### 🔄 Multi-Tab Scraping
```python
def scrape_product_details():
    with SyncGAScrap() as scraper:
        # Main catalog page
        scraper.goto("https://shop.com/catalog")
        product_links = scraper.get_all_attributes("a.product-link", "href")
        
        detailed_products = []
        
        # Open each product in new tab
        for i, link in enumerate(product_links[:10]):  # First 10 products
            print(f"Scraping product {i+1}/10...")
            
            # Create new tab
            product_page = scraper.new_page()
            scraper.goto(link, page=product_page)
            
            # Extract detailed information
            title = scraper.get_text("h1", page=product_page)
            price = scraper.get_text(".price", page=product_page)
            description = scraper.get_text(".description", page=product_page)
            images = scraper.get_all_attributes("img.product-image", "src", page=product_page)
            
            detailed_products.append({
                "title": title,
                "price": price,
                "description": description,
                "images": images,
                "url": link
            })
            
            # Close tab to save memory
            scraper.close_page(product_page)
        
        return detailed_products

# Scrape detailed product information
products = scrape_product_details()
```

### 🎯 Form Automation
```python
def automate_job_application():
    with SyncGAScrap(sandbox_mode=True) as scraper:
        scraper.goto("https://company.com/careers/apply")
        
        # Fill personal information
        scraper.input("#first-name", "John")
        scraper.input("#last-name", "Doe")
        scraper.input("#email", "john.doe@email.com")
        scraper.input("#phone", "+1-555-0123")
        
        # Upload resume
        scraper.upload_files("#resume", ["resume.pdf"])
        
        # Fill experience section
        scraper.select_option("#experience-level", "3-5 years")
        scraper.check("#remote-work")
        
        # Fill text areas
        scraper.input("#cover-letter", """
        Dear Hiring Manager,
        
        I am excited to apply for this position...
        """)
        
        # Handle dynamic form sections
        if scraper.get_text(".additional-questions"):
            scraper.input("#question-1", "My answer to question 1")
            scraper.input("#question-2", "My answer to question 2")
        
        # Submit application
        scraper.click("#submit-application")
        
        # Wait for confirmation
        scraper.wait_for_text("Application submitted successfully")
        confirmation = scraper.get_text(".confirmation-message")
        
        return confirmation

# Automate application process
result = automate_job_application()
print(f"Application result: {result}")
```

### 📊 Data Monitoring & Alerts
```python
import time
import smtplib
from email.mime.text import MIMEText

def monitor_stock_prices():
    target_stocks = {
        "AAPL": 150.00,  # Alert if below $150
        "GOOGL": 2500.00,  # Alert if below $2500
        "TSLA": 800.00   # Alert if below $800
    }
    
    while True:
        with SyncGAScrap(headless=True, sandbox_mode=True) as scraper:
            alerts = []
            
            for symbol, target_price in target_stocks.items():
                scraper.goto(f"https://finance.yahoo.com/quote/{symbol}")
                
                # Extract current price
                price_text = scraper.get_text("[data-symbol='{symbol}'] [data-field='regularMarketPrice']")
                current_price = float(price_text.replace("$", "").replace(",", ""))
                
                print(f"{symbol}: ${current_price}")
                
                # Check if alert needed
                if current_price < target_price:
                    alerts.append(f"{symbol} is below target: ${current_price} < ${target_price}")
            
            # Send alerts if any
            if alerts:
                send_email_alert(alerts)
            
            # Wait 5 minutes before next check
            time.sleep(300)

def send_email_alert(alerts):
    msg = MIMEText("\n".join(alerts))
    msg['Subject'] = "Stock Price Alert"
    msg['From'] = "alerts@yourapp.com"
    msg['To'] = "you@email.com"
    
    # Send email (configure SMTP settings)
    # smtp_server.send_message(msg)
    print("Alert sent:", alerts)

# Start monitoring
# monitor_stock_prices()  # Uncomment to run
```

---

## 🎨 Creative Applications

### 📸 Website Screenshot Gallery
```python
def create_website_gallery():
    websites = [
        "https://github.com",
        "https://stackoverflow.com", 
        "https://reddit.com",
        "https://news.ycombinator.com",
        "https://dev.to"
    ]
    
    with SyncGAScrap(viewport={"width": 1920, "height": 1080}) as scraper:
        for i, url in enumerate(websites):
            print(f"Capturing {url}...")
            
            scraper.goto(url)
            scraper.wait_for_load_state("networkidle")
            
            # Take full page screenshot
            filename = f"gallery_{i+1}_{url.split('//')[1].split('.')[0]}.png"
            scraper.screenshot_full_page(filename)
            
            print(f"Saved: {filename}")

# Create gallery
create_website_gallery()
```

### 🎵 Music Chart Tracker
```python
def track_music_charts():
    with SyncGAScrap(sandbox_mode=True) as scraper:
        scraper.goto("https://music-charts.com/top-100")
        
        # Extract chart data
        positions = scraper.get_all_text(".chart-position")
        songs = scraper.get_all_text(".song-title")
        artists = scraper.get_all_text(".artist-name")
        
        # Create chart data
        chart = []
        for pos, song, artist in zip(positions, songs, artists):
            chart.append({
                "position": int(pos),
                "song": song,
                "artist": artist,
                "date": "2024-01-01"  # Add current date
            })
        
        # Save to file
        import json
        with open("music_chart.json", "w") as f:
            json.dump(chart, f, indent=2)
        
        return chart

# Track charts
chart_data = track_music_charts()
print(f"Tracked {len(chart_data)} songs")
```

---

## 🛠️ Utility Functions

### 📁 Data Export Helper
```python
import json
import csv
from datetime import datetime

def save_scraped_data(data, filename, format="json"):
    """Save scraped data in various formats"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        filename = f"{filename}_{timestamp}.json"
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
    
    elif format == "csv":
        filename = f"{filename}_{timestamp}.csv"
        if data and isinstance(data[0], dict):
            with open(filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
    
    print(f"Data saved to: {filename}")
    return filename

# Usage
scraped_data = [{"title": "Example", "price": "$10"}]
save_scraped_data(scraped_data, "products", "csv")
```

### 🔄 Retry Mechanism
```python
def scrape_with_retry(url, max_retries=3):
    """Scrape with automatic retry on failure"""
    for attempt in range(max_retries):
        try:
            with SyncGAScrap(sandbox_mode=True) as scraper:
                scraper.goto(url)
                data = scraper.get_text(".content")
                return data
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff

# Usage
data = scrape_with_retry("https://example.com")
```

---

<div align="center">

**🎯 Ready to Build Your Own Scrapers?**

**Next:** [🔧 Installation Guide](installation.md) • [⚡ Hot Reload](hot-reload.md)

</div>
