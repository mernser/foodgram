from django.urls import include, path
from rest_framework import routers

from api.views import (TagViewSet, IngredientViewSet,
                       RecipeViewSet, ShoppingCartViewSet,
                       get_recipe_short_link)
from users.views import (CustomUserViewSet,
                         CustomSubscriptionViewSet, SubscriptionViewSet)

router = routers.SimpleRouter()
router.register('tags', TagViewSet, basename='tags')
router.register('ingredients', IngredientViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
    path('users/subscriptions/',
         CustomSubscriptionViewSet.as_view({'get': 'subscriptions', })),
    path('users/me/avatar/',
         CustomUserViewSet.as_view({'put': 'avatar_update',
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
]
