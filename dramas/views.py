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
        - page: Page number (default: 1)
        - page_size: Items per page (default: 50)
        """
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 50))
        
        try:
            service = JoliboxService()
            result = service.get_dramas(page=page, page_size=page_size)
            return Response(result)
        except ValueError as e:
            return Response(
                {"code": "ERROR", "message": str(e), "data": []},
                status=status.HTTP_400_BAD_REQUEST
            )


class DramaDetailView(APIView):
    """API view to get drama details."""
    
    def get(self, request, drama_id):
        """Get details for a specific drama."""
        try:
            service = JoliboxService()
            result = service.get_drama_detail(drama_id)
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
