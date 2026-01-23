from django.urls import path
from .views import ActiveAdsView

urlpatterns = [
    path('active/', ActiveAdsView.as_view(), name='active-ads'),
]
