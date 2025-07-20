"""
E-commerce Price Monitoring Template
Monitors product prices and sends alerts when prices drop below target thresholds
"""

import asyncio
import sys
import os
import json
import time
import smtplib
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class PriceMonitor:
    """Template for monitoring product prices and sending alerts"""
    
    def __init__(self, config_file: str = "price_monitor_config.json"):
        """
        Initialize price monitor
        
        Args:
            config_file: Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.price_history = self._load_price_history()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load monitoring configuration"""
        default_config = {
            "products": [],
            "check_interval_minutes": 60,
            "email_settings": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "from_email": "",
                "to_emails": []
            },
            "webhook_settings": {
                "enabled": False,
                "url": "",
                "headers": {}
            }
        }
        
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
                # Merge with defaults
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            print(f"⚠️ Config file {self.config_file} not found, creating default...")
            self._save_config(default_config)
            return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """Save configuration to file"""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=2)
    
    def _load_price_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load price history from file"""
        history_file = "price_history.json"
        try:
            with open(history_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_price_history(self):
        """Save price history to file"""
        history_file = "price_history.json"
        with open(history_file, "w") as f:
            json.dump(self.price_history, f, indent=2)
    
    def add_product(self, name: str, url: str, target_price: float, 
                   price_selector: str = None, title_selector: str = None):
        """
        Add a product to monitor
        
        Args:
            name: Product name/identifier
            url: Product URL
            target_price: Alert when price drops below this
            price_selector: CSS selector for price element
            title_selector: CSS selector for product title
        """
        product = {
            "name": name,
            "url": url,
            "target_price": target_price,
            "price_selector": price_selector or ".price, .product-price, .current-price",
            "title_selector": title_selector or "h1, .product-title, .product-name",
            "added_at": datetime.now().isoformat(),
            "active": True
        }
        
        self.config["products"].append(product)
        self._save_config(self.config)
        print(f"✅ Added product: {name}")
    
    def start_monitoring(self):
        """Start continuous price monitoring"""
        print("🔍 Starting price monitoring...")
        print(f"📊 Monitoring {len(self.config['products'])} products")
        print(f"⏰ Check interval: {self.config['check_interval_minutes']} minutes")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while True:
                self._check_all_prices()
                
                # Wait for next check
                wait_seconds = self.config["check_interval_minutes"] * 60
                print(f"⏳ Waiting {self.config['check_interval_minutes']} minutes until next check...")
                time.sleep(wait_seconds)
                
        except KeyboardInterrupt:
            print("\n👋 Stopping price monitoring...")
    
    def _check_all_prices(self):
        """Check prices for all monitored products"""
        print(f"\n🔍 Checking prices at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        alerts = []
        
        with SyncGAScrap(headless=True, sandbox_mode=True) as scraper:
            for product in self.config["products"]:
                if not product.get("active", True):
                    continue
                    
                try:
                    price_data = self._check_single_price(scraper, product)
                    if price_data:
                        # Store price history
                        product_id = product["name"]
                        if product_id not in self.price_history:
                            self.price_history[product_id] = []
                        
                        self.price_history[product_id].append(price_data)
                        
                        # Check for price alert
                        if price_data["price"] <= product["target_price"]:
                            alerts.append({
                                "product": product,
                                "price_data": price_data
                            })
                            
                except Exception as e:
                    print(f"❌ Error checking {product['name']}: {e}")
        
        # Save updated price history
        self._save_price_history()
        
        # Send alerts if any
        if alerts:
            self._send_alerts(alerts)
        
        print(f"✅ Price check complete. {len(alerts)} alerts generated.")
    
    def _check_single_price(self, scraper: SyncGAScrap, product: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Check price for a single product"""
        print(f"🔍 Checking: {product['name']}")
        
        # Navigate to product page
        scraper.goto(product["url"])
        
        # Handle popups
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close",
            ".age-verification button"
        ]
        for selector in popup_selectors:
            scraper.click(selector)
        
        # Wait for page to load
        scraper.wait_for_load_state("networkidle")
        
        # Extract price
        price_text = scraper.get_text(product["price_selector"])
        if not price_text:
            print(f"⚠️ Could not find price for {product['name']}")
            return None
        
        # Parse price
        import re
        price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
        if not price_match:
            print(f"⚠️ Could not parse price: {price_text}")
            return None
        
        try:
            current_price = float(price_match.group().replace(',', ''))
        except ValueError:
            print(f"⚠️ Invalid price format: {price_text}")
            return None
        
        # Extract product title
        title = scraper.get_text(product["title_selector"]) or product["name"]
        
        price_data = {
            "timestamp": datetime.now().isoformat(),
            "price": current_price,
            "price_text": price_text,
            "title": title,
            "url": product["url"]
        }
        
        # Compare with target
        if current_price <= product["target_price"]:
            print(f"🎯 ALERT: {product['name']} is ${current_price} (target: ${product['target_price']})")
        else:
            print(f"💰 {product['name']}: ${current_price} (target: ${product['target_price']})")
        
        return price_data
    
    def _send_alerts(self, alerts: List[Dict[str, Any]]):
        """Send price alerts via configured methods"""
        print(f"📢 Sending {len(alerts)} price alerts...")
        
        # Send email alerts
        if self.config["email_settings"]["enabled"]:
            self._send_email_alerts(alerts)
        
        # Send webhook alerts
        if self.config["webhook_settings"]["enabled"]:
            self._send_webhook_alerts(alerts)
    
    def _send_email_alerts(self, alerts: List[Dict[str, Any]]):
        """Send email alerts"""
        try:
            email_config = self.config["email_settings"]
            
            # Create email content
            subject = f"Price Alert: {len(alerts)} product(s) below target price"
            
            body = "🎯 Price Alert!\n\n"
            body += "The following products are now below your target price:\n\n"
            
            for alert in alerts:
                product = alert["product"]
                price_data = alert["price_data"]
                body += f"📦 {product['name']}\n"
                body += f"💰 Current Price: ${price_data['price']}\n"
                body += f"🎯 Target Price: ${product['target_price']}\n"
                body += f"🔗 URL: {product['url']}\n\n"
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = email_config["from_email"]
            msg['To'] = ", ".join(email_config["to_emails"])
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"])
            server.starttls()
            server.login(email_config["username"], email_config["password"])
            
            for to_email in email_config["to_emails"]:
                server.send_message(msg, to_addrs=[to_email])
            
            server.quit()
            print("📧 Email alerts sent successfully")
            
        except Exception as e:
            print(f"❌ Failed to send email alerts: {e}")
    
    def _send_webhook_alerts(self, alerts: List[Dict[str, Any]]):
        """Send webhook alerts"""
        try:
            import requests
            
            webhook_config = self.config["webhook_settings"]
            
            payload = {
                "timestamp": datetime.now().isoformat(),
                "alert_count": len(alerts),
                "alerts": []
            }
            
            for alert in alerts:
                payload["alerts"].append({
                    "product_name": alert["product"]["name"],
                    "current_price": alert["price_data"]["price"],
                    "target_price": alert["product"]["target_price"],
                    "url": alert["product"]["url"],
                    "savings": alert["product"]["target_price"] - alert["price_data"]["price"]
                })
            
            response = requests.post(
                webhook_config["url"],
                json=payload,
                headers=webhook_config.get("headers", {})
            )
            
            if response.status_code == 200:
                print("🔗 Webhook alerts sent successfully")
            else:
                print(f"⚠️ Webhook returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ Failed to send webhook alerts: {e}")
    
    def get_price_history(self, product_name: str) -> List[Dict[str, Any]]:
        """Get price history for a product"""
        return self.price_history.get(product_name, [])
    
    def generate_report(self) -> str:
        """Generate a price monitoring report"""
        report = "📊 Price Monitoring Report\n"
        report += "=" * 50 + "\n\n"
        
        for product in self.config["products"]:
            if not product.get("active", True):
                continue
                
            product_name = product["name"]
            history = self.get_price_history(product_name)
            
            report += f"📦 {product_name}\n"
            report += f"🎯 Target Price: ${product['target_price']}\n"
            
            if history:
                latest = history[-1]
                report += f"💰 Current Price: ${latest['price']}\n"
                
                if len(history) > 1:
                    previous = history[-2]
                    change = latest['price'] - previous['price']
                    if change > 0:
                        report += f"📈 Price Change: +${change:.2f}\n"
                    elif change < 0:
                        report += f"📉 Price Change: ${change:.2f}\n"
                    else:
                        report += f"➡️ Price Change: No change\n"
                
                # Price trend
                if len(history) >= 5:
                    recent_prices = [h['price'] for h in history[-5:]]
                    if all(recent_prices[i] <= recent_prices[i+1] for i in range(len(recent_prices)-1)):
                        report += f"📈 Trend: Rising\n"
                    elif all(recent_prices[i] >= recent_prices[i+1] for i in range(len(recent_prices)-1)):
                        report += f"📉 Trend: Falling\n"
                    else:
                        report += f"📊 Trend: Fluctuating\n"
            else:
                report += f"❓ No price data available\n"
            
            report += "\n"
        
        return report

# Example usage and setup
def setup_example_monitor():
    """Set up an example price monitor"""
    monitor = PriceMonitor()
    
    # Add some example products (replace with real URLs)
    monitor.add_product(
        name="Example Laptop",
        url="https://example-store.com/laptop-123",
        target_price=999.99,
        price_selector=".price-current",
        title_selector="h1.product-title"
    )
    
    monitor.add_product(
        name="Example Phone",
        url="https://example-store.com/phone-456", 
        target_price=699.99
    )
    
    return monitor

def main():
    """Example usage of the price monitor"""
    print("🔍 GA-Scrap Price Monitor Template")
    print("=" * 40)
    
    # Setup monitor
    monitor = setup_example_monitor()
    
    # Show current configuration
    print(f"📊 Monitoring {len(monitor.config['products'])} products")
    
    # Generate report
    report = monitor.generate_report()
    print(report)
    
    # Start monitoring (uncomment to run continuously)
    # monitor.start_monitoring()

if __name__ == "__main__":
    main()
