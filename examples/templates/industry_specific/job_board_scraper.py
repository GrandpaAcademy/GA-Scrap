"""
Job Board Scraper Template
Specialized template for scraping job listings from various job boards
"""

import sys
import os
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class JobBoardScraper:
    """Specialized scraper for job boards and career sites"""
    
    def __init__(self, output_dir: str = "job_data"):
        """Initialize job board scraper"""
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.jobs = []
        
    def scrape_job_listings(self, job_board_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Scrape job listings from a job board
        
        Args:
            job_board_config: Configuration for the specific job board
            
        Returns:
            List of job listings
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"💼 Starting job scraping from {job_board_config.get('name', 'Unknown')}", "info")
            
            # Navigate to job search page
            search_url = self._build_search_url(job_board_config)
            scraper.goto(search_url)
            
            # Handle popups and cookies
            self._handle_job_board_popups(scraper)
            
            # Apply filters if specified
            if "filters" in job_board_config:
                self._apply_job_filters(scraper, job_board_config["filters"])
            
            # Scrape job listings with pagination
            page = 1
            max_pages = job_board_config.get("max_pages", 5)
            
            while page <= max_pages:
                scraper.log(f"📄 Scraping page {page}/{max_pages}", "info")
                
                # Wait for job listings to load
                job_selector = job_board_config["selectors"]["job_container"]
                scraper.wait_for_selector(job_selector, timeout=10000)
                
                # Extract jobs from current page
                page_jobs = self._extract_jobs_from_page(scraper, job_board_config["selectors"])
                
                if not page_jobs:
                    scraper.log("No jobs found on this page, stopping", "warning")
                    break
                
                self.jobs.extend(page_jobs)
                scraper.log(f"📋 Found {len(page_jobs)} jobs on page {page}", "info")
                
                # Go to next page
                if not self._go_to_next_page(scraper, job_board_config.get("pagination", {})):
                    scraper.log("No more pages available", "info")
                    break
                
                page += 1
            
            # Enhance job data with detailed information
            if job_board_config.get("extract_details", False):
                self._extract_job_details(scraper, job_board_config)
            
            scraper.log(f"✅ Job scraping complete! Found {len(self.jobs)} jobs", "success")
            return self.jobs
    
    def _build_search_url(self, config: Dict[str, Any]) -> str:
        """Build search URL with parameters"""
        base_url = config["base_url"]
        search_params = config.get("search_params", {})
        
        if not search_params:
            return base_url
        
        # Build query string
        params = []
        for key, value in search_params.items():
            if value:
                params.append(f"{key}={value}")
        
        query_string = "&".join(params)
        separator = "&" if "?" in base_url else "?"
        
        return f"{base_url}{separator}{query_string}"
    
    def _handle_job_board_popups(self, scraper: SyncGAScrap):
        """Handle common job board popups"""
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close",
            ".newsletter-popup .close",
            ".job-alert-popup .close",
            ".location-popup .close",
            ".gdpr-accept"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
    
    def _apply_job_filters(self, scraper: SyncGAScrap, filters: Dict[str, Any]):
        """Apply job search filters"""
        for filter_type, filter_config in filters.items():
            try:
                if filter_type == "location":
                    location_input = filter_config.get("selector", "input[name='location']")
                    scraper.input(location_input, filter_config["value"])
                
                elif filter_type == "job_type":
                    job_type_selector = filter_config.get("selector", "select[name='job_type']")
                    scraper.select_option(job_type_selector, filter_config["value"])
                
                elif filter_type == "salary_range":
                    min_salary = filter_config.get("min_selector", "input[name='min_salary']")
                    max_salary = filter_config.get("max_selector", "input[name='max_salary']")
                    scraper.input(min_salary, str(filter_config.get("min", "")))
                    scraper.input(max_salary, str(filter_config.get("max", "")))
                
                elif filter_type == "experience_level":
                    exp_selector = filter_config.get("selector", "select[name='experience']")
                    scraper.select_option(exp_selector, filter_config["value"])
                
                elif filter_type == "remote":
                    remote_checkbox = filter_config.get("selector", "input[name='remote']")
                    if filter_config.get("value", False):
                        scraper.check(remote_checkbox)
                
            except Exception as e:
                scraper.log(f"⚠️ Could not apply filter {filter_type}: {e}", "warning")
        
        # Apply filters by clicking search/filter button
        filter_button = filters.get("apply_button", "button[type='submit'], .search-button")
        scraper.click(filter_button)
    
    def _extract_jobs_from_page(self, scraper: SyncGAScrap, selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """Extract job listings from current page"""
        jobs = []
        
        # Get all job containers
        job_containers = scraper.get_all_elements(selectors["job_container"])
        
        for i in range(len(job_containers)):
            try:
                job_data = self._extract_single_job(scraper, i, selectors)
                if job_data:
                    jobs.append(job_data)
            except Exception as e:
                scraper.log(f"⚠️ Error extracting job {i}: {e}", "warning")
                continue
        
        return jobs
    
    def _extract_single_job(self, scraper: SyncGAScrap, index: int, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """Extract data from a single job listing"""
        base_selector = f"{selectors['job_container']}:nth-child({index + 1})"
        
        job_data = {
            "scraped_at": datetime.now().isoformat(),
            "job_index": index
        }
        
        # Extract basic job information
        field_mappings = {
            "title": "job_title",
            "company": "company_name", 
            "location": "job_location",
            "salary": "salary_range",
            "description": "job_description",
            "posted_date": "date_posted",
            "job_type": "employment_type",
            "experience": "experience_level",
            "link": "job_url"
        }
        
        for field, selector_key in field_mappings.items():
            if selector_key in selectors:
                try:
                    full_selector = f"{base_selector} {selectors[selector_key]}"
                    
                    if selector_key == "job_url":
                        # Extract URL from link
                        value = scraper.get_attribute(full_selector, "href")
                    else:
                        # Extract text content
                        value = scraper.get_text(full_selector)
                    
                    job_data[field] = value
                    
                except Exception as e:
                    job_data[field] = None
        
        # Clean and enhance job data
        job_data = self._clean_job_data(job_data)
        
        # Only return job if we have essential information
        if job_data.get("title") and job_data.get("company"):
            return job_data
        
        return None
    
    def _clean_job_data(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize job data"""
        # Clean title
        if job_data.get("title"):
            job_data["title"] = job_data["title"].strip()
        
        # Clean company name
        if job_data.get("company"):
            job_data["company"] = job_data["company"].strip()
        
        # Parse salary information
        if job_data.get("salary"):
            salary_info = self._parse_salary(job_data["salary"])
            job_data.update(salary_info)
        
        # Parse and normalize location
        if job_data.get("location"):
            location_info = self._parse_location(job_data["location"])
            job_data.update(location_info)
        
        # Parse posted date
        if job_data.get("posted_date"):
            parsed_date = self._parse_posted_date(job_data["posted_date"])
            if parsed_date:
                job_data["posted_date_parsed"] = parsed_date
        
        # Make job URL absolute
        if job_data.get("link") and not job_data["link"].startswith("http"):
            if job_data["link"].startswith("/"):
                # Assume we need to add the domain
                job_data["link"] = f"https://example-jobboard.com{job_data['link']}"
        
        return job_data
    
    def _parse_salary(self, salary_text: str) -> Dict[str, Any]:
        """Parse salary information from text"""
        salary_info = {"salary_text": salary_text}
        
        # Extract numeric values
        numbers = re.findall(r'[\d,]+', salary_text.replace(',', ''))
        
        if numbers:
            try:
                if len(numbers) == 1:
                    # Single salary value
                    salary_info["salary_min"] = int(numbers[0])
                    salary_info["salary_max"] = int(numbers[0])
                elif len(numbers) >= 2:
                    # Salary range
                    salary_info["salary_min"] = int(numbers[0])
                    salary_info["salary_max"] = int(numbers[1])
            except ValueError:
                pass
        
        # Determine salary period
        salary_lower = salary_text.lower()
        if "hour" in salary_lower or "/hr" in salary_lower:
            salary_info["salary_period"] = "hourly"
        elif "year" in salary_lower or "annual" in salary_lower:
            salary_info["salary_period"] = "yearly"
        elif "month" in salary_lower:
            salary_info["salary_period"] = "monthly"
        
        # Determine currency
        if "$" in salary_text:
            salary_info["currency"] = "USD"
        elif "€" in salary_text:
            salary_info["currency"] = "EUR"
        elif "£" in salary_text:
            salary_info["currency"] = "GBP"
        
        return salary_info
    
    def _parse_location(self, location_text: str) -> Dict[str, Any]:
        """Parse location information"""
        location_info = {"location_text": location_text}
        
        # Check for remote work indicators
        remote_keywords = ["remote", "work from home", "wfh", "telecommute"]
        if any(keyword in location_text.lower() for keyword in remote_keywords):
            location_info["is_remote"] = True
        else:
            location_info["is_remote"] = False
        
        # Extract city and state/country (basic parsing)
        parts = location_text.split(",")
        if len(parts) >= 2:
            location_info["city"] = parts[0].strip()
            location_info["state_country"] = parts[1].strip()
        
        return location_info
    
    def _parse_posted_date(self, date_text: str) -> Optional[str]:
        """Parse posted date to ISO format"""
        try:
            date_lower = date_text.lower().strip()
            
            # Handle relative dates
            if "today" in date_lower:
                return datetime.now().isoformat()
            elif "yesterday" in date_lower:
                return (datetime.now() - timedelta(days=1)).isoformat()
            elif "ago" in date_lower:
                # Extract number of days/hours ago
                numbers = re.findall(r'\d+', date_text)
                if numbers:
                    num = int(numbers[0])
                    if "day" in date_lower:
                        return (datetime.now() - timedelta(days=num)).isoformat()
                    elif "hour" in date_lower:
                        return (datetime.now() - timedelta(hours=num)).isoformat()
                    elif "week" in date_lower:
                        return (datetime.now() - timedelta(weeks=num)).isoformat()
            
            # Try to parse absolute dates (basic patterns)
            # This would need to be expanded for different date formats
            
        except Exception:
            pass
        
        return None
    
    def _go_to_next_page(self, scraper: SyncGAScrap, pagination_config: Dict[str, Any]) -> bool:
        """Navigate to next page of results"""
        next_selectors = pagination_config.get("next_selectors", [
            ".pagination .next:not(.disabled)",
            ".pager .next",
            "a[aria-label='Next page']",
            ".next-page"
        ])
        
        for selector in next_selectors:
            if scraper.click(selector):
                # Wait for new page to load
                scraper.wait_for_load_state("networkidle")
                return True
        
        return False
    
    def _extract_job_details(self, scraper: SyncGAScrap, config: Dict[str, Any]):
        """Extract detailed information for each job"""
        scraper.log("🔍 Extracting detailed job information...", "info")
        
        for i, job in enumerate(self.jobs):
            if job.get("link"):
                try:
                    scraper.log(f"📋 Getting details for job {i+1}/{len(self.jobs)}", "info")
                    
                    # Navigate to job detail page
                    scraper.goto(job["link"])
                    
                    # Extract additional details
                    detail_selectors = config.get("detail_selectors", {})
                    for field, selector in detail_selectors.items():
                        try:
                            value = scraper.get_text(selector)
                            job[f"detail_{field}"] = value
                        except:
                            job[f"detail_{field}"] = None
                    
                    # Brief pause between requests
                    scraper.wait(1000)
                    
                except Exception as e:
                    scraper.log(f"⚠️ Could not get details for job {i+1}: {e}", "warning")
    
    def save_jobs(self, filename: str = None) -> str:
        """Save scraped jobs to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"jobs_{timestamp}.json"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(self.jobs)} jobs to {filepath}")
        return filepath
    
    def filter_jobs(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter jobs based on criteria"""
        filtered_jobs = []
        
        for job in self.jobs:
            matches = True
            
            # Filter by salary range
            if "min_salary" in criteria and job.get("salary_min"):
                if job["salary_min"] < criteria["min_salary"]:
                    matches = False
            
            # Filter by location
            if "location_keywords" in criteria:
                location_text = job.get("location_text", "").lower()
                if not any(keyword.lower() in location_text for keyword in criteria["location_keywords"]):
                    matches = False
            
            # Filter by remote work
            if "remote_only" in criteria and criteria["remote_only"]:
                if not job.get("is_remote", False):
                    matches = False
            
            # Filter by keywords in title or description
            if "keywords" in criteria:
                title_desc = f"{job.get('title', '')} {job.get('description', '')}".lower()
                if not any(keyword.lower() in title_desc for keyword in criteria["keywords"]):
                    matches = False
            
            if matches:
                filtered_jobs.append(job)
        
        return filtered_jobs

# Example usage
def example_tech_jobs():
    """Example: Scrape tech jobs from a job board"""
    print("💻 Tech Jobs Scraper Example")
    print("=" * 50)
    
    scraper = JobBoardScraper()
    
    # Configuration for a hypothetical job board
    job_board_config = {
        "name": "TechJobs",
        "base_url": "https://example-jobboard.com/jobs",
        "search_params": {
            "q": "software engineer",
            "location": "San Francisco"
        },
        "max_pages": 3,
        "selectors": {
            "job_container": ".job-listing",
            "job_title": ".job-title",
            "company_name": ".company-name",
            "job_location": ".job-location",
            "salary_range": ".salary",
            "date_posted": ".posted-date",
            "job_url": "a.job-link@href"
        },
        "filters": {
            "job_type": {
                "selector": "select[name='employment_type']",
                "value": "full-time"
            },
            "remote": {
                "selector": "input[name='remote_ok']",
                "value": True
            }
        },
        "pagination": {
            "next_selectors": [".pagination .next"]
        }
    }
    
    # Scrape jobs
    jobs = scraper.scrape_job_listings(job_board_config)
    
    # Filter for high-paying remote jobs
    filtered_jobs = scraper.filter_jobs({
        "min_salary": 100000,
        "remote_only": True,
        "keywords": ["python", "javascript", "react"]
    })
    
    # Save results
    scraper.save_jobs()
    
    print(f"\n📊 Results:")
    print(f"Total jobs found: {len(jobs)}")
    print(f"Filtered jobs: {len(filtered_jobs)}")
    
    # Show sample jobs
    for job in jobs[:3]:
        print(f"\n📋 {job.get('title', 'N/A')}")
        print(f"🏢 {job.get('company', 'N/A')}")
        print(f"📍 {job.get('location', 'N/A')}")
        print(f"💰 {job.get('salary', 'N/A')}")

if __name__ == "__main__":
    example_tech_jobs()
