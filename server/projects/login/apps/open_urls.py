"""
Login - root urls
"""
from django.urls import include, path

urlpatterns = [
    path('api/v1/login/', include('login.urls.v1')),
    path('api/v3/login/', include('login.urls.v3')),
]
