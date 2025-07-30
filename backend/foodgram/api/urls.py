from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views
from users.views import CustomUserViewSet
from api.views import TagViewSet

router = routers.SimpleRouter()
router.register('tags', TagViewSet, basename='tags')

urlpatterns = [
    path('', include('djoser.urls')),
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/',
         CustomUserViewSet.as_view({'put': 'avatar_update',
                                    'delete': 'avatar_delete'})),
]
