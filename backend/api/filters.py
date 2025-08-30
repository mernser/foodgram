from django_filters import rest_framework
from rest_framework import filters

from recipes.models import Recipie


class RecipeFilter(rest_framework.FilterSet):
    is_favorited = rest_framework.BooleanFilter(
        method='filter_is_favorited'
    )
    is_in_shopping_cart = rest_framework.BooleanFilter(
        method='filter_is_in_shopping_cart'
    )
    author = rest_framework.NumberFilter(
        field_name='author__id'
    )
    tags = rest_framework.AllValuesMultipleFilter(
        field_name='tags__slug'
    )

    class Meta:
        model = Recipie
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def filter_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(favorites_by__user=self.request.user)
        return queryset

    def filter_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(cart_owners__user=self.request.user)
        return queryset


class IngredientSearchFilter(filters.SearchFilter):
    search_param = 'name'

    def get_search_fields(self, view, request):
        return ('name',)
