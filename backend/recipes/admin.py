from django.contrib import admin
from django.db.models import Count
from django.utils.safestring import mark_safe

from recipes.models import (Favorite, Ingredient, RecipeIngredient, Recipie,
                            ShoppingCart, Tag)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Recipie)
class RecipieAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_ingredients',
                    'get_tags', 'get_favorites_count')
    search_fields = ('name', 'username')
    list_filter = ('tags',)
    inlines = (RecipeIngredientInline,)
    ordering = ('-pub_date',)
    readonly_fields = ('get_favorites_count', 'short_link',
                       'pub_date', 'get_image')

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            favorites_count=Count('favorite')
        )

    @admin.display(description='Кол-во в избранном')
    def get_favorites_count(self, obj):
        return obj.favorites_count

    @admin.display(description='Изображение рецепта')
    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="80" height="60">')

    @admin.display(description='Ингредиенты')
    def get_ingredients(self, obj):
        ingredients = (
            f'{ingredient.ingredient.name}'
            for ingredient in obj.recipe_ingredients.all()
        )
        return ', '.join(ingredients) if ingredients else '-'

    @admin.display(description='Теги')
    def get_tags(self, obj):
        tags = (tag.name for tag in getattr(obj, 'tags').all())
        return ', '.join(tags) if tags else '-'


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
