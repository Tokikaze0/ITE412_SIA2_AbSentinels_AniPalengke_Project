import random
import time

class LalamoveService:
    """
    Mock service for Lalamove API integration.
    In a real application, this would make HTTP requests to Lalamove's API endpoints.
    """
    
    BASE_URL = "https://rest.sandbox.lalamove.com" # Sandbox URL
    
    @staticmethod
    def get_quotation(pickup_address, delivery_address):
        """
        Get a delivery quotation.
        """
        # Mock logic: Calculate fee based on string length difference or random
        # In real app: Call /v3/quotations
        
        base_fee = 60.00
        distance_fee = random.uniform(20, 150)
        total_fee = base_fee + distance_fee
        
        return {
            'quotation_id': f"QUOT_{int(time.time())}",
            'price_breakdown': {
                'base': base_fee,
                'distance': distance_fee,
                'total': round(total_fee, 2),
                'currency': 'PHP'
            },
            'distance': f"{random.randint(2, 15)} km",
            'eta': f"{random.randint(15, 45)} mins"
        }

    @staticmethod
    def place_delivery(quotation_id, contact_name, contact_phone):
        """
        Place a delivery order using a quotation.
        """
        # In real app: Call /v3/orders
        return {
            'order_ref': f"LALA_{int(time.time())}",
            'status': 'ASSIGNING_DRIVER',
            'driver': None,
            'share_link': f"https://lalamove.app/tracking/{int(time.time())}"
        }

    @staticmethod
    def get_order_status(order_ref):
        """
        Check status of delivery.
        """
        statuses = ['ASSIGNING_DRIVER', 'ON_GOING', 'PICKED_UP', 'COMPLETED']
        return random.choice(statuses)
