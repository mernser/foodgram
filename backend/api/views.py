from io import BytesIO

from django.contrib.auth import get_user_model
from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django_filters import rest_framework
from djoser.views import UserViewSet as BaseUserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import (IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientSearchFilter, RecipeFilter
from api.pagination import PageNumberPagination
from api.permissions import OwnerOrReadOnly
from api.serializers import (AvatarUpdateSerializer, CreateRecipeSerializer,
                             FavoriteCreateSerializer, IngredientSerializer,
                             RecipeSerializer, ShoppingCartCreateSerializer,
                             SubscriptionCreateSerializer, TagSerializer,
                             UserProfileListRecipesSerilizer,
                             UserProfileSerializer)
from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipie,
                            ShoppingCart, Tag)
from users.models import Subscription

User = get_user_model()


class UserViewSet(BaseUserViewSet):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    pagination_class = PageNumberPagination

    @action(detail=False,
            url_path='me',
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserProfileSerializer(
            request.user,
            context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False,
            methods=('put',),
            url_path='me/avatar')
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

    @avatar_update.mapping.delete
    def avatar_delete(self, request):
        request.user.avatar.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False,
            methods=('get',),
            permission_classes=(IsAuthenticated,),
            url_path='subscriptions')
    def subscriptions(self, request):
        subscriptions = User.objects.filter(
            author_subscribers__user=request.user
        ).annotate(
            recipes_count=Count('recipes')
        ).order_by('-date_joined')
        page = self.paginate_queryset(subscriptions)
        serializer = UserProfileListRecipesSerilizer(
            page,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)

    @action(detail=True,
            methods=('post',),
            permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        user_to_subscribe = get_object_or_404(User, pk=id)
        serializer = SubscriptionCreateSerializer(
            data={'author': user_to_subscribe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @subscribe.mapping.delete
    def unsubscribe(self, request, id=None):
        user_to_unsubscribe = get_object_or_404(User, pk=id)
        deleted_count, _ = Subscription.objects.filter(
            user=request.user,
            author=user_to_unsubscribe
        ).delete()
        return Response(
            status=(
                status.HTTP_204_NO_CONTENT
                if deleted_count
                else status.HTTP_400_BAD_REQUEST
            )
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (IngredientSearchFilter,)
    search_fields = ('name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipie.objects.select_related('author').prefetch_related(
        'tags',
        'recipe_ingredients__ingredient'
    ).all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,
                          OwnerOrReadOnly)
    filter_backends = (rest_framework.DjangoFilterBackend,)
    filterset_class = RecipeFilter

    @staticmethod
    def generate_shopping_list_content(items):
        content = ''
        for item in items:
            content += (
                f'{item["ingredient__name"]} '
                f'({item["ingredient__measurement_unit"]}) - '
                f'{item["total_amount"]}\n'
            )
        return content

    def get_serializer_class(self):
        if self.action in ('create', 'update', 'partial_update'):
            return CreateRecipeSerializer
        return super().get_serializer_class()

    def _create_object(self, serializer_class, pk):
        recipe = get_object_or_404(Recipie, pk=pk)
        data = {
            'user': self.request.user.id,
            'recipe': recipe.id
        }
        serializer = serializer_class(
            data=data,
            context={'request': self.request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _delete_object(self, model, pk):
        recipe = get_object_or_404(Recipie, pk=pk)
        deleted_count, _ = model.objects.filter(
            user=self.request.user,
            recipe=recipe
        ).delete()
        return Response(
            status=(
                status.HTTP_204_NO_CONTENT
                if deleted_count
                else status.HTTP_400_BAD_REQUEST
            )
        )

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='favorite'
    )
    def favorite(self, request, pk=None):
        return self._create_object(FavoriteCreateSerializer, pk)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        return self._delete_object(Favorite, pk)

    @action(
        detail=True,
        methods=('post',),
        permission_classes=(permissions.IsAuthenticated,),
        url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        return self._create_object(ShoppingCartCreateSerializer, pk)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        return self._delete_object(ShoppingCart, pk)

    @action(
        methods=('get',),
        detail=False,
        url_path='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        items = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=request.user
        ).select_related('ingredient').values(
            'ingredient__name',
            'ingredient__measurement_unit',
        ).annotate(total_amount=Sum('amount'))
        file_buffer = BytesIO(
            self.generate_shopping_list_content(items).encode('utf-8')
        )
        response = FileResponse(
            file_buffer,
            content_type='text/plain',
            as_attachment=True,
            filename='ingredients_totals.txt'
        )
        response['Content-Disposition'] = (
            'attachment; filename="ingredients_totals.txt"'
        )
        return response

    @action(
        methods=('get',),
        detail=True,
        url_path='get-link',
    )
    def get_recipe_short_link(self, request, pk):
        recipe = get_object_or_404(Recipie, id=pk)
        short_link_path = reverse('short_link_redirect',
                                  kwargs={'short_link': recipe.short_link})
        short_link_url = request.build_absolute_uri(short_link_path)
        return Response({'short-link': short_link_url})
