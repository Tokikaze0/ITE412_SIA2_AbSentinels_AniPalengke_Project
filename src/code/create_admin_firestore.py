import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anipalengke.settings')
django.setup()

from core.utils import create_user_firestore

def create_admin():
    print("Creating Admin User in Firestore...")
    username = input("Username (default: admin): ") or "admin"
    email = input("Email (default: admin@example.com): ") or "admin@example.com"
    password = input("Password (default: admin123): ") or "admin123"
    
    print(f"Creating user {username}...")
    user_id, error = create_user_firestore(username, email, password, role='admin', is_verified=True)
    
    if user_id:
        print(f"Successfully created admin user with ID: {user_id}")
    else:
        print(f"Failed to create admin user: {error}")

if __name__ == "__main__":
    create_admin()
