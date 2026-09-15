from django.urls import path
from .features import status_manager, add_location, profile_manager, settings_manager

urlpatterns = [
    path('update-status/<int:haven_id>/', status_manager.toggle_status_view, name='update_status'),
    path('add-location/', add_location.add_location_view, name='add_location'),
    path('profile/', profile_manager.profile_view, name='profile'),
    path('settings/', settings_manager.settings_view, name='settings'),
]