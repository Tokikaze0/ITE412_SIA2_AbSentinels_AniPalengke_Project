import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anipalengke.settings')
django.setup()

from firebase_admin import firestore

def reset():
    db = firestore.client()
    products_ref = db.collection('products')
    
    print("Deleting all products...")
    docs = products_ref.stream()
    deleted = 0
    for doc in docs:
        doc.reference.delete()
        deleted += 1
    print(f"Deleted {deleted} products.")

    print("Re-seeding with new data...")
    
    mock_products = [
        {'name': 'Tomatoes', 'price': 50, 'stock': 100, 'category': 'Gulay', 'location': 'Bulacan', 'farmer_name': 'Farmer John', 'image': '/static/images/kamatis.jpg'},
        {'name': 'Cassava', 'price': 35, 'stock': 50, 'category': 'Root Crops', 'location': 'Pampanga', 'farmer_name': 'Farmer Jane', 'image': '/static/images/cassava.jpg'},
        {'name': 'Eggplant', 'price': 40, 'stock': 80, 'category': 'Gulay', 'location': 'Batangas', 'farmer_name': 'Farmer Mario', 'image': '/static/images/eggplant.jpg'},
    ]

    for p in mock_products:
        products_ref.add(p)
        print(f"Added: {p['name']}")

    print("Done! Database reset and seeded.")

if __name__ == '__main__':
    reset()
