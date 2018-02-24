from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        if not User.objects.filter(username="mattadmin").exists():
            User.objects.create_superuser("mattadmin", "matt388@gmail.com", "195481")
            self.stdout.write(self.style.SUCCESS('Successfully created new super user'))