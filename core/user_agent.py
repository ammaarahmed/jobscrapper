from dataclasses import dataclass
from typing import List, Optional
from itertools import cycle
import random

@dataclass
class UserAgent:
    """Represents a single user agent with metadata."""
    string: str
    browser: str
    os: str
    device_type: str = "desktop"  # desktop, mobile, tablet

class UserAgentManager:
    """Manages a pool of user agents with rotation capability."""
    
    def __init__(self, user_agents: Optional[List[UserAgent]] = None) -> None:
        """
        Initialize the user agent manager.
        
        Args:
            user_agents: Optional list of UserAgent objects. If None, uses default list.
        """
        self.user_agents = user_agents or self._get_default_user_agents()
        self.user_agent_pool = cycle(self.user_agents)
    
    def _get_default_user_agents(self) -> List[UserAgent]:
        """Get a list of default user agents."""
        return [
            UserAgent(
                string="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                browser="Chrome",
                os="Windows",
                device_type="desktop"
            ),
            UserAgent(
                string="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                browser="Chrome",
                os="MacOS",
                device_type="desktop"
            ),
            UserAgent(
                string="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                browser="Firefox",
                os="Windows",
                device_type="desktop"
            ),
            UserAgent(
                string="Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
                browser="Safari",
                os="iOS",
                device_type="mobile"
            ),
            UserAgent(
                string="Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
                browser="Chrome",
                os="Android",
                device_type="mobile"
            )
        ]
    
    def get_next_user_agent(self) -> str:
        """
        Get the next user agent string in rotation.
        
        Returns:
            str: The next user agent string
        """
        return next(self.user_agent_pool).string
    
    def get_random_user_agent(self) -> str:
        """
        Get a random user agent string.
        
        Returns:
            str: A random user agent string
        """
        return random.choice(self.user_agents).string
    
    def get_user_agent_by_type(self, device_type: str) -> Optional[str]:
        """
        Get a random user agent string for a specific device type.
        
        Args:
            device_type: The device type (desktop, mobile, tablet)
            
        Returns:
            Optional[str]: A user agent string or None if no matching user agents
        """
        matching = [ua for ua in self.user_agents if ua.device_type == device_type]
        return random.choice(matching).string if matching else None
    
    def add_user_agent(self, user_agent: UserAgent) -> None:
        """
        Add a new user agent to the pool.
        
        Args:
            user_agent: The UserAgent object to add
        """
        self.user_agents.append(user_agent)
        self.user_agent_pool = cycle(self.user_agents)

# Example usage:
if __name__ == "__main__":
    ua_manager = UserAgentManager()
    
    # Get next in rotation
    print("Next user agent:", ua_manager.get_next_user_agent())
    
    # Get random
    print("Random user agent:", ua_manager.get_random_user_agent())
    
    # Get mobile-specific
    print("Mobile user agent:", ua_manager.get_user_agent_by_type("mobile"))
