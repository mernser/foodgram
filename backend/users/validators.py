import re

from django.core.exceptions import ValidationError


def validate_username(username):
    if username.lower() == 'me':
        raise ValidationError(
            'me - Недопустимое имя пользователя'
        )
    if not bool(re.match(r'^[\w.@+-]+$', username)):
        raise ValidationError(
            'Допустимые символы в username:'
            'Буквы, цифры, нижнее подчеркивание, точка, @, +, -'
        )
    return username
