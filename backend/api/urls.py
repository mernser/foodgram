from django.urls import include, path
from rest_framework import routers

from api.views import (IngredientViewSet, RecipeViewSet, ShoppingCartViewSet,
                       SubscriptionViewSet, TagViewSet, UserViewSet,
                       get_recipe_short_link)

router = routers.SimpleRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')
router.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/',
         UserViewSet.as_view({'get': 'subscriptions'})),
    path('users/me/avatar/',
         UserViewSet.as_view({'put': 'avatar_update',
                                     'delete': 'avatar_delete'})),
    path('users/<int:pk>/subscribe/',
         SubscriptionViewSet.as_view({'post': 'create',
                                      'delete': 'delete'})),
    path('recipes/<int:pk>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create',
                                      'delete': 'delete'})),
    path('recipes/<int:pk>/get-link/',
         get_recipe_short_link),
    path('', include('djoser.urls')),
    path('', include(router.urls)),
]
