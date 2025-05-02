import configparser 
import requests
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import itertools

config = configparser.ConfigParser()
config.read('config.ini')

apiKey = config['proxy']['api_key']
apiSecret = config['proxy']['api_secret']
proxyProvider = "https://api.proxy-cheap.com/proxies"


@dataclass
class Proxy:
    id: int
    status: str
    network_type: str
    username: Optional[str]
    password: Optional[str]
    public_ip: Optional[str]
    connect_ip: Optional[str]
    ip_version: Optional[str]
    http_port: Optional[int]
    https_port: Optional[int]
    socks5_port: Optional[int]
    proxy_type: Optional[str]
    created_at: Optional[str]
    expires_at: Optional[str]
    metadata: Dict[str, Any]
    bandwidth: Dict[str, Any]
    routes: List[Any]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Proxy":
        auth = data.get("authentication", {})
        conn = data.get("connection", {})
        return cls(
            id=data["id"],
            status=data["status"],
            network_type=data["networkType"],
            username=auth.get("username"),
            password=auth.get("password"),
            public_ip=conn.get("publicIp"),
            connect_ip=conn.get("connectIp"),
            ip_version=conn.get("ipVersion"),
            http_port=conn.get("httpPort"),
            https_port=conn.get("httpsPort"),
            socks5_port=conn.get("socks5Port"),
            proxy_type=data.get("proxyType"),
            created_at=data.get("createdAt"),
            expires_at=data.get("expiresAt"),
            metadata=data.get("metadata", {}),
            bandwidth=data.get("bandwidth", {}),
            routes=data.get("routes", []),
        )

    def to_requests_dict(self) -> Dict[str, str]:
        if not all([self.username, self.password,
                    self.connect_ip, self.http_port]):
            raise ValueError("Missing auth/connection fields")
        url = (
            f"http://{self.username}:{self.password}"
            f"@{self.connect_ip}:{self.http_port}"
        )
        return {"http": url, "https": url}



class ProxyManager:
    def __init__(self, proxies: List[Proxy]) -> None:
        """
        Build per-network-type rotation cycles from an existing list
        of Proxy objects (assumed already ACTIVE).
        """
        # group by network_type
        grouped: Dict[str, List[Proxy]] = {}
        for p in proxies:
            if p.status.upper() != "ACTIVE":
                continue
            grouped.setdefault(p.network_type.upper(), []).append(p)

        # build a cycle for each network_type
        self._cycles: Dict[str, itertools.cycle] = {
            nt: itertools.cycle(lst) for nt, lst in grouped.items()
        }

        # pick a default current_type
        if "RESIDENTIAL_STATIC" in self._cycles:
            self.current_type = "RESIDENTIAL_STATIC"
        elif "MOBILE" in self._cycles:
            self.current_type = "MOBILE"
        else:
            self.current_type = next(iter(self._cycles), None)

    @classmethod
    def load_from_api(
        cls,
        proxy_provider: str,
        timeout: float = 10.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> "ProxyManager":
        """
        Fetch the proxy list JSON from api_url, parse into Proxy
        objects, and return a ready-to-use ProxyManager.
        """
        payload={}
        headers = {
          'Accept': 'application/json',
          'X-Api-Key': apiKey,
          'X-Api-Secret': apiSecret 
        }

        resp = requests.request("GET", proxy_provider , headers=headers, data=payload)

        resp.raise_for_status()

        data = resp.json()

        proxies = [
            Proxy.from_dict(d)
            for d in data.get("proxies", [])
        ]
        return cls(proxies)

    def set_current_type(self, network_type: str) -> None:
        nt = network_type.upper()
        if nt not in self._cycles:
            raise ValueError(f"No proxies for network_type {nt}")
        self.current_type = nt

    def toggle_type(self) -> None:
        a, b = "RESIDENTIAL_STATIC", "MOBILE"
        if a in self._cycles and b in self._cycles:
            self.current_type = b if self.current_type == a else a

    def get_next_current(self) -> Optional[Proxy]:
        """
        Round-robin from the currently selected network_type.
        """
        if not self.current_type:
            return None
        return next(self._cycles[self.current_type], None)

    def get_next_by_type(self, network_type: str) -> Optional[Proxy]:
        nt = network_type.upper()
        cycle = self._cycles.get(nt)
        return next(cycle, None) if cycle else None


# ------------------------
# Example usage:

if __name__ == "__main__":
    # 1) Load from API in one call:
    manager = ProxyManager.load_from_api(proxyProvider)

    # 2) Rotate through residential_static:
    manager.set_current_type("RESIDENTIAL_STATIC")
    p1 = manager.get_next_current()

    # 3) Toggle to mobile and get one:
    manager.toggle_type()
    p2 = manager.get_next_current()

    print(p1 and p1.connect_ip, p2 and p2.connect_ip)
