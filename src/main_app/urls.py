from django.urls import path
from src.presentation.views import index_view, list_files_view, download_multiple_files_view

urlpatterns = [
    path('', index_view, name='index'),
    path('list_files/', list_files_view, name='list_files'),
    path('download_multiple_files/', download_multiple_files_view, name='download_multiple_files'),
]
