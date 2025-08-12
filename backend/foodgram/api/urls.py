from django.urls import include, path
from rest_framework import routers
from users.views import (CustomUserViewSet,
                         CustomSubscriptionViewSet, SubscriptionViewSet)
from api.views import (TagViewSet, IngredientViewSet,
                       RecipeViewSet, ShoppingCartViewSet)

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
                                      'delete': 'destroy'})),
    path('recipes/<int:pk>/shopping_cart/',
         ShoppingCartViewSet.as_view({'post': 'create',
                                      'delete': 'destroy'})),
    path('', include('djoser.urls')),
]
