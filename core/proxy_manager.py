from dataclasses import dataclass
from typing import Dict, List, Optional, TypedDict
from itertools import cycle
import requests
from config.settings import settings

class ProxyConnection(TypedDict):
    publicIp: str
    httpPort: int
    ipVersion: str

class ProxyAuth(TypedDict):
    username: str
    password: str

class ProxyData(TypedDict):
    id: int
    status: str
    networkType: str
    authentication: ProxyAuth
    connection: ProxyConnection
    proxyType: str

@dataclass
class Proxy:
    """Represents a single proxy configuration."""
    ip: str
    port: int
    username: str
    password: str
    
    @property
    def url(self) -> str:
        """Get the formatted proxy URL."""
        return f"http://{self.username}:{self.password}@{self.ip}:{self.port}"
    
    def to_dict(self) -> Dict[str, str]:
        """Convert proxy to dictionary format for requests library."""
        return {
            "http": self.url,
            "https": self.url
        }

class ProxyManager:
    """Manages a pool of residential proxies with rotation capability."""
    
    def __init__(self, residential: bool = True) -> None:
        """Initialize the proxy manager and fetch available proxies."""
        self.residential = residential

        self.residential_proxies: List[Proxy] = self._fetch_residential_proxies()
        self.mobile_proxy: Proxy = self._fetch_mobile_proxy()

        if not self.residential_proxies and not self.mobile_proxy:
            raise Exception("No residential or mobile proxies found!")
        
        if self.residential:
            self.proxy_pool = cycle(self.residential_proxies)  

    def _fetch_residential_proxies(self) -> List[Proxy]:
        """
        Fetch and filter residential proxies from the API.
        
        Returns:
            List[Proxy]: List of configured proxy objects
        """
        headers = {
            "Accept": "application/json",
            "X-Api-Key": settings.residential_proxy.api_key,
            "X-Api-Secret": settings.residential_proxy.api_secret
        }
        
        response = requests.get(
            settings.residential_proxy.url,
            headers=headers,
            timeout=settings.scraper.request_timeout
        )
        response.raise_for_status()
        
        data = response.json()
        residential = [
            p for p in data.get("proxies", [])
            if p.get("networkType") == "RESIDENTIAL_STATIC" 
            and p.get("status") == "ACTIVE"
        ]
        
        return [
            Proxy(
                ip=proxy["connection"]["publicIp"],
                port=proxy["connection"]["httpPort"],
                username=proxy["authentication"]["username"],
                password=proxy["authentication"]["password"]
            )
            for proxy in residential
        ]
    
    def _fetch_mobile_proxy(self) -> Proxy:
        """Fetch a mobile proxy from the API."""
        
        mobile_request_proxy = f"http://{settings.mobile_proxy.username}:{settings.mobile_proxy.password}@{settings.mobile_proxy.host}:{settings.mobile_proxy.port}"
        mobile_request_proxies = {
            "http": mobile_request_proxy,
            "https": mobile_request_proxy,
        }

        try: # TODO: figure out why the mobile proxy ip request is timing out
            response = requests.get(
                settings.mobile_proxy.url,
                proxies=mobile_request_proxies,
                timeout=settings.scraper.request_timeout
            )
            response.raise_for_status()
            data = response.json()["origin"]
            print("Mobile proxy fetched: ", data)
            return Proxy(
                ip=data,
                port=settings.mobile_proxy.port,
                username=settings.mobile_proxy.username,
                password=settings.mobile_proxy.password
            )
        except TimeoutError:
            print(f"Error fetching mobile proxy: {e}")
            return None
        except Exception as e:
            print(f"Error fetching mobile proxy: {e}")
            return None

    
    def switch_proxy(self) -> None:
        """Switch to the next proxy in the pool."""
        self.residential = not self.residential

    def get_next_proxy(self) -> Dict[str, str]:
        """
        Get the next proxy in rotation.
        
        Returns:
            Dict[str, str]: Proxy configuration for requests library
        """
        if self.residential:
            proxy = next(self.proxy_pool)
            return proxy.to_dict()
        else:
            proxy = next(self.proxy_pool)
            return proxy.to_dict()

    def refresh_proxies(self) -> None:
        """Refresh the proxy pool with new proxies from the API."""
        self.proxies = self._fetch_residential_proxies()
        self.proxy_pool = cycle(self.proxies)

# Example usage:
if __name__ == "__main__":
    proxy_manager = ProxyManager()
    for _ in range(5):  # Get 5 proxies in rotation
        print(proxy_manager.get_next_proxy())