from django.urls import path
from . import views, api_views

urlpatterns = [
    path('', views.show_landing, name='landing'),
    path('api/safe-havens/', api_views.safe_havens_geojson_api, name='api_safe_havens'),
    path('api/discreet-ping/', api_views.discreet_ping_api, name='api_discreet_ping'),
]
