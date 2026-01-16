import requests
from typing import Optional, Dict, Any, List
from .models import JoliboxConfig


class JoliboxService:
    """Service class for interacting with Jolibox API."""
    
    BASE_URL = "https://api.jolibox.com"
    
    def __init__(self, config: Optional[JoliboxConfig] = None):
        self.config = config or JoliboxConfig.get_active_config()
        if not self.config:
            raise ValueError("No active Jolibox configuration found. Please add one via admin panel.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "Content-Type": "application/json",
            "X-Joli-Source": self.config.joli_source_token,
            "X-Device-Id": self.config.device_id,
        }
    
    def get_dramas(self, page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """Fetch list of dramas from Jolibox API."""
        url = f"{self.BASE_URL}/v2/drama/list"
        params = {
            "page": page,
            "pageSize": page_size,
        }
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": []}
    
    def get_episodes(self, drama_id: str) -> Dict[str, Any]:
        """Fetch episodes for a specific drama."""
        url = f"{self.BASE_URL}/v2/drama/{drama_id}/episodes"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": []}
    
    def get_drama_detail(self, drama_id: str) -> Dict[str, Any]:
        """Fetch details for a specific drama."""
        url = f"{self.BASE_URL}/v2/drama/{drama_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": None}
