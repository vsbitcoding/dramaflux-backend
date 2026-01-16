from django.urls import path
from .views import DramaListView, DramaDetailView, EpisodeListView, UnlockEpisodeView

urlpatterns = [
    path('dramas/', DramaListView.as_view(), name='drama-list'),
    path('dramas/<str:drama_id>/', DramaDetailView.as_view(), name='drama-detail'),
    path('dramas/<str:drama_id>/episodes/', EpisodeListView.as_view(), name='episode-list'),
    path('dramas/<str:drama_id>/unlock/<int:episode_num>/', UnlockEpisodeView.as_view(), name='unlock-episode'),
]
