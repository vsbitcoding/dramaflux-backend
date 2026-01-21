
import requests
from django.http import StreamingHttpResponse, HttpResponse
from urllib.parse import quote, unquote, urljoin
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import JoliboxService
from .models import Drama, Episode

class ProxyM3U8View(APIView):
    """
    Proxy for M3U8 playlists to handle CORS and rewrites.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        target_url = request.query_params.get('url')
        if not target_url:
            return Response({"error": "Missing url parameter"}, status=400)
        
        # Decode if it was double encoded or just use as is
        # target_url = unquote(target_url) 

        try:
            # Fake headers to look like a browser
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://www.nanodrama.com/",
                "Origin": "https://www.nanodrama.com"
            }
            
            resp = requests.get(target_url, headers=headers, allow_redirects=True)
            resp.raise_for_status()
            
            base_url = resp.url
            content = resp.text
            new_lines = []
            
            # Use root-relative paths to avoid Host header/Port stripping issues
            # This ensures the browser resolves valid URLs against the current page origin
            proxy_m3u8 = "/api/proxy/m3u8/?url="
            proxy_ts = "/api/proxy/ts/?url="

            
            for line in content.splitlines():
                if line.strip().startswith('#') or not line.strip():
                    new_lines.append(line)
                    continue
                
                # It's a URL
                original_segment_url = line.strip()
                absolute_url = urljoin(base_url, original_segment_url)
                encoded_url = quote(absolute_url)
                
                # Check if it's a playlist or a segment
                if '.m3u8' in absolute_url or 'm3u8' in absolute_url.split('?')[0]:
                    new_lines.append(f"{proxy_m3u8}{encoded_url}")
                else:
                    new_lines.append(f"{proxy_ts}{encoded_url}")
            
            new_content = "\n".join(new_lines)
            
            return HttpResponse(
                new_content,
                content_type="application/vnd.apple.mpegurl",
                headers={"Access-Control-Allow-Origin": "*"}
            )
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)

class ProxyStreamView(APIView):
    """
    Proxy for video segments (TS) or other binary content.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        target_url = request.query_params.get('url')
        if not target_url:
            return Response({"error": "Missing url parameter"}, status=400)
            
        try:
             # Fake headers
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Referer": "https://www.nanodrama.com/",
            }
            
            resp = requests.get(target_url, headers=headers, stream=True, timeout=10)
            resp.raise_for_status()
            
            response = StreamingHttpResponse(
                resp.iter_content(chunk_size=8192),
                content_type=resp.headers.get('Content-Type', 'application/octet-stream')
            )
            response['Access-Control-Allow-Origin'] = '*'
            return response
            
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class DramaListView(APIView):
    """API view to list all available dramas."""
    
    def get(self, request):
        """
        Get list of dramas.
        
        Query params:
        - limit: Max items to return (default: 2000)
        """
        limit = int(request.query_params.get('limit', 2000))
        
        try:
            service = JoliboxService()
            result = service.get_dramas(limit=limit)
            return Response(result)
        except ValueError as e:
            return Response(
                {"code": "ERROR", "message": str(e), "data": []},
                status=status.HTTP_400_BAD_REQUEST
            )


class DramaDetailView(APIView):
    """API view to get drama details."""
    
    def get(self, request, drama_id):
        """
        Get details for a specific drama.
        
        Query params:
        - episode_num: Episode number to get details for (default: 1)
        """
        episode_num = int(request.query_params.get('episode_num', 1))
        
        try:
            service = JoliboxService()
            result = service.get_drama_detail(drama_id, episode_num=episode_num)
            return Response(result)
        except ValueError as e:
            return Response(
                {"code": "ERROR", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )


class EpisodeListView(APIView):
    """API view to list episodes for a drama."""
    
    def get(self, request, drama_id):
        """Get episodes for a specific drama."""
        try:
            service = JoliboxService()
            result = service.get_episodes(drama_id)
            return Response(result)
        except ValueError as e:
            return Response(
                {"code": "ERROR", "message": str(e), "data": []},
                status=status.HTTP_400_BAD_REQUEST
            )


class UnlockEpisodeView(APIView):
    """API view to unlock an episode."""
    
    def get(self, request, drama_id, episode_num):
        """
        Unlock a specific episode.
        
        Query params:
        - session_id: Session identifier (default: auto-generated)
        """
        session_id = request.query_params.get('session_id', 'dramaflux')
        
        try:
            service = JoliboxService()
            result = service.unlock_episode(drama_id, int(episode_num), session_id)
            return Response(result)
        except ValueError as e:
            return Response(
                {"code": "ERROR", "message": str(e), "data": None},
                status=status.HTTP_400_BAD_REQUEST
            )


# ============================================================================
# CACHED DRAMA VIEWS - Serve from local database (no API calls)
# ============================================================================

class CachedDramaListView(APIView):
    """API view to list all cached dramas from local database."""
    
    def get(self, request):
        """
        Get list of cached dramas.
        
        Query params:
        - limit: Max items to return (default: 100)
        - offset: Pagination offset (default: 0)
        - category: Filter by category
        - search: Search by name
        """
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        category = request.query_params.get('category')
        search = request.query_params.get('search')
        
        queryset = Drama.objects.filter(is_active=True)
        
        if category:
            queryset = queryset.filter(categories__contains=[category])
        
        if search:
            queryset = queryset.filter(name__icontains=search)
        
        total = queryset.count()
        dramas = queryset[offset:offset + limit]
        
        data = []
        for drama in dramas:
            data.append({
                "dramaId": drama.drama_id,
                "name": drama.name,
                "description": drama.description,
                "cover": drama.cover_url,
                "logo": drama.logo_url,
                "episodeCount": drama.episode_count,
                "orientation": drama.orientation,
                "categories": drama.categories,
                "views": drama.views,
                "syncedEpisodes": drama.episodes.filter(is_unlocked=True).count(),
            })
        
        return Response({
            "code": "SUCCESS",
            "message": "success",
            "data": data,
            "total": total,
            "limit": limit,
            "offset": offset,
        })


class CachedDramaDetailView(APIView):
    """API view to get cached drama details from local database."""
    
    def get(self, request, drama_id):
        """Get details for a specific cached drama."""
        try:
            drama = Drama.objects.get(drama_id=drama_id)
        except Drama.DoesNotExist:
            return Response(
                {"code": "ERROR", "message": "Drama not found in cache", "data": None},
                status=status.HTTP_404_NOT_FOUND
            )
        
        episodes = []
        for ep in drama.episodes.all():
            episodes.append({
                "episodeNumber": ep.episode_number,
                "videoUrl": ep.video_url,
                "isUnlocked": ep.is_unlocked,
                "lastSynced": ep.last_synced.isoformat() if ep.last_synced else None,
            })
        
        return Response({
            "code": "SUCCESS",
            "message": "success",
            "data": {
                "dramaId": drama.drama_id,
                "name": drama.name,
                "description": drama.description,
                "cover": drama.cover_url,
                "logo": drama.logo_url,
                "episodeCount": drama.episode_count,
                "orientation": drama.orientation,
                "categories": drama.categories,
                "views": drama.views,
                "lastSynced": drama.last_synced.isoformat() if drama.last_synced else None,
                "episodes": episodes,
            }
        })


class CachedEpisodePlayView(APIView):
    """API view to get cached episode video URL."""
    
    def get(self, request, drama_id, episode_num):
        """
        Get video URL for a specific episode from cache.
        
        Returns proxied m3u8 URL ready to play.
        """
        try:
            episode = Episode.objects.get(
                drama__drama_id=drama_id, 
                episode_number=episode_num
            )
        except Episode.DoesNotExist:
            return Response(
                {"code": "ERROR", "message": "Episode not found in cache", "data": None},
                status=status.HTTP_404_NOT_FOUND
            )
        
        if not episode.is_unlocked or not episode.video_url:
            return Response({
                "code": "ERROR",
                "message": "Episode not unlocked or video URL not available",
                "data": {
                    "isUnlocked": episode.is_unlocked,
                    "error": episode.unlock_error,
                }
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Build proxied URL for CORS handling
        # Use root-relative path to avoid Host header issues
        proxied_url = f"/api/proxy/m3u8/?url={quote(episode.video_url)}"

        
        return Response({
            "code": "SUCCESS",
            "message": "success",
            "data": {
                "dramaId": drama_id,
                "dramaName": episode.drama.name,
                "episodeNumber": episode.episode_number,
                "videoUrl": episode.video_url,
                "proxiedUrl": proxied_url,
                "lastSynced": episode.last_synced.isoformat() if episode.last_synced else None,
            }
        })

