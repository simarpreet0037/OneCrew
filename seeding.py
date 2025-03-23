import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OneCrew.settings')
django.setup()

from dashboard.models import User

# Create dummy users
def create_dummy_users():
    if not User.objects.filter(email="admin@example.com").exists():
        User.objects.create_superuser(email="admin@example.com", password="admin123")
        print("Superuser created!")

    if not User.objects.filter(email="user@example.com").exists():
        User.objects.create_user(email="user@example.com", password="user123")
        print("Regular user created!")

    if not User.objects.filter(email="test@example.com").exists():
        User.objects.create_user(email="test@example.com", password="test123")
        print("Regular test user created!")

    if not User.objects.filter(email="dummy@example.com").exists():
        User.objects.create_user(email="dummy@example.com", password="dummy123")
        print("Regular dummy user created!")

    if not User.objects.filter(email="ems@example.com").exists():
        User.objects.create_user(email="ems@example.com", password="ems123")
        print("Regular ems user created!")

if __name__ == "__main__":
    create_dummy_users()
#test@gmail.com
#1234