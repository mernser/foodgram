from django.contrib import admin
from api.models import Recipie, Tag, Ingredient, Favorite, ShoppingCart


@admin.register(Recipie)
class RecipieAdmin(admin.ModelAdmin):
    # list_display = ('pk', 'email', 'username', 'first_name', 'last_name')
    list_display = ('pk', 'name', 'author', 'text', 'cooking_time',)
    # search_fields = ('username', 'email', 'first_name', 'last_name')
    # list_filter = ('username', 'email')
    # empty_value_display = '-'

@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    # list_display = ('pk', 'email', 'username', 'first_name', 'last_name')
    list_display = ('pk', 'user', 'recipe')
    # search_fields = ('username', 'email', 'first_name', 'last_name')
    # list_filter = ('username', 'email')
    # empty_value_display = '-'

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    pass
    # list_display = ('pk', 'email', 'username', 'first_name', 'last_name')
    # search_fields = ('username', 'email', 'first_name', 'last_name')
    # list_filter = ('username', 'email')
    # empty_value_display = '-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    pass
    # list_display = ('pk', 'email', 'username', 'first_name', 'last_name')
    # search_fields = ('username', 'email', 'first_name', 'last_name')
    # list_filter = ('username', 'email')
    # empty_value_display = '-'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    pass
    # list_display = ('pk', 'follower', 'subscribed_to')
    # search_fields = ('follower', 'subscribed_to')
    # list_filter = ('follower', 'subscribed_to')
    # empty_value_display = '-'
