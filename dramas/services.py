"""
NanoDrama API Service
Implements correct endpoints from nanodrama.ipynb
"""
import requests
from typing import Dict, Any, Optional, List
from .models import JoliboxConfig


class JoliboxService:
    """Service class for interacting with NanoDrama API."""
    
    BASE_URL = "https://www.nanodrama.com/api"
    
    def __init__(self, config: Optional[JoliboxConfig] = None):
        self.config = config or JoliboxConfig.get_config()
        if not self.config:
            raise ValueError("No Jolibox configuration found. Please add one via admin panel.")
    
    def _get_headers(self, drama_id: str = None, episode_num: int = None) -> Dict[str, str]:
        """Get request headers with authentication."""
        headers = {
            "accept": "application/json, text/plain, */*",
            "accept-language": "en",
            "referer": "https://www.nanodrama.com/",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "x-joli-accept-language": "en",
            "x-joli-source": self.config.joli_source_token,
            "x-os-type": "ANDROID",
            "x-runtime-type": "WEB",
        }
        
        # Add user agent for detail/unlock endpoints
        if drama_id:
            headers["x-user-agent"] = f"JoliboxMinidramaWeb (PC; undefined; 10; en) uuid/{self.config.device_id} adid/ version/2.4.0"
            if episode_num:
                headers["referer"] = f"https://www.nanodrama.com/drama/{drama_id}/{episode_num}"
        
        return headers
    
    def get_dramas(self, limit: int = 2000) -> Dict[str, Any]:
        """
        Fetch list of dramas from NanoDrama API.
        Endpoint: GET /dramas?tag=ALL&limit=2000&reqId=dramaflux
        """
        url = f"{self.BASE_URL}/dramas"
        params = {
            "tag": "ALL",
            "limit": limit,
            "reqId": "dramaflux",
        }
        
        try:
            response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            # API returns {"code": "SUCCESS", "data": [...]}
            if isinstance(result, dict) and "data" in result:
                return result
            # Or might return list directly
            elif isinstance(result, list):
                return {"code": "SUCCESS", "message": "success", "data": result}
            
            return result
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": []}
    
    def get_drama_detail(self, drama_id: str, episode_num: int = 1) -> Dict[str, Any]:
        """
        Get drama detail with specific episode.
        Endpoint: GET /dramas/{dramaId}/detail?episodeNum=1
        """
        url = f"{self.BASE_URL}/dramas/{drama_id}/detail"
        params = {"episodeNum": episode_num}
        
        try:
            response = requests.get(
                url, 
                headers=self._get_headers(drama_id, episode_num), 
                params=params, 
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            if isinstance(result, dict):
                if "data" in result:
                    return result
                else:
                    return {"code": "SUCCESS", "message": "success", "data": result}
            
            return {"code": "SUCCESS", "message": "success", "data": result}
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": None}
    
    def unlock_episode(self, drama_id: str, episode_num: int, session_id: str = "dramaflux") -> Dict[str, Any]:
        """
        Unlock an episode via ads/unlock endpoint.
        Endpoint: GET /dramas/ads/unlock?dramaId={id}&sessionId={session}&episodeNum={num}
        """
        url = f"{self.BASE_URL}/dramas/ads/unlock"
        params = {
            "dramaId": drama_id,
            "sessionId": session_id,
            "episodeNum": episode_num,
        }
        
        try:
            response = requests.get(
                url, 
                headers=self._get_headers(drama_id, episode_num), 
                params=params, 
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            return result if isinstance(result, dict) else {"code": "SUCCESS", "data": result}
        except requests.RequestException as e:
            return {"code": "ERROR", "message": str(e), "data": None}
    
    def get_episodes(self, drama_id: str) -> Dict[str, Any]:
        """
        Get episodes by fetching drama detail.
        Episodes are included in the detail response.
        """
        detail = self.get_drama_detail(drama_id, episode_num=1)
        
        if detail.get("code") == "SUCCESS" and detail.get("data"):
            data = detail["data"]
            # Extract episodes from detail response if available
            episodes = data.get("episodes", [])
            if not episodes and "episodeCount" in data:
                # Generate episode list if not provided
                episode_count = data.get("episodeCount", 0)
                episodes = [
                    {
                        "episodeId": f"{drama_id}-ep{i}",
                        "episodeNumber": i,
                        "title": f"Episode {i}",
                        "videoUrl": None
                    }
                    for i in range(1, episode_count + 1)
                ]
            return {"code": "SUCCESS", "message": "success", "data": episodes}
        
        return {"code": "ERROR", "message": "Failed to fetch episodes", "data": []}
