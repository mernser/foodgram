import csv
import os

from django.core.management.base import BaseCommand
from api.models import Ingredient


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            default='ingredients.csv'
        )

    def handle(self, *args, **options):
        file_path = options['file_path']
        if not os.path.exists(file_path):
            raise FileNotFoundError('файл не найден')
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for name, measurement_unit in reader:
                    Ingredient.objects.update_or_create(
                        name=name.strip(),
                        measurement_unit=measurement_unit.strip()
                    )
        except Exception as e:
            print(f'Ошибка при чтении/записи: {e}')
