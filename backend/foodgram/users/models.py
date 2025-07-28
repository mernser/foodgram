from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import validate_username


class MyUser(AbstractUser):
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        null=True,
        blank=True,
    )
    email = models.EmailField(
        'email',
        max_length=254,
        unique=True,
        blank=False,
        null=False,
        help_text='Адрес электронной почты',
    )
    username = models.CharField(
        'Имя пользователя',
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        help_text='Уникальный юзернейм',
        validators=(validate_username, )
    )
    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=False,
        null=False
    )
    password = models.CharField(
        'Пароль',
        blank=False,
        null=False,
    )

    class Meta:
        ordering = ('last_name',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} + {self.last_name}'


class Subscription