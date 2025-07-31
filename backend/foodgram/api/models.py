import hashlib

from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram.constants import (MAX_TAG_LENGTH,
                                MAX_INGRIDIENT_NAME_LENGTH,
                                MAX_UNIT_NAME_LENGTH,
                                MAX_RECIPE_NAME_LENGTH,
                                MIN_RECIPE_LENGTH_NAME,
                                MAX_LINK_LENGTH,
                                MAX_HASH_LENGTH)

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=MAX_INGRIDIENT_NAME_LENGTH,
        unique=True,
        blank=False,
        null=False)
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_UNIT_NAME_LENGTH,
        blank=False,
        null=False)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


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
        return f'{self.name}'


class Recipie(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        blank=False,
        help_text='Изображение блюда'
    )
    name = models.CharField(
        'Название',
        max_length=MAX_RECIPE_NAME_LENGTH,
        blank=False,
        help_text='Наименование рецепта'
    )
    text = models.TextField(
        'Описание',
        blank=False,
        help_text='Описание рецепта',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=(
            MinValueValidator(
                MIN_RECIPE_LENGTH_NAME,
                f'Значение не должно быть меньше {MIN_RECIPE_LENGTH_NAME}',
            ),),
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
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    short_link = models.CharField(
        'Уникальный хеш для генерации ссылки',
        max_length=MAX_LINK_LENGTH,
        blank=True,
        editable=False,
        unique=True
    )

    def save(self, *args, **kwargs):
        # Если это новый объект и short_link ещё не установлен
        if not self.pk and not self.short_link:
            # Сначала сохраняем, чтобы получить pub_date
            super().save(*args, **kwargs)
            # Теперь генерируем short_link
            self.short_link = (
                hashlib.sha256(
                    f'{self.pub_date.isoformat()}{self.author.id}'
                    .encode('utf-8')).hexdigest())[:MAX_HASH_LENGTH]
            # Сохраняем только short_link
            super().save(update_fields=['short_link'])
        else:
            super().save(*args, **kwargs)

    class Meta:
        ordering = ('pub_date',)
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients'  # Уже правильно
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients'  # Добавлено для симметрии
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=(
            MinValueValidator(1, 'Количество не может быть меньше 1'),
        )
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_ingredient_in_recipe'  # Теперь имя уникально
            )
        ]

    def __str__(self):
        return f'{self.ingredient.name} - {self.amount}'

class Favorite(models.Model):
    recipe = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в избранном',
        related_name='favorites'  # Изменено related_name
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='У кого в избранном',
        related_name='favorites'  # Добавлено related_name
    )

    class Meta:
        verbose_name = 'Рецепт в избранном'
        verbose_name_plural = 'Рецепты в избранных'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_in_favorites'  # Уникальное имя ограничения
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='shopping_carts'  # Лучше использовать множественное число
    )
    recipe = models.ForeignKey(
        Recipie,
        on_delete=models.CASCADE,
        verbose_name='Рецепт в корзине',
        related_name='in_shopping_carts'  # Лучше использовать множественное число
    )
    added_at = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзины покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_recipe_in_user_shopping_cart'  # Уточненное имя
            )
        ]

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'