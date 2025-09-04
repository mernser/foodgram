from django.contrib.auth.models import AbstractUser
from django.db import models

from foodgram.constants import MAX_EMAIL_LENGTH, MAX_NAME_FIELDS_LENTGH
from users.validators import validate_username


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    avatar = models.ImageField(
        'Аватар',
        upload_to='users/avatars/',
        default=None,
        help_text='Фотография профиля пользователя',
    )
    email = models.EmailField(
        'Email',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
        help_text='Адрес электронной почты',
    )
    username = models.CharField(
        'Username',
        max_length=MAX_NAME_FIELDS_LENTGH,
        unique=True,
        help_text='Уникальный юзернейм',
        validators=(validate_username, )
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_NAME_FIELDS_LENTGH,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_NAME_FIELDS_LENTGH,
    )

    class Meta:
        ordering = ('last_name',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписки пользователя',
        related_name='user_subscriptions'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписки на автора',
        related_name='subscriptions_to_author'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_user_subscriptions',
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name='self_subscription_unallowed'
            ),
        )
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return (
            f'{self.user.username} -> {self.author.username}'
        )
