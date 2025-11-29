import uuid
from django.conf import settings

def create_gcash_payment_link(amount, description):
    """
    Mock Payment Gateway API (GCash).
    Returns a payment ID and a redirect URL.
    Uses settings.PAYMENT_GATEWAY_KEY for authentication (mock).
    """
    # In a real app, we would use the API key here:
    # api_key = settings.PAYMENT_GATEWAY_KEY
    
    payment_id = str(uuid.uuid4())
    # In a real app, this would be a URL from PayMongo/Xendit
    redirect_url = f"/orders/payment/gcash/mock/{payment_id}/?amount={amount}"
    return payment_id, redirect_url

def verify_gcash_payment(payment_id):
    """
    Mock verification. Always returns success for demo.
    """
    return True
