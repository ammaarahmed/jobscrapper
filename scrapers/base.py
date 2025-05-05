from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
import requests
from datetime import datetime
import json
import logging
from pathlib import Path

from core.user_agent import UserAgentManager
from core.proxy_manager import ProxyManager
from core.data_model import Job, SearchParams, SearchResult, ScrapingMethod

class BaseScraper(ABC):
    def __init__(
        self,
        scraping_method: str = ScrapingMethod.API,
        api_key: Optional[str] = None,
        headless: bool = True,
        proxy_enabled: bool = True,
        user_agent_enabled: bool = True
    ):
        self.scraping_method = scraping_method
        self.api_key = api_key
        self.headless = headless
        self.proxy_enabled = proxy_enabled
        self.user_agent_enabled = user_agent_enabled
        
        # Initialize managers
        self.user_agent_manager = UserAgentManager() if user_agent_enabled else None
        self.proxy_manager = ProxyManager() if proxy_enabled else None
        
        # Setup logging
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()
        
        # Initialize scraping method specific components
        self._init_scraping_method()

    def _setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        handler = logging.FileHandler(log_dir / f"{self.__class__.__name__}.log")
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def _init_scraping_method(self):
        """Initialize components based on scraping method"""
        if self.scraping_method == ScrapingMethod.API:
            if not self.api_key:
                raise ValueError("API key is required for API scraping method")
            self._init_api_client()
        elif self.scraping_method in [ScrapingMethod.HEADLESS, ScrapingMethod.NON_HEADLESS]:
            self._init_browser()

    def _init_api_client(self):
        """Initialize API client with necessary headers and configuration"""
        self.api_headers = {
            "indeed-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        self.api_base_url = "https://api.indeed.com/v1"  # Replace with actual API endpoint

    def _init_browser(self):
        """Initialize browser for headless/non-headless scraping"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.chrome.service import Service
            from webdriver_manager.chrome import ChromeDriverManager
            
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            
            # Add common options
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            # Add user agent if enabled
            if self.user_agent_enabled:
                user_agent = self.user_agent_manager.get_next()
                options.add_argument(f"user-agent={user_agent}")
            
            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options
            )
            
        except ImportError:
            self.logger.error("Selenium dependencies not installed. Please install them using: pip install selenium webdriver-manager")
            raise

    def _make_request(self, url: str, method: str = "GET", **kwargs) -> requests.Response:
        """Make HTTP request with rotating user agents and proxies"""
        headers = self._get_headers()
        proxies = self.proxy_manager.get_proxy() if self.proxy_enabled else None
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                proxies=proxies,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            raise

    def _get_headers(self) -> Dict[str, str]:
        """Get headers with rotating user agent"""
        headers = {
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive",
        }
        
        if self.user_agent_enabled:
            headers["User-Agent"] = self.user_agent_manager.get_next()
            
        return headers

    @abstractmethod
    def search_jobs(self, params: SearchParams) -> SearchResult:
        """Search for jobs based on parameters"""
        pass

    def close(self):
        """Clean up resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()