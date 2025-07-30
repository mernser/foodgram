from django.db import models

from foodgram.constants import MAX_TAG_LENGTH


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
