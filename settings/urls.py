from django.urls import path


from .views import homepage_view

app_name = 'setting'

urlpatterns = [
    path('', homepage_view, name='homepage'),
]