from api.models import Tag, Ingredient, Recipie, Favorite, ShoppingCart
from api.serializers import (TagSerializer,
                             IngredientSerializer, RecipeSerializer,
                             FavoriteRecipeSerializer
                             )
from django.shortcuts import get_object_or_404
from foodgram.constants import (ERROR_ALREADY_FAVORITED,
                                ERROR_NO_RECIPE_FAVORITED,
                                ERROR_ALREADY_IN_SHOPPINGCART,)
from rest_framework import permissions, viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class ShoppingCartViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteRecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request, *args, **kwargs):
        recipe = get_object_or_404(Recipie, pk=kwargs.get('pk'))
        if ShoppingCart.objects.filter(
                user=request.user,
                recipe=recipe
        ).exists():
            return Response(
                {'detail': ERROR_ALREADY_IN_SHOPPINGCART},
                status=status.HTTP_400_BAD_REQUEST
            )
        ShoppingCart.objects.create(
            user=request.user,
            recipe=recipe
        )
        serializer = FavoriteRecipeSerializer(
            recipe,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipie,
            pk=kwargs.get('pk')
        )
        remove_item = get_object_or_404(
            ShoppingCart,
            user=request.user,
            recipe=recipe)
        remove_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipie.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        params = self.request.query_params
        if user.is_authenticated:
            is_favorited = params.get('is_favorited')
            if is_favorited and is_favorited == '1':
                queryset = queryset.filter(
                    id__in=Favorite.objects.filter(user=user).values('recipe')
                )
            is_in_shopping_cart = params.get('is_in_shopping_cart')
            if is_in_shopping_cart and is_in_shopping_cart == '1':
                queryset = queryset.filter(
                    id__in=ShoppingCart.objects
                    .filter(user=user).values('recipe')
                )
        if author_id := params.get('author'):
            queryset = queryset.filter(author=author_id)
        if tags := params.getlist('tags'):
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        return queryset

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipie, pk=pk)
        user = request.user
        favorite = Favorite.objects.filter(user=user, recipe=recipe)

        if request.method == 'POST':
            if favorite:
                return Response(
                    {'errors': ERROR_ALREADY_FAVORITED},
                    status=status.HTTP_400_BAD_REQUEST
                )
            Favorite.objects.create(user=user, recipe=recipe)
            serializer = FavoriteRecipeSerializer(
                recipe,
                context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        elif request.method == 'DELETE':
            if not favorite:
                return Response(
                    {'errors': ERROR_NO_RECIPE_FAVORITED},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
