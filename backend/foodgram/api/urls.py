from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views
from users.views import CustomUserViewSet
from api.views import TagViewSet, IngredientViewSet

router = routers.SimpleRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/',
         CustomUserViewSet.as_view({'put': 'avatar_update',
                                    'delete': 'avatar_delete'})),
]
