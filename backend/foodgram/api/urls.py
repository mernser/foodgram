from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views
from users.views import CustomUserViewSet

# router = routers.DefaultRouter()

urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/', CustomUserViewSet.as_view({'put': 'avatar'})),
]
