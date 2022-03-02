import json

from django.core.management.base import BaseCommand
from api.models import Ingredient


class Command(BaseCommand):

    def handle(self, *args, **options):
        with open('ingredients.json', "rb") as f:
            reader = json.load(f)
        model_object = Ingredient
        for row in reader:
            model_object.objects.create(**row)
        self.stdout.write(self.style.SUCCESS('Database Successfully Update'))
