from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters import rest_framework

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from api.models import (Favorite, Ingredient, Recipie, RecipeIngredient,
                        ShoppingCart, Tag)
from api.serializers import (CreateRecipeSerializer, FavoriteRecipeSerializer,
                             IngredientSerializer, RecipeSerializer,
                             TagSerializer)
from api.filters import RecipeFilter, IngredientSearchFilter
from foodgram.constants import (ERROR_ALREADY_FAVORITED,
                                ERROR_ALREADY_IN_SHOPPINGCART,
                                ERROR_NO_RECIPE_FAVORITED)
from foodgram.permissions import OwnerOrReadOnly


class TagViewSet(viewsets.ModelViewSet):
    http_method_names = ('get',)
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class IngredientViewSet(viewsets.ModelViewSet):
    http_method_names = ('get',)
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('name',)


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

    def delete(self, request, *args, **kwargs):
        recipe = get_object_or_404(
            Recipie,
            pk=kwargs.get('pk')
        )
        remove_item = ShoppingCart.objects.filter(
            user=request.user,
            recipe=recipe
        ).first()
        if not remove_item:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        remove_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipie.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          OwnerOrReadOnly)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return super().get_serializer_class()

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

    @action(
        methods=('get',),
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        items = RecipeIngredient.objects.filter(
            recipe__cart_owners__user=request.user
        ).select_related('ingredient').values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(total_amount=Sum('amount'))
        content = ''
        for item in items:
            content += (
                f"{item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}\n"
            )
        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="ingredients_totals.txt"'
        )
        return response


@api_view(['GET'])
def short_link_redirect(request, short_link):
    recipe = get_object_or_404(Recipie, short_link=short_link)
    return redirect(request.build_absolute_uri(f'/recipes/{recipe.pk}'))


@api_view(['GET'])
def get_recipe_short_link(request, pk):
    recipe = get_object_or_404(Recipie, id=pk)
    short_link_url = request.build_absolute_uri(f'/s/{recipe.short_link}')
    return Response({'short-link': short_link_url})
