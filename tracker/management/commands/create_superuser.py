"""
Create initial admin user if needed.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Create a superuser account'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for the superuser')
        parser.add_argument('--email', type=str, help='Email for the superuser')
        parser.add_argument('--password', type=str, help='Password for the superuser')
    
    def handle(self, *args, **options):
        username = options.get('username', 'admin')
        email = options.get('email', 'admin@example.com')
        password = options.get('password', 'admin')
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User {username} already exists')
            )
            return
        
        User.objects.create_superuser(username, email, password)
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created superuser {username}'
            )
        )
