import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            nargs='?',
            default='./data/ingredients.csv'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        if not file_path:
            file_path = os.path.join(
                settings.BASE_DIR, 'data', 'ingredients.csv'
            )
        else:
            if not os.path.isabs(file_path):
                file_path = os.path.join(settings.BASE_DIR, file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError('файл не найден')
        self.stdout.write(self.style.NOTICE('Загрузка ингредиентов начата.'))
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                ingredients_to_create = []
                for name, measurement_unit in reader:
                    ingredients_to_create.append(
                        Ingredient(
                            name=name.strip(),
                            measurement_unit=measurement_unit.strip())
                    )
                Ingredient.objects.bulk_create(
                    ingredients_to_create,
                    ignore_conflicts=True
                )
        except Exception as e:
            self.stderr.write(
                self.style.ERROR(f'Ошибка при чтении/записи: {e}')
            )
            raise
        self.stdout.write(
            self.style.SUCCESS('Загрузка ингредиентов завершена.')
        )
