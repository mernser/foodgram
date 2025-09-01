from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters import rest_framework
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import PageNumberPagination
from api.permissions import OwnerOrReadOnly
from api.serializers import (AvatarUpdateSerializer, CreateRecipeSerializer,
                             FavoriteRecipeSerializer, IngredientSerializer,
                             RecipeSerializer, TagSerializer,
                             UserProfileListRecipesSerilizer)
from foodgram.constants import (ERROR_ALREADY_FAVORITED,
                                ERROR_ALREADY_IN_SHOPPINGCART,
                                ERROR_ALREADY_SUBSCRIBED,
                                ERROR_NO_RECIPE_FAVORITED,
                                ERROR_SELF_SUBSCRIPTION)
from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipie,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class UserViewSet(BaseUserViewSet):
    permission_classes = (IsAuthenticated, OwnerOrReadOnly,)
    pagination_class = PageNumberPagination

    @action(detail=True,
            methods=('delete',),
            url_path='avatar')
    def avatar_delete(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=('put',),
            url_path='avatar')
    def avatar_update(self, request):
        serializer = AvatarUpdateSerializer(
            request.user,
            data=request.data,
            partial=False,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False,
            methods=('get',),
            permission_classes=(IsAuthenticated,),
            url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            subscribed_to__follower=request.user
        ).annotate(recipes_count=Count('recipes'))
        page = self.paginate_queryset(subscriptions)
        serializer = UserProfileListRecipesSerilizer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


class SubscriptionViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    pagination_class = PageNumberPagination

    def create(self, request, *args, **kwargs):
        recipes_limit = request.query_params.get('recipes_limit', None)
        user_to_subscribe = get_object_or_404(User, pk=kwargs.get('pk'))
        if Subscription.objects.filter(
                follower=request.user,
                subscribed_to=user_to_subscribe
        ).exists():
            return Response(
                {'detail': ERROR_ALREADY_SUBSCRIBED},
                status=status.HTTP_400_BAD_REQUEST
            )
        if user_to_subscribe == request.user:
            return Response(
                {'detail': ERROR_SELF_SUBSCRIPTION},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(follower=request.user,
                                    subscribed_to=user_to_subscribe)
        
        user_to_subscribe = User.objects.filter(pk=user_to_subscribe.pk).annotate(
            recipes_count=Count('recipes')
        ).first()
        serializer = UserProfileListRecipesSerilizer(
            user_to_subscribe,
            context={'request': request,
                     'recipes_limit': recipes_limit}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        user_to_unsubscribe = get_object_or_404(User, pk=kwargs.get('pk'))
        if not user_to_unsubscribe:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription = Subscription.objects.filter(
            follower=request.user,
            subscribed_to=user_to_unsubscribe
        ).first()
        if not subscription:
            return Response(
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
