from django.db import models

from foodgram.constants import (MAX_TAG_LENGTH,
                                MAX_INGRIDIENT_NAME_LENGTH,
                                MAX_UNIT_NAME_LENGTH,)


class Tag(models.Model):
    name = models.CharField(
        'название тега',
        max_length=MAX_TAG_LENGTH,
        unique=True
    )
    slug = models.SlugField(
        'slug названия тега',
        max_length=MAX_TAG_LENGTH,
        unique=True
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return f'{self.name}'


# class Recipies(models.Model):
#     image = models.ImageField('Картинка', upload_to='recipes/')
#     name = models.CharField('Название', max_length=RECIPE_MAX_LENGTH_NAME)
#     text = models.TextField('Описание')
#     cooking_time = models.PositiveSmallIntegerField(
#         'Время приготовления в минутах',
#         validators=[
#             MinValueValidator(
#                 COOKING_MIN_TIME,
#                 f'Значение не должно быть меньше {COOKING_MIN_TIME}',
#             ),
#             MaxValueValidator(
#                 MAX_POSITIVE_VALUE,
#                 f'Значение не должно быть больше {MAX_POSITIVE_VALUE}',
#             ),
#         ],
#     )
#     tags = models.ManyToManyField(Tag, verbose_name='Теги')
#     ingredients = models.ManyToManyField(
#         Ingredient, verbose_name='Ингредиенты', through='RecipeIngredient'
#     )

#     class Meta:
#         ordering = ('-created_at',)
#         default_related_name = 'recipes'
#         verbose_name = 'Рецепт'
#         verbose_name_plural = 'Рецепты'

#     def __str__(self):
#         return self.name


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
