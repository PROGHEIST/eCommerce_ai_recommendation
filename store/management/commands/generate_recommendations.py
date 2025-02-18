from django.core.management.base import BaseCommand
from store.recommendations import generate_recommendations

class Command(BaseCommand):
    help = "Generate AI-based product recommendations for users"

    def handle(self, *args, **kwargs):
        generate_recommendations()
