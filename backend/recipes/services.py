import hashlib

from django.apps import apps
from django.utils import timezone

from foodgram.constants import MAX_HASH_LENGTH


def generate_short_link(short_link, id):
    if not short_link:
        Recipie = apps.get_model('recipes', 'Recipie')
        base_str = f'{timezone.now().timestamp()}{id if id else ""}'
        short_link = (
            hashlib
            .md5(base_str.encode()).hexdigest()[:MAX_HASH_LENGTH]
        )
        i = 1
        original_url = short_link
        while Recipie.objects.filter(short_link=short_link).exists():
            short_link = f'{original_url[:(MAX_HASH_LENGTH - 1)]}{i}'
            i += 1
    return short_link
