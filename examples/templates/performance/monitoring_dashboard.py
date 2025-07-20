"""
Monitoring Dashboard Template
Real-time monitoring and alerting system for scraping operations
"""

import asyncio
import sys
import os
import json
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

@dataclass
class ScrapingMetric:
    """Data class for scraping metrics"""
    timestamp: str
    url: str
    success: bool
    duration: float
    error_message: Optional[str] = None
    response_size: int = 0
    status_code: Optional[int] = None

class ScrapingMonitor:
    """Real-time monitoring system for scraping operations"""
    
    def __init__(self, db_path: str = "monitoring.db"):
        """
        Initialize scraping monitor
        
        Args:
            db_path: Path to SQLite database for storing metrics
        """
        self.db_path = db_path
        self.metrics = []
        self.alerts = []
        self.is_monitoring = False
        
        # Initialize database
        self._init_database()
        
        # Monitoring thresholds
        self.thresholds = {
            "error_rate_threshold": 0.1,  # 10% error rate
            "response_time_threshold": 10.0,  # 10 seconds
            "consecutive_failures_threshold": 5,
            "monitoring_window_minutes": 15
        }
    
    def _init_database(self):
        """Initialize SQLite database for metrics storage"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create metrics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                url TEXT NOT NULL,
                success BOOLEAN NOT NULL,
                duration REAL NOT NULL,
                error_message TEXT,
                response_size INTEGER DEFAULT 0,
                status_code INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                message TEXT NOT NULL,
                severity TEXT NOT NULL,
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def record_metric(self, metric: ScrapingMetric):
        """Record a scraping metric"""
        self.metrics.append(metric)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO metrics (timestamp, url, success, duration, error_message, response_size, status_code)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            metric.timestamp,
            metric.url,
            metric.success,
            metric.duration,
            metric.error_message,
            metric.response_size,
            metric.status_code
        ))
        
        conn.commit()
        conn.close()
        
        # Check for alerts
        self._check_alerts(metric)
    
    def _check_alerts(self, metric: ScrapingMetric):
        """Check if any alerts should be triggered"""
        current_time = datetime.now()
        window_start = current_time - timedelta(minutes=self.thresholds["monitoring_window_minutes"])
        
        # Get recent metrics
        recent_metrics = self._get_metrics_since(window_start)
        
        # Check error rate
        if len(recent_metrics) >= 10:  # Need minimum sample size
            error_rate = sum(1 for m in recent_metrics if not m.success) / len(recent_metrics)
            if error_rate > self.thresholds["error_rate_threshold"]:
                self._create_alert(
                    "high_error_rate",
                    f"Error rate is {error_rate:.1%} (threshold: {self.thresholds['error_rate_threshold']:.1%})",
                    "warning"
                )
        
        # Check response time
        if metric.duration > self.thresholds["response_time_threshold"]:
            self._create_alert(
                "slow_response",
                f"Slow response time: {metric.duration:.2f}s for {metric.url}",
                "warning"
            )
        
        # Check consecutive failures
        consecutive_failures = 0
        for m in reversed(recent_metrics[-10:]):  # Check last 10 requests
            if not m.success:
                consecutive_failures += 1
            else:
                break
        
        if consecutive_failures >= self.thresholds["consecutive_failures_threshold"]:
            self._create_alert(
                "consecutive_failures",
                f"{consecutive_failures} consecutive failures detected",
                "critical"
            )
    
    def _get_metrics_since(self, since: datetime) -> List[ScrapingMetric]:
        """Get metrics since a specific time"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, url, success, duration, error_message, response_size, status_code
            FROM metrics
            WHERE datetime(timestamp) >= datetime(?)
            ORDER BY timestamp
        """, (since.isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            ScrapingMetric(
                timestamp=row[0],
                url=row[1],
                success=bool(row[2]),
                duration=row[3],
                error_message=row[4],
                response_size=row[5] or 0,
                status_code=row[6]
            )
            for row in rows
        ]
    
    def _create_alert(self, alert_type: str, message: str, severity: str):
        """Create a new alert"""
        alert = {
            "timestamp": datetime.now().isoformat(),
            "alert_type": alert_type,
            "message": message,
            "severity": severity
        }
        
        self.alerts.append(alert)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO alerts (timestamp, alert_type, message, severity)
            VALUES (?, ?, ?, ?)
        """, (alert["timestamp"], alert_type, message, severity))
        
        conn.commit()
        conn.close()
        
        print(f"🚨 ALERT [{severity.upper()}]: {message}")
    
    def start_monitoring(self, urls: List[str], selectors: Dict[str, str],
                        check_interval: int = 300):  # 5 minutes
        """
        Start continuous monitoring of URLs
        
        Args:
            urls: List of URLs to monitor
            selectors: Selectors for data extraction
            check_interval: Interval between checks in seconds
        """
        self.is_monitoring = True
        
        print(f"🔍 Starting monitoring of {len(urls)} URLs")
        print(f"⏰ Check interval: {check_interval} seconds")
        print("Press Ctrl+C to stop monitoring")
        
        try:
            while self.is_monitoring:
                self._monitor_urls(urls, selectors)
                
                if self.is_monitoring:  # Check again in case it was stopped
                    print(f"⏳ Waiting {check_interval} seconds until next check...")
                    time.sleep(check_interval)
                    
        except KeyboardInterrupt:
            print("\n👋 Stopping monitoring...")
            self.is_monitoring = False
    
    def _monitor_urls(self, urls: List[str], selectors: Dict[str, str]):
        """Monitor a batch of URLs"""
        print(f"\n🔍 Monitoring check at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with SyncGAScrap(headless=True, sandbox_mode=True, debug=False) as scraper:
            for url in urls:
                start_time = time.time()
                
                try:
                    # Navigate to URL
                    scraper.goto(url)
                    
                    # Extract data to verify page is working
                    data_extracted = False
                    for field_name, selector in selectors.items():
                        try:
                            value = scraper.get_text(selector)
                            if value:
                                data_extracted = True
                                break
                        except:
                            continue
                    
                    duration = time.time() - start_time
                    
                    # Get page size (approximate)
                    try:
                        content_length = len(scraper.page.content())
                    except:
                        content_length = 0
                    
                    # Record successful metric
                    metric = ScrapingMetric(
                        timestamp=datetime.now().isoformat(),
                        url=url,
                        success=data_extracted,
                        duration=duration,
                        response_size=content_length,
                        status_code=200 if data_extracted else None
                    )
                    
                    self.record_metric(metric)
                    
                    status = "✅" if data_extracted else "⚠️"
                    print(f"{status} {url} - {duration:.2f}s")
                    
                except Exception as e:
                    duration = time.time() - start_time
                    
                    # Record failed metric
                    metric = ScrapingMetric(
                        timestamp=datetime.now().isoformat(),
                        url=url,
                        success=False,
                        duration=duration,
                        error_message=str(e)
                    )
                    
                    self.record_metric(metric)
                    print(f"❌ {url} - {str(e)[:50]}...")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for monitoring dashboard"""
        current_time = datetime.now()
        
        # Get metrics for different time windows
        last_hour = current_time - timedelta(hours=1)
        last_24h = current_time - timedelta(hours=24)
        
        hour_metrics = self._get_metrics_since(last_hour)
        day_metrics = self._get_metrics_since(last_24h)
        
        # Calculate statistics
        dashboard_data = {
            "current_time": current_time.isoformat(),
            "last_hour": {
                "total_requests": len(hour_metrics),
                "successful_requests": sum(1 for m in hour_metrics if m.success),
                "failed_requests": sum(1 for m in hour_metrics if not m.success),
                "success_rate": (sum(1 for m in hour_metrics if m.success) / len(hour_metrics) * 100) if hour_metrics else 0,
                "avg_response_time": sum(m.duration for m in hour_metrics) / len(hour_metrics) if hour_metrics else 0
            },
            "last_24h": {
                "total_requests": len(day_metrics),
                "successful_requests": sum(1 for m in day_metrics if m.success),
                "failed_requests": sum(1 for m in day_metrics if not m.success),
                "success_rate": (sum(1 for m in day_metrics if m.success) / len(day_metrics) * 100) if day_metrics else 0,
                "avg_response_time": sum(m.duration for m in day_metrics) / len(day_metrics) if day_metrics else 0
            },
            "recent_alerts": self._get_recent_alerts(24),
            "recent_metrics": [asdict(m) for m in hour_metrics[-20:]],  # Last 20 metrics
            "url_performance": self._get_url_performance(day_metrics)
        }
        
        return dashboard_data
    
    def _get_recent_alerts(self, hours: int) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = datetime.now() - timedelta(hours=hours)
        
        cursor.execute("""
            SELECT timestamp, alert_type, message, severity, resolved
            FROM alerts
            WHERE datetime(timestamp) >= datetime(?)
            ORDER BY timestamp DESC
            LIMIT 50
        """, (since.isoformat(),))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [
            {
                "timestamp": row[0],
                "alert_type": row[1],
                "message": row[2],
                "severity": row[3],
                "resolved": bool(row[4])
            }
            for row in rows
        ]
    
    def _get_url_performance(self, metrics: List[ScrapingMetric]) -> Dict[str, Dict[str, Any]]:
        """Get performance statistics per URL"""
        url_stats = {}
        
        for metric in metrics:
            if metric.url not in url_stats:
                url_stats[metric.url] = {
                    "total_requests": 0,
                    "successful_requests": 0,
                    "total_duration": 0,
                    "max_duration": 0,
                    "min_duration": float('inf')
                }
            
            stats = url_stats[metric.url]
            stats["total_requests"] += 1
            
            if metric.success:
                stats["successful_requests"] += 1
            
            stats["total_duration"] += metric.duration
            stats["max_duration"] = max(stats["max_duration"], metric.duration)
            stats["min_duration"] = min(stats["min_duration"], metric.duration)
        
        # Calculate derived metrics
        for url, stats in url_stats.items():
            if stats["total_requests"] > 0:
                stats["success_rate"] = (stats["successful_requests"] / stats["total_requests"]) * 100
                stats["avg_duration"] = stats["total_duration"] / stats["total_requests"]
            else:
                stats["success_rate"] = 0
                stats["avg_duration"] = 0
            
            if stats["min_duration"] == float('inf'):
                stats["min_duration"] = 0
        
        return url_stats

class MonitoringDashboardServer:
    """Simple HTTP server for monitoring dashboard"""
    
    def __init__(self, monitor: ScrapingMonitor, port: int = 8080):
        """
        Initialize dashboard server
        
        Args:
            monitor: ScrapingMonitor instance
            port: Port to serve dashboard on
        """
        self.monitor = monitor
        self.port = port
    
    def start_server(self):
        """Start the dashboard server"""
        class DashboardHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/" or self.path == "/dashboard":
                    self.serve_dashboard()
                elif self.path == "/api/data":
                    self.serve_api_data()
                elif self.path.startswith("/static/"):
                    self.serve_static_file()
                else:
                    self.send_error(404)
            
            def serve_dashboard(self):
                html_content = self.get_dashboard_html()
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(html_content.encode())
            
            def serve_api_data(self):
                data = self.server.monitor.get_dashboard_data()
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(data, indent=2).encode())
            
            def get_dashboard_html(self):
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>GA-Scrap Monitoring Dashboard</title>
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                        .container { max-width: 1200px; margin: 0 auto; }
                        .card { background: white; padding: 20px; margin: 10px 0; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        .metric { display: inline-block; margin: 10px 20px 10px 0; }
                        .metric-value { font-size: 24px; font-weight: bold; color: #2196F3; }
                        .metric-label { font-size: 12px; color: #666; }
                        .alert { padding: 10px; margin: 5px 0; border-radius: 4px; }
                        .alert-warning { background: #fff3cd; border: 1px solid #ffeaa7; }
                        .alert-critical { background: #f8d7da; border: 1px solid #f5c6cb; }
                        .status-good { color: #28a745; }
                        .status-warning { color: #ffc107; }
                        .status-error { color: #dc3545; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
                        th { background-color: #f2f2f2; }
                    </style>
                    <script>
                        function refreshData() {
                            fetch('/api/data')
                                .then(response => response.json())
                                .then(data => updateDashboard(data))
                                .catch(error => console.error('Error:', error));
                        }
                        
                        function updateDashboard(data) {
                            // Update metrics
                            document.getElementById('hour-total').textContent = data.last_hour.total_requests;
                            document.getElementById('hour-success-rate').textContent = data.last_hour.success_rate.toFixed(1) + '%';
                            document.getElementById('hour-avg-time').textContent = data.last_hour.avg_response_time.toFixed(2) + 's';
                            
                            // Update alerts
                            const alertsContainer = document.getElementById('alerts');
                            alertsContainer.innerHTML = '';
                            data.recent_alerts.slice(0, 5).forEach(alert => {
                                const alertDiv = document.createElement('div');
                                alertDiv.className = `alert alert-${alert.severity}`;
                                alertDiv.innerHTML = `<strong>${alert.alert_type}</strong>: ${alert.message} <small>(${new Date(alert.timestamp).toLocaleString()})</small>`;
                                alertsContainer.appendChild(alertDiv);
                            });
                            
                            document.getElementById('last-update').textContent = new Date().toLocaleString();
                        }
                        
                        // Auto-refresh every 30 seconds
                        setInterval(refreshData, 30000);
                        
                        // Initial load
                        window.onload = refreshData;
                    </script>
                </head>
                <body>
                    <div class="container">
                        <h1>🔍 GA-Scrap Monitoring Dashboard</h1>
                        
                        <div class="card">
                            <h2>📊 Last Hour Metrics</h2>
                            <div class="metric">
                                <div class="metric-value" id="hour-total">-</div>
                                <div class="metric-label">Total Requests</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value" id="hour-success-rate">-</div>
                                <div class="metric-label">Success Rate</div>
                            </div>
                            <div class="metric">
                                <div class="metric-value" id="hour-avg-time">-</div>
                                <div class="metric-label">Avg Response Time</div>
                            </div>
                        </div>
                        
                        <div class="card">
                            <h2>🚨 Recent Alerts</h2>
                            <div id="alerts">
                                <p>Loading alerts...</p>
                            </div>
                        </div>
                        
                        <div class="card">
                            <p><small>Last updated: <span id="last-update">-</span></small></p>
                            <p><small>Auto-refreshes every 30 seconds</small></p>
                        </div>
                    </div>
                </body>
                </html>
                """
            
            def log_message(self, format, *args):
                pass  # Suppress default logging
        
        server = HTTPServer(('localhost', self.port), DashboardHandler)
        server.monitor = self.monitor
        
        print(f"🌐 Dashboard server started at http://localhost:{self.port}")
        print("Press Ctrl+C to stop")
        
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Stopping dashboard server...")
            server.shutdown()

# Example usage functions
def example_website_monitoring():
    """Example: Monitor website uptime and performance"""
    print("🔍 Website Monitoring Example")
    print("=" * 50)
    
    monitor = ScrapingMonitor()
    
    # URLs to monitor
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
        "https://httpbin.org/delay/2"  # This will be slower
    ]
    
    # Simple selectors to verify pages are working
    selectors = {
        "title": "title",
        "content": "body"
    }
    
    # Start monitoring in a separate thread
    monitoring_thread = threading.Thread(
        target=monitor.start_monitoring,
        args=(urls, selectors, 60),  # Check every minute
        daemon=True
    )
    monitoring_thread.start()
    
    # Start dashboard server
    dashboard = MonitoringDashboardServer(monitor, port=8080)
    dashboard.start_server()

def example_api_monitoring():
    """Example: Monitor API endpoints"""
    print("🔗 API Monitoring Example")
    print("=" * 50)
    
    monitor = ScrapingMonitor()
    
    # API endpoints to monitor
    urls = [
        "https://jsonplaceholder.typicode.com/posts/1",
        "https://jsonplaceholder.typicode.com/users/1",
        "https://httpbin.org/status/500"  # This will fail
    ]
    
    # Selectors for API responses
    selectors = {
        "response": "body"  # Just check if we get any response
    }
    
    # Configure stricter thresholds for API monitoring
    monitor.thresholds.update({
        "error_rate_threshold": 0.05,  # 5% error rate
        "response_time_threshold": 5.0,  # 5 seconds
        "consecutive_failures_threshold": 3
    })
    
    print("Starting API monitoring...")
    print("Dashboard will be available at http://localhost:8081")
    
    # Start monitoring
    monitoring_thread = threading.Thread(
        target=monitor.start_monitoring,
        args=(urls, selectors, 30),  # Check every 30 seconds
        daemon=True
    )
    monitoring_thread.start()
    
    # Start dashboard
    dashboard = MonitoringDashboardServer(monitor, port=8081)
    dashboard.start_server()

def main():
    """Main function to demonstrate monitoring"""
    print("📊 GA-Scrap Monitoring Dashboard Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Website uptime monitoring")
    print("2. API endpoint monitoring")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        example_website_monitoring()
    elif choice == "2":
        example_api_monitoring()
    else:
        print("Invalid choice. Running website monitoring example...")
        example_website_monitoring()

if __name__ == "__main__":
    main()
