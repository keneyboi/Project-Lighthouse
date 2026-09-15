from django.urls import path
from . import views


urlpatterns = [
    path('update-status/<int:haven_id>/', views.toggle_status_view, name='update_status'),
    path('add-location/', views.add_location_view, name='add_location'),
]