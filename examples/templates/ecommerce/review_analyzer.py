"""
E-commerce Review Analyzer Template
Scrapes and analyzes product reviews with sentiment analysis and insights
"""

import asyncio
import sys
import os
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from collections import Counter

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class ReviewAnalyzer:
    """Template for scraping and analyzing product reviews"""
    
    def __init__(self, output_dir: str = "review_analysis"):
        """
        Initialize review analyzer
        
        Args:
            output_dir: Directory to save analysis results
        """
        self.output_dir = output_dir
        self.reviews = []
        self._ensure_output_dir()
    
    def _ensure_output_dir(self):
        """Create output directory if it doesn't exist"""
        os.makedirs(self.output_dir, exist_ok=True)
    
    def analyze_product_reviews(self, product_url: str, max_pages: int = 5) -> Dict[str, Any]:
        """
        Scrape and analyze reviews for a product
        
        Args:
            product_url: URL of the product page
            max_pages: Maximum review pages to scrape
            
        Returns:
            Analysis results dictionary
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log("📝 Starting review analysis...", "info")
            
            # Navigate to product page
            scraper.goto(product_url)
            
            # Extract product info
            product_info = self._extract_product_info(scraper)
            
            # Navigate to reviews section
            self._navigate_to_reviews(scraper)
            
            # Scrape reviews
            self.reviews = self._scrape_all_reviews(scraper, max_pages)
            
            # Analyze reviews
            analysis = self._analyze_reviews(product_info)
            
            # Save results
            self._save_analysis(analysis)
            
            scraper.log(f"✅ Analysis complete! Analyzed {len(self.reviews)} reviews", "success")
            return analysis
    
    def _extract_product_info(self, scraper: SyncGAScrap) -> Dict[str, Any]:
        """Extract basic product information"""
        product_info = {
            "url": scraper.page.url,
            "scraped_at": datetime.now().isoformat()
        }
        
        # Common selectors for product info
        selectors = {
            "title": ["h1", ".product-title", ".product-name", "[data-testid='product-title']"],
            "price": [".price", ".product-price", ".current-price", ".price-current"],
            "rating": [".rating", ".average-rating", ".product-rating", ".stars"],
            "review_count": [".review-count", ".reviews-count", ".total-reviews"]
        }
        
        for field, field_selectors in selectors.items():
            for selector in field_selectors:
                try:
                    value = scraper.get_text(selector)
                    if value:
                        product_info[field] = value.strip()
                        break
                except:
                    continue
        
        return product_info
    
    def _navigate_to_reviews(self, scraper: SyncGAScrap):
        """Navigate to the reviews section"""
        # Try to find and click reviews tab/link
        review_nav_selectors = [
            "a[href*='review']",
            ".reviews-tab",
            ".tab-reviews",
            "[data-testid='reviews-tab']",
            "button:contains('Reviews')",
            ".review-section-link"
        ]
        
        for selector in review_nav_selectors:
            if scraper.click(selector):
                scraper.wait_for_selector(".review, .review-item", timeout=5000)
                break
        
        # Scroll to reviews section if no clickable element found
        review_section_selectors = [
            "#reviews",
            ".reviews-section",
            ".review-list",
            ".customer-reviews"
        ]
        
        for selector in review_section_selectors:
            try:
                scraper.scroll_to_element(selector)
                break
            except:
                continue
    
    def _scrape_all_reviews(self, scraper: SyncGAScrap, max_pages: int) -> List[Dict[str, Any]]:
        """Scrape reviews from multiple pages"""
        all_reviews = []
        page = 1
        
        while page <= max_pages:
            scraper.log(f"📄 Scraping reviews page {page}...", "info")
            
            # Wait for reviews to load
            scraper.wait_for_selector(".review, .review-item, .customer-review", timeout=10000)
            
            # Extract reviews from current page
            page_reviews = self._extract_reviews_from_page(scraper)
            
            if not page_reviews:
                scraper.log("No reviews found on this page", "warning")
                break
            
            all_reviews.extend(page_reviews)
            scraper.log(f"Found {len(page_reviews)} reviews on page {page}", "info")
            
            # Try to go to next page
            if not self._go_to_next_review_page(scraper):
                scraper.log("No more review pages", "info")
                break
            
            page += 1
        
        return all_reviews
    
    def _extract_reviews_from_page(self, scraper: SyncGAScrap) -> List[Dict[str, Any]]:
        """Extract reviews from current page"""
        reviews = []
        
        # Common review container selectors
        review_selectors = [
            ".review",
            ".review-item", 
            ".customer-review",
            "[data-testid='review']",
            ".review-card"
        ]
        
        # Find review containers
        review_elements = None
        for selector in review_selectors:
            try:
                elements = scraper.get_all_elements(selector)
                if elements:
                    review_elements = elements
                    break
            except:
                continue
        
        if not review_elements:
            return reviews
        
        # Extract data from each review
        for i in range(len(review_elements)):
            try:
                review_data = self._extract_single_review(scraper, i)
                if review_data:
                    reviews.append(review_data)
            except Exception as e:
                scraper.log(f"Error extracting review {i}: {e}", "warning")
                continue
        
        return reviews
    
    def _extract_single_review(self, scraper: SyncGAScrap, index: int) -> Dict[str, Any]:
        """Extract data from a single review"""
        review = {
            "scraped_at": datetime.now().isoformat()
        }
        
        # Selectors for review data
        base_selectors = [
            f".review:nth-child({index + 1})",
            f".review-item:nth-child({index + 1})",
            f".customer-review:nth-child({index + 1})"
        ]
        
        # Try each base selector
        for base in base_selectors:
            # Extract review fields
            fields = {
                "rating": [f"{base} .rating", f"{base} .stars", f"{base} .review-rating"],
                "title": [f"{base} .review-title", f"{base} .review-headline", f"{base} h3"],
                "text": [f"{base} .review-text", f"{base} .review-body", f"{base} .review-content"],
                "author": [f"{base} .reviewer-name", f"{base} .author", f"{base} .customer-name"],
                "date": [f"{base} .review-date", f"{base} .date", f"{base} .review-time"],
                "verified": [f"{base} .verified", f"{base} .verified-purchase"],
                "helpful_count": [f"{base} .helpful-count", f"{base} .votes"]
            }
            
            extracted_any = False
            for field, selectors in fields.items():
                for selector in selectors:
                    try:
                        value = scraper.get_text(selector)
                        if value:
                            review[field] = value.strip()
                            extracted_any = True
                            break
                    except:
                        continue
                if field in review:
                    break
            
            if extracted_any:
                break
        
        # Clean and parse data
        review = self._clean_review_data(review)
        
        return review if review.get("text") else None
    
    def _clean_review_data(self, review: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize review data"""
        # Parse rating
        if review.get("rating"):
            rating_text = review["rating"]
            rating_match = re.search(r'(\d+\.?\d*)', rating_text)
            if rating_match:
                try:
                    review["rating_numeric"] = float(rating_match.group())
                except:
                    pass
        
        # Parse helpful count
        if review.get("helpful_count"):
            helpful_text = review["helpful_count"]
            helpful_match = re.search(r'(\d+)', helpful_text)
            if helpful_match:
                try:
                    review["helpful_count_numeric"] = int(helpful_match.group())
                except:
                    pass
        
        # Parse date
        if review.get("date"):
            # Basic date parsing - can be enhanced
            date_text = review["date"]
            # Remove common prefixes
            date_text = re.sub(r'^(on|reviewed|posted)\s+', '', date_text, flags=re.IGNORECASE)
            review["date_cleaned"] = date_text.strip()
        
        # Check if verified purchase
        if review.get("verified"):
            review["is_verified"] = "verified" in review["verified"].lower()
        
        return review
    
    def _go_to_next_review_page(self, scraper: SyncGAScrap) -> bool:
        """Navigate to next page of reviews"""
        next_selectors = [
            ".reviews-pagination .next:not(.disabled)",
            ".review-pagination .next",
            ".pagination .next",
            "[aria-label='Next page']",
            ".load-more-reviews"
        ]
        
        for selector in next_selectors:
            if scraper.click(selector):
                scraper.wait_for_load_state("networkidle")
                return True
        
        return False
    
    def _analyze_reviews(self, product_info: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze scraped reviews"""
        if not self.reviews:
            return {"error": "No reviews to analyze"}
        
        analysis = {
            "product_info": product_info,
            "total_reviews": len(self.reviews),
            "analysis_date": datetime.now().isoformat()
        }
        
        # Rating analysis
        ratings = [r.get("rating_numeric") for r in self.reviews if r.get("rating_numeric")]
        if ratings:
            analysis["rating_stats"] = {
                "average": sum(ratings) / len(ratings),
                "min": min(ratings),
                "max": max(ratings),
                "distribution": dict(Counter(ratings))
            }
        
        # Sentiment analysis (basic keyword-based)
        analysis["sentiment"] = self._analyze_sentiment()
        
        # Common themes
        analysis["themes"] = self._extract_themes()
        
        # Review quality metrics
        analysis["quality_metrics"] = self._analyze_quality()
        
        # Time analysis
        analysis["time_analysis"] = self._analyze_time_patterns()
        
        return analysis
    
    def _analyze_sentiment(self) -> Dict[str, Any]:
        """Basic sentiment analysis using keywords"""
        positive_words = [
            "excellent", "amazing", "great", "love", "perfect", "awesome", 
            "fantastic", "wonderful", "outstanding", "brilliant", "superb"
        ]
        
        negative_words = [
            "terrible", "awful", "hate", "horrible", "worst", "bad",
            "disappointing", "useless", "broken", "defective", "poor"
        ]
        
        sentiment_scores = []
        
        for review in self.reviews:
            text = (review.get("text", "") + " " + review.get("title", "")).lower()
            
            positive_count = sum(1 for word in positive_words if word in text)
            negative_count = sum(1 for word in negative_words if word in text)
            
            if positive_count > negative_count:
                sentiment_scores.append("positive")
            elif negative_count > positive_count:
                sentiment_scores.append("negative")
            else:
                sentiment_scores.append("neutral")
        
        sentiment_distribution = dict(Counter(sentiment_scores))
        
        return {
            "distribution": sentiment_distribution,
            "positive_percentage": sentiment_distribution.get("positive", 0) / len(sentiment_scores) * 100,
            "negative_percentage": sentiment_distribution.get("negative", 0) / len(sentiment_scores) * 100
        }
    
    def _extract_themes(self) -> Dict[str, Any]:
        """Extract common themes from reviews"""
        # Combine all review text
        all_text = " ".join([
            (review.get("text", "") + " " + review.get("title", "")).lower()
            for review in self.reviews
        ])
        
        # Common product-related keywords
        themes = {
            "quality": ["quality", "build", "construction", "material", "durable"],
            "price": ["price", "cost", "expensive", "cheap", "value", "money"],
            "shipping": ["shipping", "delivery", "arrived", "package", "fast"],
            "customer_service": ["service", "support", "help", "staff", "response"],
            "usability": ["easy", "difficult", "simple", "complicated", "user-friendly"],
            "performance": ["performance", "speed", "fast", "slow", "efficient"]
        }
        
        theme_counts = {}
        for theme, keywords in themes.items():
            count = sum(all_text.count(keyword) for keyword in keywords)
            if count > 0:
                theme_counts[theme] = count
        
        return theme_counts
    
    def _analyze_quality(self) -> Dict[str, Any]:
        """Analyze review quality metrics"""
        verified_count = sum(1 for r in self.reviews if r.get("is_verified"))
        
        # Text length analysis
        text_lengths = [len(r.get("text", "")) for r in self.reviews]
        avg_length = sum(text_lengths) / len(text_lengths) if text_lengths else 0
        
        # Reviews with helpful votes
        helpful_reviews = [r for r in self.reviews if r.get("helpful_count_numeric", 0) > 0]
        
        return {
            "verified_percentage": (verified_count / len(self.reviews)) * 100,
            "average_text_length": avg_length,
            "reviews_with_helpful_votes": len(helpful_reviews),
            "detailed_reviews": len([r for r in self.reviews if len(r.get("text", "")) > 100])
        }
    
    def _analyze_time_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in reviews"""
        # This is a basic implementation - can be enhanced with proper date parsing
        dates = [r.get("date_cleaned") for r in self.reviews if r.get("date_cleaned")]
        
        return {
            "reviews_with_dates": len(dates),
            "date_range": f"{min(dates)} to {max(dates)}" if dates else "Unknown"
        }
    
    def _save_analysis(self, analysis: Dict[str, Any]):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save full analysis
        analysis_file = os.path.join(self.output_dir, f"review_analysis_{timestamp}.json")
        with open(analysis_file, "w", encoding="utf-8") as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        
        # Save raw reviews
        reviews_file = os.path.join(self.output_dir, f"raw_reviews_{timestamp}.json")
        with open(reviews_file, "w", encoding="utf-8") as f:
            json.dump(self.reviews, f, indent=2, ensure_ascii=False)
        
        # Generate summary report
        report = self._generate_summary_report(analysis)
        report_file = os.path.join(self.output_dir, f"review_summary_{timestamp}.txt")
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"💾 Analysis saved to {self.output_dir}/")
    
    def _generate_summary_report(self, analysis: Dict[str, Any]) -> str:
        """Generate a human-readable summary report"""
        report = "📝 Review Analysis Summary\n"
        report += "=" * 50 + "\n\n"
        
        # Product info
        product_info = analysis.get("product_info", {})
        report += f"📦 Product: {product_info.get('title', 'Unknown')}\n"
        report += f"🔗 URL: {product_info.get('url', 'Unknown')}\n"
        report += f"📊 Total Reviews Analyzed: {analysis.get('total_reviews', 0)}\n\n"
        
        # Rating stats
        rating_stats = analysis.get("rating_stats", {})
        if rating_stats:
            report += f"⭐ Average Rating: {rating_stats.get('average', 0):.1f}/5\n"
            report += f"📈 Rating Range: {rating_stats.get('min', 0)} - {rating_stats.get('max', 0)}\n\n"
        
        # Sentiment
        sentiment = analysis.get("sentiment", {})
        if sentiment:
            report += f"😊 Positive Reviews: {sentiment.get('positive_percentage', 0):.1f}%\n"
            report += f"😞 Negative Reviews: {sentiment.get('negative_percentage', 0):.1f}%\n\n"
        
        # Top themes
        themes = analysis.get("themes", {})
        if themes:
            report += "🏷️ Top Discussion Themes:\n"
            sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)
            for theme, count in sorted_themes[:5]:
                report += f"  • {theme.title()}: {count} mentions\n"
            report += "\n"
        
        # Quality metrics
        quality = analysis.get("quality_metrics", {})
        if quality:
            report += f"✅ Verified Reviews: {quality.get('verified_percentage', 0):.1f}%\n"
            report += f"📝 Average Review Length: {quality.get('average_text_length', 0):.0f} characters\n"
            report += f"📖 Detailed Reviews: {quality.get('detailed_reviews', 0)}\n"
        
        return report

# Example usage
def main():
    """Example usage of the review analyzer"""
    print("📝 GA-Scrap Review Analyzer Template")
    print("=" * 40)
    
    # Initialize analyzer
    analyzer = ReviewAnalyzer()
    
    # Example product URL (replace with real URL)
    product_url = "https://example-store.com/product/123"
    
    # Analyze reviews
    analysis = analyzer.analyze_product_reviews(product_url, max_pages=3)
    
    # Display summary
    if "error" not in analysis:
        print(f"\n📊 Analysis Summary:")
        print(f"Total reviews: {analysis.get('total_reviews', 0)}")
        
        rating_stats = analysis.get('rating_stats', {})
        if rating_stats:
            print(f"Average rating: {rating_stats.get('average', 0):.1f}/5")
        
        sentiment = analysis.get('sentiment', {})
        if sentiment:
            print(f"Positive sentiment: {sentiment.get('positive_percentage', 0):.1f}%")

if __name__ == "__main__":
    main()
