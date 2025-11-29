import uuid
import requests
import base64
from django.conf import settings

class PayMongoService:
    def __init__(self):
        self.secret_key = settings.PAYMONGO_SECRET_KEY
        self.base_url = settings.PAYMONGO_BASE_URL
        # PayMongo requires Basic Auth with the secret key as the username
        self.headers = {
            "Authorization": f"Basic {base64.b64encode(self.secret_key.encode()).decode()}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    def create_payment_link(self, amount, description, remarks=""):
        """
        Create a GCash/GrabPay payment link via PayMongo.
        Amount should be in centavos (e.g., 100.00 PHP -> 10000).
        """
        url = f"{self.base_url}/links"
        
        # Convert amount to integer centavos
        amount_centavos = int(amount * 100)
        
        payload = {
            "data": {
                "attributes": {
                    "amount": amount_centavos,
                    "description": description,
                    "remarks": remarks
                }
            }
        }

        try:
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()['data']
            return {
                'id': data['id'],
                'checkout_url': data['attributes']['checkout_url'],
                'reference_number': data['attributes']['reference_number']
            }
        except requests.exceptions.RequestException as e:
            print(f"PayMongo Error: {e}")
            return None

    def get_payment_status(self, link_id):
        """
        Check the status of a payment link.
        """
        url = f"{self.base_url}/links/{link_id}"
        
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            data = response.json()['data']
            # Statuses: unpaid, paid
            return data['attributes']['status']
        except requests.exceptions.RequestException as e:
            print(f"PayMongo Error: {e}")
            return None

# Keep the old mock functions for backward compatibility if needed, 
# or update them to use the new service.

def create_gcash_payment_link(amount, description):
    """
    Wrapper for PayMongoService to maintain compatibility.
    """
    service = PayMongoService()
    result = service.create_payment_link(amount, description)
    if result:
        return result['id'], result['checkout_url']
    return None, None

def verify_gcash_payment(payment_id):
    """
    Wrapper for PayMongoService to maintain compatibility.
    """
    service = PayMongoService()
    status = service.get_payment_status(payment_id)
    return status == 'paid'
