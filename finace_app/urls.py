"""finace_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from rest_framework import routers, serializers, viewsets
from rest_framework_simplejwt import views as jwt_views

from frontend.api.views import homepage_api_view


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('frontend.urls')),
    path('portfolio/', include('tickers.urls')),
    path('accounts/', include('accounts.urls')),
    path('settings/', include('settings.urls')),
    path('chat/', include('chat.urls')),
    path('backup/', include('backup_data.urls')),


    # api
    path('api/', homepage_api_view, name='api_homepage'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/tickers/', include('tickers.api.urls')),
    path('api/accounts/', include('accounts.api.urls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# 22