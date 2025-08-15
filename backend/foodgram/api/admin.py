from django.contrib import admin
from api.models import Recipie, Tag, Ingredient, Favorite, ShoppingCart, RecipeIngredient


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipie)
class RecipieAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author', 'text', 'cooking_time', 'display_tags', 'short_link')
    list_filter = ('author', 'tags', 'pub_date')
    list_display_links = ('pk', 'name')  # Какие поля должны быть ссылками
    inlines = (RecipeIngredientInline,)  # Добавляем инлайн с ингредиентами
    readonly_fields = ('pub_date', 'short_link')
    empty_value_display = '-'

    @admin.display(description='Tags')
    def display_tags(self, obj):
        return ", ".join([tag.name for tag in obj.tags.all()])


# @admin.register(RecipeIngredient)
# class RecipeIngredient(admin.ModelAdmin):
#     list_display = ('pk', 'name',)

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
    list_display = ('pk', 'name', 'slug')
    # search_fields = ('follower', 'subscribed_to')
    # list_filter = ('follower', 'subscribed_to')
    # empty_value_display = '-'
