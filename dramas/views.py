from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import JoliboxService


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
