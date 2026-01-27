from rest_framework.views import APIView
from rest_framework.response import Response
from .models import AdConfig

class ActiveAdsView(APIView):
    def get(self, request):
        active_ads = AdConfig.objects.filter(is_active=True)
        
        data = {
            'HOME_FEED': [],
            'DRAMA_PLAYER': [],
            'BETWEEN_ROWS': []
        }
        
        for ad in active_ads:
            ad_data = {
                'id': ad.id,
                'code': ad.code,
                'sequence': ad.sequence,
                'type': ad.ad_type,
                'show_random': ad.show_random,
                'random_min': ad.random_min,
                'random_max': ad.random_max
            }
            if ad.ad_type in data:
                data[ad.ad_type].append(ad_data)
                
        return Response(data)
