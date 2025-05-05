import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import yaml

@dataclass
class ProxySettings:
    api_url: str
    api_key: str
    api_secret: str

@dataclass
class ScraperSettings:
    request_timeout: int = 30
    max_retries: int = 3
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    delay_between_requests: float = 2.0

@dataclass
class StorageSettings:
    output_format: str = "csv"
    output_directory: str = "data"
    filename_prefix: str = "jobs_"

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
        self.proxy = ProxySettings(
            api_url=config_data['API_URL'],
            api_key=config_data['API_KEY'],
            api_secret=config_data['API_SECRET']
        )
        
        # Load scraper settings with defaults
        self.scraper = ScraperSettings()
        
        # Load storage settings with defaults
        self.storage = StorageSettings()
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self._load_config()

# Create a global settings instance
settings = Settings()

