from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from foodgram.constants import (MAX_INGREDIENT_AMOUNT,
                                MAX_INGRIDIENT_NAME_LENGTH, MAX_LINK_LENGTH,
                                MAX_RECIPE_LENGTH_NAME, MAX_RECIPE_NAME_LENGTH,
                                MAX_STR_FIELD, MAX_TAG_LENGTH,
                                MAX_UNIT_NAME_LENGTH, MIN_INGREDIENT_AMOUNT,
                                MIN_RECIPE_LENGTH_NAME)
from recipes.services import generate_short_link

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=MAX_INGRIDIENT_NAME_LENGTH,
        unique=True)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_UNIT_NAME_LENGTH)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        constraints = (
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            ),
        )

    def __str__(self):
        return self.name[:MAX_STR_FIELD]


class Tag(models.Model):
    name = models.CharField(
        'название тега',
        max_length=MAX_TAG_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'slug тега',
        max_length=MAX_TAG_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name[:MAX_STR_FIELD]


class Recipie(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        help_text='Изображение блюда'
    )
    name = models.CharField(
        'Название',
        max_length=MAX_RECIPE_NAME_LENGTH,
        help_text='Наименование рецепта'
    )
    text = models.TextField(
        'Описание',
        help_text='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=(
            MinValueValidator(
                MIN_RECIPE_LENGTH_NAME,
                f'Значение не должно быть меньше {MIN_RECIPE_LENGTH_NAME}',
            ),
            MaxValueValidator(
                MAX_RECIPE_LENGTH_NAME,
                f'Значение не должно быть меньше {MAX_RECIPE_LENGTH_NAME}',
            )
        )
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги'
    )
    short_link = models.CharField(
        'Ссылка на рецепт',
        max_length=MAX_LINK_LENGTH,
        unique=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def save(self, *args, **kwargs):
        self.short_link = generate_short_link(self.short_link, self.id)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name[:MAX_STR_FIELD]


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients'
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(
                MIN_INGREDIENT_AMOUNT,
                f'Количество не может быть меньше {MIN_INGREDIENT_AMOUNT}'),
            MaxValueValidator(
                MAX_INGREDIENT_AMOUNT,
                f'Значение не должно быть больше {MAX_INGREDIENT_AMOUNT}',
            )
        )
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient_in_recipe'
            ),
        )

    def __str__(self):
        return (
            f'{self.ingredient.name[:MAX_STR_FIELD]} - '
            f'{str(self.amount)[:MAX_STR_FIELD]}'
        )


class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в избранном',
        related_name='favorites_by'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='У кого в избранном',
        related_name='favorite_recipes'
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранных'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_user_recipe_in_favorites'
            ),
        )

    def __str__(self):
        return (
            f'{self.user.username[:MAX_STR_FIELD]} - '
            f'{self.recipe.name[:MAX_STR_FIELD]}'
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Владелец корзины',
        related_name='shopping_list')
    recipe = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине',
        related_name='cart_owners')

    class Meta:
        verbose_name = 'Рецепт в корзине'
        verbose_name_plural = 'Рецепты в корзинах'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_owner_recipe_in_cart'
            ),
        )

    def __str__(self):
        return (
            f'{self.recipe.name[:MAX_STR_FIELD]} '
            f'в корзине у {self.user.username}'
        )
