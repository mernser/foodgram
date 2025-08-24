from django.contrib import admin
from api.models import (Recipie, Tag, Ingredient,
                        Favorite, ShoppingCart, RecipeIngredient)
from django.db.models import Count


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipie)
class RecipieAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name', 'username')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)
    ordering = ('-pub_date',)
    readonly_fields = ('get_favorites_count', 'short_link', 'pub_date')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=Count('favorites_by')
        )

    def get_favorites_count(self, obj):
        return obj.favorites_count
    get_favorites_count.short_description = 'Количество добавлений в избранное'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    ordering = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount')
    list_filter = ('recipe', 'ingredient')
    search_fields = ('recipe__name', 'ingredient__name')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', )
    list_filter = ('name', 'measurement_unit')
    search_fields = ('name',)
