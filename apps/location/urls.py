from django.urls import path
from . import views

urlpatterns = [
    path('', views.manage_locations_view, name='manage_locations'),
    path('create/', views.create_location_view, name='create_location'),
    path('edit/<int:haven_id>/', views.edit_location_view, name='edit_location'),
    path('delete/<int:haven_id>/', views.delete_location_view, name='delete_location'),
    path('update-status/<int:haven_id>/', views.toggle_status_view, name='update_status'),
    path('add-location/', views.add_location_view, name='add_location'),
]