"""
Database Export Template
Demonstrates how to scrape data and export it to various databases
"""

import asyncio
import sys
import os
import json
import sqlite3
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
import uuid

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class DatabaseExporter:
    """Template for scraping data and exporting to databases"""
    
    def __init__(self, db_type: str = "sqlite", connection_params: Dict[str, Any] = None):
        """
        Initialize database exporter
        
        Args:
            db_type: Type of database ('sqlite', 'mysql', 'postgresql', 'mongodb')
            connection_params: Database connection parameters
        """
        self.db_type = db_type
        self.connection_params = connection_params or {}
        self.scraped_data = []
        
        # Initialize database connection
        self.connection = self._init_database()
    
    def _init_database(self):
        """Initialize database connection based on type"""
        if self.db_type == "sqlite":
            return self._init_sqlite()
        elif self.db_type == "mysql":
            return self._init_mysql()
        elif self.db_type == "postgresql":
            return self._init_postgresql()
        elif self.db_type == "mongodb":
            return self._init_mongodb()
        else:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def _init_sqlite(self):
        """Initialize SQLite database"""
        db_path = self.connection_params.get("database", "scraped_data.db")
        conn = sqlite3.connect(db_path)
        
        # Create tables if they don't exist
        self._create_sqlite_tables(conn)
        
        print(f"✅ Connected to SQLite database: {db_path}")
        return conn
    
    def _create_sqlite_tables(self, conn):
        """Create SQLite tables for scraped data"""
        cursor = conn.cursor()
        
        # Main scraped data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_data (
                id TEXT PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                scraped_at TIMESTAMP,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table for structured data fields
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_fields (
                id TEXT PRIMARY KEY,
                scraped_data_id TEXT,
                field_name TEXT,
                field_value TEXT,
                field_type TEXT,
                FOREIGN KEY (scraped_data_id) REFERENCES scraped_data (id)
            )
        """)
        
        conn.commit()
    
    def _init_mysql(self):
        """Initialize MySQL database"""
        try:
            import mysql.connector
            
            conn = mysql.connector.connect(
                host=self.connection_params.get("host", "localhost"),
                user=self.connection_params.get("user", "root"),
                password=self.connection_params.get("password", ""),
                database=self.connection_params.get("database", "scraped_data")
            )
            
            self._create_mysql_tables(conn)
            print("✅ Connected to MySQL database")
            return conn
            
        except ImportError:
            raise ImportError("mysql-connector-python is required for MySQL support")
    
    def _create_mysql_tables(self, conn):
        """Create MySQL tables"""
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_data (
                id VARCHAR(36) PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                content LONGTEXT,
                scraped_at TIMESTAMP,
                metadata JSON,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_fields (
                id VARCHAR(36) PRIMARY KEY,
                scraped_data_id VARCHAR(36),
                field_name VARCHAR(255),
                field_value TEXT,
                field_type VARCHAR(50),
                FOREIGN KEY (scraped_data_id) REFERENCES scraped_data (id)
            )
        """)
        
        conn.commit()
    
    def _init_postgresql(self):
        """Initialize PostgreSQL database"""
        try:
            import psycopg2
            
            conn = psycopg2.connect(
                host=self.connection_params.get("host", "localhost"),
                database=self.connection_params.get("database", "scraped_data"),
                user=self.connection_params.get("user", "postgres"),
                password=self.connection_params.get("password", "")
            )
            
            self._create_postgresql_tables(conn)
            print("✅ Connected to PostgreSQL database")
            return conn
            
        except ImportError:
            raise ImportError("psycopg2 is required for PostgreSQL support")
    
    def _create_postgresql_tables(self, conn):
        """Create PostgreSQL tables"""
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraped_data (
                id UUID PRIMARY KEY,
                url TEXT NOT NULL,
                title TEXT,
                content TEXT,
                scraped_at TIMESTAMP,
                metadata JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_fields (
                id UUID PRIMARY KEY,
                scraped_data_id UUID,
                field_name VARCHAR(255),
                field_value TEXT,
                field_type VARCHAR(50),
                FOREIGN KEY (scraped_data_id) REFERENCES scraped_data (id)
            )
        """)
        
        conn.commit()
    
    def _init_mongodb(self):
        """Initialize MongoDB database"""
        try:
            from pymongo import MongoClient
            
            client = MongoClient(
                host=self.connection_params.get("host", "localhost"),
                port=self.connection_params.get("port", 27017)
            )
            
            db_name = self.connection_params.get("database", "scraped_data")
            db = client[db_name]
            
            print("✅ Connected to MongoDB database")
            return db
            
        except ImportError:
            raise ImportError("pymongo is required for MongoDB support")
    
    def scrape_and_export(self, urls: List[str], selectors: Dict[str, str], 
                         table_name: str = "scraped_data") -> Dict[str, Any]:
        """
        Scrape data from URLs and export to database
        
        Args:
            urls: List of URLs to scrape
            selectors: Dictionary of field names and CSS selectors
            table_name: Name of the table/collection to store data
            
        Returns:
            Summary of scraping and export results
        """
        results = {
            "total_urls": len(urls),
            "successful_scrapes": 0,
            "failed_scrapes": 0,
            "database_inserts": 0,
            "database_failures": 0,
            "start_time": datetime.now().isoformat()
        }
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("🗄️ Starting database export scraper...", "info")
            
            for i, url in enumerate(urls):
                try:
                    scraper.log(f"📄 Scraping {i+1}/{len(urls)}: {url}", "info")
                    
                    # Navigate to URL
                    scraper.goto(url)
                    
                    # Handle popups
                    self._handle_popups(scraper)
                    
                    # Extract data
                    scraped_item = self._extract_data(scraper, url, selectors)
                    
                    if scraped_item:
                        # Export to database
                        if self._export_to_database(scraped_item, table_name):
                            results["successful_scrapes"] += 1
                            results["database_inserts"] += 1
                        else:
                            results["successful_scrapes"] += 1
                            results["database_failures"] += 1
                    else:
                        results["failed_scrapes"] += 1
                        
                except Exception as e:
                    scraper.log(f"❌ Error processing {url}: {e}", "error")
                    results["failed_scrapes"] += 1
        
        results["end_time"] = datetime.now().isoformat()
        scraper.log(f"✅ Export complete! {results['database_inserts']} items saved to database", "success")
        
        return results
    
    def _handle_popups(self, scraper: SyncGAScrap):
        """Handle common website popups"""
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close", ".overlay-close"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
    
    def _extract_data(self, scraper: SyncGAScrap, url: str, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract data using provided selectors"""
        data = {
            "id": str(uuid.uuid4()),
            "url": url,
            "scraped_at": datetime.now().isoformat(),
            "title": scraper.get_text("title"),
            "metadata": {
                "user_agent": scraper.page.evaluate("navigator.userAgent"),
                "page_load_time": scraper.page.evaluate("performance.timing.loadEventEnd - performance.timing.navigationStart")
            }
        }
        
        # Extract data for each selector
        extracted_fields = {}
        for field_name, selector in selectors.items():
            try:
                if selector.endswith("[]"):  # Multiple elements
                    selector = selector[:-2]
                    values = scraper.get_all_text(selector)
                    extracted_fields[field_name] = values
                elif selector.startswith("@"):  # Attribute
                    attr_selector, attr_name = selector[1:].split("@")
                    value = scraper.get_attribute(attr_selector, attr_name)
                    extracted_fields[field_name] = value
                else:  # Single element text
                    value = scraper.get_text(selector)
                    extracted_fields[field_name] = value
                    
            except Exception as e:
                scraper.log(f"⚠️ Could not extract {field_name}: {e}", "warning")
                extracted_fields[field_name] = None
        
        data["extracted_fields"] = extracted_fields
        
        # Set main content field if available
        main_content_fields = ["content", "description", "text", "body"]
        for field in main_content_fields:
            if field in extracted_fields and extracted_fields[field]:
                data["content"] = extracted_fields[field]
                break
        
        return data if extracted_fields else None
    
    def _export_to_database(self, data: Dict[str, Any], table_name: str) -> bool:
        """Export data to database"""
        try:
            if self.db_type == "sqlite":
                return self._export_to_sqlite(data)
            elif self.db_type == "mysql":
                return self._export_to_mysql(data)
            elif self.db_type == "postgresql":
                return self._export_to_postgresql(data)
            elif self.db_type == "mongodb":
                return self._export_to_mongodb(data, table_name)
            
        except Exception as e:
            print(f"❌ Database export error: {e}")
            return False
    
    def _export_to_sqlite(self, data: Dict[str, Any]) -> bool:
        """Export data to SQLite"""
        cursor = self.connection.cursor()
        
        # Insert main record
        cursor.execute("""
            INSERT INTO scraped_data (id, url, title, content, scraped_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data["id"],
            data["url"],
            data.get("title"),
            data.get("content"),
            data["scraped_at"],
            json.dumps(data.get("metadata", {}))
        ))
        
        # Insert extracted fields
        for field_name, field_value in data.get("extracted_fields", {}).items():
            if field_value is not None:
                cursor.execute("""
                    INSERT INTO data_fields (id, scraped_data_id, field_name, field_value, field_type)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    data["id"],
                    field_name,
                    str(field_value) if not isinstance(field_value, list) else json.dumps(field_value),
                    type(field_value).__name__
                ))
        
        self.connection.commit()
        return True
    
    def _export_to_mysql(self, data: Dict[str, Any]) -> bool:
        """Export data to MySQL"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO scraped_data (id, url, title, content, scraped_at, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["id"],
            data["url"],
            data.get("title"),
            data.get("content"),
            data["scraped_at"],
            json.dumps(data.get("metadata", {}))
        ))
        
        # Insert extracted fields
        for field_name, field_value in data.get("extracted_fields", {}).items():
            if field_value is not None:
                cursor.execute("""
                    INSERT INTO data_fields (id, scraped_data_id, field_name, field_value, field_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    data["id"],
                    field_name,
                    str(field_value) if not isinstance(field_value, list) else json.dumps(field_value),
                    type(field_value).__name__
                ))
        
        self.connection.commit()
        return True
    
    def _export_to_postgresql(self, data: Dict[str, Any]) -> bool:
        """Export data to PostgreSQL"""
        cursor = self.connection.cursor()
        
        cursor.execute("""
            INSERT INTO scraped_data (id, url, title, content, scraped_at, metadata)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["id"],
            data["url"],
            data.get("title"),
            data.get("content"),
            data["scraped_at"],
            json.dumps(data.get("metadata", {}))
        ))
        
        # Insert extracted fields
        for field_name, field_value in data.get("extracted_fields", {}).items():
            if field_value is not None:
                cursor.execute("""
                    INSERT INTO data_fields (id, scraped_data_id, field_name, field_value, field_type)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    str(uuid.uuid4()),
                    data["id"],
                    field_name,
                    str(field_value) if not isinstance(field_value, list) else json.dumps(field_value),
                    type(field_value).__name__
                ))
        
        self.connection.commit()
        return True
    
    def _export_to_mongodb(self, data: Dict[str, Any], collection_name: str) -> bool:
        """Export data to MongoDB"""
        collection = self.connection[collection_name]
        
        # Flatten the structure for MongoDB
        document = {
            "_id": data["id"],
            "url": data["url"],
            "title": data.get("title"),
            "content": data.get("content"),
            "scraped_at": data["scraped_at"],
            "metadata": data.get("metadata", {}),
            "fields": data.get("extracted_fields", {})
        }
        
        collection.insert_one(document)
        return True
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export scraped data to CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"scraped_data_{timestamp}.csv"
        
        # Get data from database
        data = self._get_all_data()
        
        if not data:
            print("No data to export")
            return filename
        
        # Write to CSV
        with open(filename, "w", newline="", encoding="utf-8") as f:
            if data:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
        
        print(f"💾 Exported {len(data)} records to {filename}")
        return filename
    
    def _get_all_data(self) -> List[Dict[str, Any]]:
        """Get all data from database"""
        if self.db_type in ["sqlite", "mysql", "postgresql"]:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM scraped_data")
            
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            
            return [dict(zip(columns, row)) for row in rows]
        
        elif self.db_type == "mongodb":
            collection = self.connection["scraped_data"]
            return list(collection.find({}))
        
        return []
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            if self.db_type in ["sqlite", "mysql", "postgresql"]:
                self.connection.close()
            elif self.db_type == "mongodb":
                self.connection.client.close()
            print("🔌 Database connection closed")

# Example usage functions
def example_sqlite_export():
    """Example: Scrape news and export to SQLite"""
    print("📰 News Scraper with SQLite Export")
    print("=" * 50)
    
    # Initialize SQLite exporter
    exporter = DatabaseExporter(db_type="sqlite", connection_params={"database": "news_data.db"})
    
    # URLs to scrape
    urls = [
        "https://news.ycombinator.com",
        "https://techcrunch.com"
    ]
    
    # Define selectors
    selectors = {
        "headlines": ".titleline > a[]",
        "main_headline": "h1",
        "description": "meta[name='description']@content"
    }
    
    # Scrape and export
    results = exporter.scrape_and_export(urls, selectors)
    
    # Export to CSV as well
    csv_file = exporter.export_to_csv()
    
    # Close connection
    exporter.close_connection()
    
    print(f"\n📊 Results:")
    print(f"Database inserts: {results['database_inserts']}")
    print(f"CSV export: {csv_file}")

def example_mongodb_export():
    """Example: Scrape products and export to MongoDB"""
    print("🛒 Product Scraper with MongoDB Export")
    print("=" * 50)
    
    # Initialize MongoDB exporter
    exporter = DatabaseExporter(
        db_type="mongodb",
        connection_params={
            "host": "localhost",
            "port": 27017,
            "database": "ecommerce_data"
        }
    )
    
    # Product URLs
    urls = [
        "https://example-store.com/product/123",
        "https://example-store.com/product/456"
    ]
    
    # Product selectors
    selectors = {
        "name": "h1",
        "price": ".price",
        "description": ".product-description",
        "rating": ".rating",
        "availability": ".stock-status"
    }
    
    # Scrape and export
    results = exporter.scrape_and_export(urls, selectors, table_name="products")
    
    exporter.close_connection()
    
    print(f"\n📊 Results:")
    print(f"Products saved: {results['database_inserts']}")

def main():
    """Main function to demonstrate database export"""
    print("🗄️ GA-Scrap Database Export Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. SQLite export (news scraper)")
    print("2. MongoDB export (product scraper)")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        example_sqlite_export()
    elif choice == "2":
        example_mongodb_export()
    else:
        print("Invalid choice. Running SQLite example...")
        example_sqlite_export()

if __name__ == "__main__":
    main()
