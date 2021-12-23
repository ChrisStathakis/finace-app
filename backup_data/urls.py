from django.urls import path

from .views import BackupHomepageView, download_data_view


app_name = 'backup'

urlpatterns = [
    path('homepage/', BackupHomepageView.as_view(), name='homepage'),
    path('download/<slug:slug>/', download_data_view, name='download')
]
