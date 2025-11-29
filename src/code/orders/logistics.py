import random
from django.conf import settings

def calculate_shipping_fee(location):
    """
    Mock logistics API to calculate shipping fee based on location.
    Uses settings.LOGISTICS_API_KEY for authentication (mock).
    """
    # In a real app, we would use the API key here:
    # api_key = settings.LOGISTICS_API_KEY
    
    base_fee = 50
    location_fees = {
        'Alcate': 20,
        'Bayani': 30,
        'Inarawan': 40,
        'Villa Cerveza': 60
    }
    return base_fee + location_fees.get(location, 50)

def get_tracking_status(tracking_number):
    """
    Mock logistics API to get tracking status.
    """
    statuses = [
        "Order Placed",
        "Picked Up by Rider",
        "In Transit to Sorting Center",
        "Out for Delivery",
        "Delivered"
    ]
    # Randomly return a status for demo purposes
    return random.choice(statuses)

def generate_tracking_number():
    return f"TRK-{random.randint(10000, 99999)}"
