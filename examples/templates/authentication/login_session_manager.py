"""
Login and Session Management Template
Demonstrates how to handle various authentication flows and session management
"""

import asyncio
import sys
import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

# Add parent directory to path to import ga_scrap
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ga_scrap import SyncGAScrap

class LoginSessionManager:
    """Template for managing login sessions and authentication flows"""
    
    def __init__(self, session_file: str = "session_data.json"):
        """
        Initialize login session manager
        
        Args:
            session_file: File to store session data
        """
        self.session_file = session_file
        self.session_data = self._load_session_data()
        
    def _load_session_data(self) -> Dict[str, Any]:
        """Load session data from file"""
        try:
            with open(self.session_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_session_data(self):
        """Save session data to file"""
        with open(self.session_file, "w") as f:
            json.dump(self.session_data, f, indent=2)
    
    def login_with_credentials(self, site_name: str, login_url: str, 
                              username: str, password: str,
                              login_config: Dict[str, Any]) -> bool:
        """
        Perform login with username/password
        
        Args:
            site_name: Name identifier for the site
            login_url: URL of the login page
            username: Username/email
            password: Password
            login_config: Configuration for login process
            
        Returns:
            True if login successful, False otherwise
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"🔐 Attempting login to {site_name}...", "info")
            
            try:
                # Navigate to login page
                scraper.goto(login_url)
                
                # Handle pre-login popups
                self._handle_popups(scraper)
                
                # Wait for login form
                username_selector = login_config.get("username_selector", "input[name='username'], input[name='email'], #username, #email")
                scraper.wait_for_selector(username_selector, timeout=10000)
                
                # Fill login form
                scraper.input(username_selector, username)
                
                password_selector = login_config.get("password_selector", "input[name='password'], input[type='password'], #password")
                scraper.input(password_selector, password)
                
                # Handle additional fields (like remember me)
                if "additional_fields" in login_config:
                    for field_selector, field_value in login_config["additional_fields"].items():
                        if field_value is True:  # Checkbox
                            scraper.check(field_selector)
                        else:
                            scraper.input(field_selector, field_value)
                
                # Submit form
                submit_selector = login_config.get("submit_selector", "button[type='submit'], input[type='submit'], .login-button")
                scraper.click(submit_selector)
                
                # Wait for login to complete
                success_indicators = login_config.get("success_indicators", [])
                failure_indicators = login_config.get("failure_indicators", [".error", ".alert-danger"])
                
                # Check for success/failure
                time.sleep(3)  # Wait for page to load
                
                # Check for failure first
                for failure_selector in failure_indicators:
                    if scraper.get_element(failure_selector):
                        error_text = scraper.get_text(failure_selector)
                        scraper.log(f"❌ Login failed: {error_text}", "error")
                        return False
                
                # Check for success indicators
                login_successful = False
                if success_indicators:
                    for success_selector in success_indicators:
                        if scraper.get_element(success_selector):
                            login_successful = True
                            break
                else:
                    # If no specific indicators, check if we're redirected away from login page
                    current_url = scraper.page.url
                    login_successful = current_url != login_url and "login" not in current_url.lower()
                
                if login_successful:
                    # Save session data
                    self._save_login_session(scraper, site_name, login_config)
                    scraper.log(f"✅ Login successful for {site_name}", "success")
                    return True
                else:
                    scraper.log(f"❌ Login failed for {site_name} - no success indicators found", "error")
                    return False
                    
            except Exception as e:
                scraper.log(f"❌ Login error for {site_name}: {e}", "error")
                return False
    
    def _save_login_session(self, scraper: SyncGAScrap, site_name: str, login_config: Dict[str, Any]):
        """Save login session data"""
        # Get cookies
        cookies = scraper.get_cookies()
        
        # Get current URL (might be dashboard/profile page)
        current_url = scraper.page.url
        
        # Save session info
        self.session_data[site_name] = {
            "cookies": cookies,
            "login_time": datetime.now().isoformat(),
            "current_url": current_url,
            "user_agent": scraper.page.evaluate("navigator.userAgent"),
            "session_valid": True
        }
        
        self._save_session_data()
    
    def restore_session(self, site_name: str, target_url: str = None) -> bool:
        """
        Restore a previously saved session
        
        Args:
            site_name: Name of the site to restore session for
            target_url: URL to navigate to after restoring session
            
        Returns:
            True if session restored successfully
        """
        if site_name not in self.session_data:
            print(f"❌ No saved session for {site_name}")
            return False
        
        session_info = self.session_data[site_name]
        
        # Check if session is still valid (not too old)
        login_time = datetime.fromisoformat(session_info["login_time"])
        if datetime.now() - login_time > timedelta(hours=24):
            print(f"⚠️ Session for {site_name} is too old, may need re-login")
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"🔄 Restoring session for {site_name}...", "info")
            
            try:
                # Navigate to a page on the site first
                start_url = target_url or session_info.get("current_url", "https://example.com")
                scraper.goto(start_url)
                
                # Set cookies
                for cookie in session_info["cookies"]:
                    scraper.set_cookie(cookie)
                
                # Refresh page to apply cookies
                scraper.page.reload()
                
                # Verify session is working
                if self._verify_session(scraper, site_name):
                    scraper.log(f"✅ Session restored for {site_name}", "success")
                    return True
                else:
                    scraper.log(f"❌ Session restoration failed for {site_name}", "error")
                    # Mark session as invalid
                    self.session_data[site_name]["session_valid"] = False
                    self._save_session_data()
                    return False
                    
            except Exception as e:
                scraper.log(f"❌ Error restoring session for {site_name}: {e}", "error")
                return False
    
    def _verify_session(self, scraper: SyncGAScrap, site_name: str) -> bool:
        """Verify that the session is still valid"""
        # Common indicators that user is logged in
        logged_in_indicators = [
            ".user-menu", ".profile-menu", ".logout", ".dashboard",
            "[data-testid='user-menu']", ".user-avatar", ".account-menu"
        ]
        
        # Common indicators that user is NOT logged in
        logged_out_indicators = [
            ".login-button", ".sign-in", ".login-form", 
            "a[href*='login']", "a[href*='signin']"
        ]
        
        # Check for logged-in indicators
        for selector in logged_in_indicators:
            if scraper.get_element(selector):
                return True
        
        # Check for logged-out indicators (if found, session is invalid)
        for selector in logged_out_indicators:
            if scraper.get_element(selector):
                return False
        
        # If no clear indicators, assume session is valid
        return True
    
    def login_with_oauth(self, site_name: str, oauth_url: str, 
                        oauth_config: Dict[str, Any]) -> bool:
        """
        Handle OAuth login flow
        
        Args:
            site_name: Name identifier for the site
            oauth_url: URL to start OAuth flow
            oauth_config: Configuration for OAuth process
            
        Returns:
            True if OAuth login successful
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"🔐 Starting OAuth login for {site_name}...", "info")
            
            try:
                # Navigate to OAuth start URL
                scraper.goto(oauth_url)
                
                # Click OAuth provider button
                oauth_button = oauth_config.get("oauth_button_selector", ".oauth-button")
                scraper.click(oauth_button)
                
                # Wait for OAuth provider page
                provider_indicators = oauth_config.get("provider_indicators", [])
                if provider_indicators:
                    for indicator in provider_indicators:
                        scraper.wait_for_selector(indicator, timeout=10000)
                        break
                
                # Fill OAuth credentials if needed
                if "oauth_username" in oauth_config and "oauth_password" in oauth_config:
                    username_selector = oauth_config.get("oauth_username_selector", "input[name='email']")
                    password_selector = oauth_config.get("oauth_password_selector", "input[name='password']")
                    
                    scraper.input(username_selector, oauth_config["oauth_username"])
                    scraper.input(password_selector, oauth_config["oauth_password"])
                    
                    submit_selector = oauth_config.get("oauth_submit_selector", "button[type='submit']")
                    scraper.click(submit_selector)
                
                # Wait for redirect back to original site
                redirect_indicators = oauth_config.get("redirect_indicators", [])
                if redirect_indicators:
                    for indicator in redirect_indicators:
                        scraper.wait_for_selector(indicator, timeout=30000)
                        break
                
                # Verify OAuth login success
                if self._verify_session(scraper, site_name):
                    self._save_login_session(scraper, site_name, oauth_config)
                    scraper.log(f"✅ OAuth login successful for {site_name}", "success")
                    return True
                else:
                    scraper.log(f"❌ OAuth login failed for {site_name}", "error")
                    return False
                    
            except Exception as e:
                scraper.log(f"❌ OAuth login error for {site_name}: {e}", "error")
                return False
    
    def handle_two_factor_auth(self, site_name: str, tfa_config: Dict[str, Any]) -> bool:
        """
        Handle two-factor authentication
        
        Args:
            site_name: Name of the site
            tfa_config: Configuration for 2FA process
            
        Returns:
            True if 2FA completed successfully
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"🔐 Handling 2FA for {site_name}...", "info")
            
            try:
                # Wait for 2FA prompt
                tfa_selector = tfa_config.get("tfa_input_selector", "input[name='code'], .tfa-input")
                scraper.wait_for_selector(tfa_selector, timeout=10000)
                
                # Get 2FA code
                if "tfa_code" in tfa_config:
                    # Static code provided
                    tfa_code = tfa_config["tfa_code"]
                else:
                    # Prompt user for code
                    tfa_code = input("Enter 2FA code: ").strip()
                
                # Enter 2FA code
                scraper.input(tfa_selector, tfa_code)
                
                # Submit 2FA
                submit_selector = tfa_config.get("tfa_submit_selector", "button[type='submit'], .tfa-submit")
                scraper.click(submit_selector)
                
                # Wait for 2FA completion
                time.sleep(3)
                
                # Verify 2FA success
                if self._verify_session(scraper, site_name):
                    scraper.log(f"✅ 2FA completed for {site_name}", "success")
                    return True
                else:
                    scraper.log(f"❌ 2FA failed for {site_name}", "error")
                    return False
                    
            except Exception as e:
                scraper.log(f"❌ 2FA error for {site_name}: {e}", "error")
                return False
    
    def _handle_popups(self, scraper: SyncGAScrap):
        """Handle common popups that appear before login"""
        popup_selectors = [
            ".cookie-accept", ".cookie-banner button",
            ".modal-close", ".popup-close", ".overlay-close",
            ".newsletter-popup .close", ".gdpr-accept"
        ]
        
        for selector in popup_selectors:
            scraper.click(selector)
    
    def scrape_protected_content(self, site_name: str, protected_urls: List[str],
                                selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Scrape content from protected pages using saved session
        
        Args:
            site_name: Name of the site
            protected_urls: List of URLs that require authentication
            selectors: Selectors for data extraction
            
        Returns:
            List of scraped data
        """
        scraped_data = []
        
        # First, try to restore session
        if not self.restore_session(site_name):
            print(f"❌ Cannot access protected content - session restoration failed")
            return scraped_data
        
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            # Restore session cookies
            if site_name in self.session_data:
                session_info = self.session_data[site_name]
                for cookie in session_info["cookies"]:
                    scraper.set_cookie(cookie)
            
            scraper.log(f"🔒 Scraping protected content from {site_name}...", "info")
            
            for i, url in enumerate(protected_urls):
                try:
                    scraper.log(f"📄 Accessing protected page {i+1}/{len(protected_urls)}: {url}", "info")
                    
                    # Navigate to protected page
                    scraper.goto(url)
                    
                    # Check if we're still logged in
                    if not self._verify_session(scraper, site_name):
                        scraper.log(f"⚠️ Session expired, skipping {url}", "warning")
                        continue
                    
                    # Extract data
                    page_data = {
                        "url": url,
                        "scraped_at": datetime.now().isoformat()
                    }
                    
                    for field_name, selector in selectors.items():
                        try:
                            if selector.endswith("[]"):
                                selector = selector[:-2]
                                values = scraper.get_all_text(selector)
                                page_data[field_name] = values
                            else:
                                value = scraper.get_text(selector)
                                page_data[field_name] = value
                        except Exception as e:
                            scraper.log(f"⚠️ Could not extract {field_name}: {e}", "warning")
                            page_data[field_name] = None
                    
                    scraped_data.append(page_data)
                    scraper.log(f"✅ Scraped data from {url}", "success")
                    
                except Exception as e:
                    scraper.log(f"❌ Error scraping {url}: {e}", "error")
        
        return scraped_data
    
    def logout(self, site_name: str, logout_config: Dict[str, Any]) -> bool:
        """
        Perform logout and clear session
        
        Args:
            site_name: Name of the site
            logout_config: Configuration for logout process
            
        Returns:
            True if logout successful
        """
        with SyncGAScrap(sandbox_mode=True, debug=True) as scraper:
            scraper.log(f"👋 Logging out from {site_name}...", "info")
            
            try:
                # Restore session first
                if not self.restore_session(site_name):
                    scraper.log(f"⚠️ No active session to logout from", "warning")
                    return True
                
                # Find and click logout button
                logout_selector = logout_config.get("logout_selector", ".logout, .sign-out, a[href*='logout']")
                scraper.click(logout_selector)
                
                # Wait for logout to complete
                time.sleep(2)
                
                # Verify logout
                if not self._verify_session(scraper, site_name):
                    # Clear saved session
                    if site_name in self.session_data:
                        del self.session_data[site_name]
                        self._save_session_data()
                    
                    scraper.log(f"✅ Logout successful for {site_name}", "success")
                    return True
                else:
                    scraper.log(f"❌ Logout failed for {site_name}", "error")
                    return False
                    
            except Exception as e:
                scraper.log(f"❌ Logout error for {site_name}: {e}", "error")
                return False

# Example usage functions
def example_social_media_login():
    """Example: Login to social media platform and scrape profile data"""
    print("📱 Social Media Login and Profile Scraping")
    print("=" * 50)
    
    manager = LoginSessionManager()
    
    # Login configuration
    login_config = {
        "username_selector": "input[name='username']",
        "password_selector": "input[name='password']",
        "submit_selector": "button[type='submit']",
        "success_indicators": [".user-menu", ".profile-dropdown"],
        "failure_indicators": [".error-message", ".alert-danger"]
    }
    
    # Attempt login
    success = manager.login_with_credentials(
        site_name="social_platform",
        login_url="https://social-platform.com/login",
        username="your_username",
        password="your_password",
        login_config=login_config
    )
    
    if success:
        # Scrape protected profile data
        protected_urls = [
            "https://social-platform.com/profile",
            "https://social-platform.com/messages",
            "https://social-platform.com/settings"
        ]
        
        selectors = {
            "profile_name": ".profile-name",
            "bio": ".profile-bio",
            "followers": ".followers-count",
            "following": ".following-count"
        }
        
        profile_data = manager.scrape_protected_content("social_platform", protected_urls, selectors)
        print(f"📊 Scraped {len(profile_data)} protected pages")

def example_ecommerce_account():
    """Example: Login to e-commerce account and scrape order history"""
    print("🛒 E-commerce Account Login and Order History")
    print("=" * 50)
    
    manager = LoginSessionManager()
    
    # Login with email
    login_config = {
        "username_selector": "input[type='email']",
        "password_selector": "input[type='password']",
        "submit_selector": ".login-submit",
        "success_indicators": [".account-menu", ".my-account"],
        "additional_fields": {
            "input[name='remember']": True  # Check remember me
        }
    }
    
    success = manager.login_with_credentials(
        site_name="ecommerce_site",
        login_url="https://shop.example.com/login",
        username="user@example.com",
        password="password123",
        login_config=login_config
    )
    
    if success:
        # Scrape order history
        order_urls = [
            "https://shop.example.com/account/orders",
            "https://shop.example.com/account/wishlist"
        ]
        
        selectors = {
            "order_numbers": ".order-number[]",
            "order_dates": ".order-date[]",
            "order_totals": ".order-total[]",
            "order_status": ".order-status[]"
        }
        
        order_data = manager.scrape_protected_content("ecommerce_site", order_urls, selectors)
        print(f"📦 Found {len(order_data)} order pages")

def main():
    """Main function to demonstrate authentication templates"""
    print("🔐 GA-Scrap Authentication & Session Templates")
    print("=" * 50)
    
    print("\nAvailable examples:")
    print("1. Social media login and profile scraping")
    print("2. E-commerce account and order history")
    
    choice = input("\nEnter your choice (1-2): ").strip()
    
    if choice == "1":
        example_social_media_login()
    elif choice == "2":
        example_ecommerce_account()
    else:
        print("Invalid choice. Running social media example...")
        example_social_media_login()

if __name__ == "__main__":
    main()
