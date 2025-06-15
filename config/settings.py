import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml

@dataclass
class ResidentialProxySettings:
    url: str
    api_key: str
    api_secret: str

@dataclass
class MobileProxySettings:
    username: str
    password: str
    port: int
    host: str
    url: str
@dataclass
class ScraperSettings:
    request_timeout: int = 10
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    delay_between_requests: float = 2.0

@dataclass
class StorageSettings:
    output_format: str = "csv"
    output_directory: str = "data"
    filename_prefix: str = "jobs_"

@dataclass
class IndeedSettings:
    api_key: str

class Settings:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or self._get_default_config_path()
        self._load_config()
        
    def _get_default_config_path(self) -> str:
        """Get the default path to the config.yaml file."""
        return str(Path(__file__).parent / "config.yaml")
    
    def _load_config(self) -> None:
        """Load configuration from YAML file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        # Load proxy settings
        self.residential_proxy = ResidentialProxySettings(
            url=config_data['residential_proxy']['url'],
            api_key=config_data['residential_proxy']['api_key'],
            api_secret=config_data['residential_proxy']['api_secret']
        )

        self.mobile_proxy = MobileProxySettings(
            username=config_data['mobile_proxy']['username'],
            password=config_data['mobile_proxy']['password'],
            port=config_data['mobile_proxy']['port'],
            host=config_data['mobile_proxy']['host'],
            url=config_data['mobile_proxy']['url']
        )
        
        # Load scraper settings with defaults
        self.scraper = ScraperSettings()
        
        # Load storage settings with defaults
        self.storage = StorageSettings()

        # Load indeed settings with defaults
        self.indeed = IndeedSettings(
            api_key=config_data['indeed']['api_key']
        )
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

# Create a global settings instance
settings = Settings()

