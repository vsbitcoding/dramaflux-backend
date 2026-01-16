import requests
from typing import Optional, Dict, Any
from .models import JoliboxConfig


class JoliboxService:
    """Service class for interacting with NanoDrama/Jolibox API."""
    
    BASE_URL = "https://www.nanodrama.com/api"
    
    def __init__(self, config: Optional[JoliboxConfig] = None):
        self.config = config or JoliboxConfig.get_active_config()
        if not self.config:
            raise ValueError("No active Jolibox configuration found. Please add one via admin panel.")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication."""
        return {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en",
            "referer": "https://www.nanodrama.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "x-joli-accept-language": "en",
            "x-joli-source": self.config.joli_source_token,
            "x-os-type": "ANDROID",
            "x-runtime-type": "WEB",
        }
    
    def get_dramas(self, page: int = 1, page_size: int = 100) -> Dict[str, Any]:
        """Fetch list of dramas from NanoDrama API."""
        url = f"{self.BASE_URL}/dramas"
        params = {
            "tag": "ALL",
            "limit": page_size,
            "reqId": "dramaflux",
        }
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            # Wrap in standard format if needed
            if isinstance(result, list):
                return {"code": "SUCCESS", "message": "success", "data": result}
            return result
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": []}
    
    def get_episodes(self, drama_id: str) -> Dict[str, Any]:
        """Fetch episodes for a specific drama."""
        url = f"{self.BASE_URL}/drama/{drama_id}/episodes"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            result = response.json()
            if isinstance(result, list):
                return {"code": "SUCCESS", "message": "success", "data": result}
            return result
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": []}
    
    def get_drama_detail(self, drama_id: str) -> Dict[str, Any]:
        """Fetch details for a specific drama."""
        url = f"{self.BASE_URL}/drama/{drama_id}"
        
        try:
            response = requests.get(url, headers=self._get_headers(), timeout=30)
            response.raise_for_status()
            result = response.json()
            return {"code": "SUCCESS", "message": "success", "data": result}
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": None}
