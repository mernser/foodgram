from django.urls import include, path
from rest_framework import routers
from users.views import CustomUserViewSet
from api.views import TagViewSet, IngredientViewSet, RecipeViewSet

router = routers.SimpleRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
# 
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/me/avatar/',
         CustomUserViewSet.as_view({'put': 'avatar_update',
                                    'delete': 'avatar_delete'})),
]
