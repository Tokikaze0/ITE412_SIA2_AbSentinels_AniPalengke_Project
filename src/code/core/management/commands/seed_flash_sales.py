from django.core.management.base import BaseCommand
from firebase_admin import firestore
import random

class Command(BaseCommand):
    help = 'Seeds Firestore with flash sale products'

    def handle(self, *args, **kwargs):
        db = firestore.client()
        products_ref = db.collection('products')
        
        # Get all products
        docs = list(products_ref.stream())
        
        if not docs:
            self.stdout.write(self.style.WARNING('No products found. Please run seed command first.'))
            return

        # Reset all flash sales first
        for doc in docs:
            products_ref.document(doc.id).update({
                'is_flash_sale': False,
                'discount_price': firestore.DELETE_FIELD,
                'discount_percent': firestore.DELETE_FIELD,
                'sold_percentage': firestore.DELETE_FIELD
            })

        # Pick 3 random products
        selected_docs = random.sample(docs, min(len(docs), 3))
        
        for doc in selected_docs:
            product = doc.to_dict()
            original_price = product.get('price', 0)
            
            if original_price > 0:
                discount_percent = random.randint(10, 50)
                discount_price = int(original_price * (1 - discount_percent / 100))
                sold_percentage = random.randint(20, 90)
                
                products_ref.document(doc.id).update({
                    'is_flash_sale': True,
                    'discount_price': discount_price,
                    'discount_percent': discount_percent,
                    'sold_percentage': sold_percentage
                })
                
                self.stdout.write(self.style.SUCCESS(f"Added flash sale: {product.get('name')} (-{discount_percent}%)"))
