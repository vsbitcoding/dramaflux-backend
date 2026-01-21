from django.urls import path
from . import views

urlpatterns = [
    # Original API endpoints (call NanoDrama API directly)
    path('dramas/', views.DramaListView.as_view(), name='drama-list'),
    path('dramas/<str:drama_id>/', views.DramaDetailView.as_view(), name='drama-detail'),
    path('dramas/<str:drama_id>/episodes/', views.EpisodeListView.as_view(), name='episode-list'),
    path('dramas/<str:drama_id>/unlock/<int:episode_num>/', views.UnlockEpisodeView.as_view(), name='unlock-episode'),
    
    # Proxy endpoints for CORS handling
    path('proxy/m3u8/', views.ProxyM3U8View.as_view(), name='proxy-m3u8'),
    path('proxy/ts/', views.ProxyStreamView.as_view(), name='proxy-ts'),
    
    # Cached endpoints (serve from local database - no API calls)
    path('cached/dramas/', views.CachedDramaListView.as_view(), name='cached-drama-list'),
    path('cached/dramas/<str:drama_id>/', views.CachedDramaDetailView.as_view(), name='cached-drama-detail'),
    path('cached/dramas/<str:drama_id>/episodes/<int:episode_num>/play/', views.CachedEpisodePlayView.as_view(), name='cached-episode-play'),
]
