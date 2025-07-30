from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username
from foodgram.constants import (MAX_EMAIL_LENGTH,
                                MAX_NAME_FIELDS_LENTGH)


class MyUser(AbstractUser):
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        null=True,
        default=None,
    )
    email = models.EmailField(
        'Email',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        blank=False,
        null=False,
        help_text='Адрес электронной почты',
    )
    username = models.CharField(
        'Юзернейм',
        max_length=MAX_NAME_FIELDS_LENTGH,
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальный юзернейм',
        validators=(validate_username, )
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_NAME_FIELDS_LENTGH,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_NAME_FIELDS_LENTGH,
        blank=False,
        null=False
    )

    class Meta:
        ordering = ('last_name',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Subscription(models.Model):
    follower = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='follower'
    )
    subscribed_to = models.ForeignKey(
        MyUser,
        on_delete=models.CASCADE,
        verbose_name='На кого подписан',
        related_name='subscribed_to'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('follower', 'subscribed_to'),
                name='unique_follower_subscribed_to'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'{self.follower.username} -> {self.subscribed_to.username}'
        )
