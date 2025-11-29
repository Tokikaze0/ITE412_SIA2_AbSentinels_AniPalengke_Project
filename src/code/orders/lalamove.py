import time
import hmac
import hashlib
import uuid
import requests
import json
from django.conf import settings

class LalamoveService:
    def __init__(self):
        self.host = settings.LALAMOVE_BASE_URL
        self.key = settings.LALAMOVE_API_KEY
        self.secret = settings.LALAMOVE_API_SECRET
        self.market = settings.LALAMOVE_MARKET

    def _generate_signature(self, method, path, body=""):
        time_stamp = int(time.time() * 1000)
        raw_signature = f"{time_stamp}\r\n{method}\r\n{path}\r\n\r\n{body}"
        signature = hmac.new(
            self.secret.encode(), raw_signature.encode(), hashlib.sha256
        ).hexdigest()
        return time_stamp, signature

    def _request(self, method, path, payload=None):
        url = f"{self.host}{path}"
        body = json.dumps(payload) if payload else ""
        time_stamp, signature = self._generate_signature(method, path, body)

        headers = {
            "Authorization": f"hmac {self.key}:{time_stamp}:{signature}",
            "Market": self.market,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Generate a unique request ID for idempotency
        if method == 'POST':
            headers['X-Request-ID'] = str(uuid.uuid4())

        try:
            response = requests.request(method, url, headers=headers, data=body)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Lalamove API Error: {e}")
            # Return error dict instead of crashing, or re-raise depending on preference
            return {"error": str(e)}

    def get_quotation(self, pickup_address, delivery_address):
        """
        Get a price quote for delivery.
        """
        path = "/v3/quotations"
        payload = {
            "data": {
                "serviceType": "MOTORCYCLE", # or VAN, TRUCK330, etc.
                "stops": [
                    {"address": pickup_address},
                    {"address": delivery_address}
                ],
                "language": "en_PH"
            }
        }
        return self._request("POST", path, payload)

    def place_order(self, quotation_id, sender_details, recipient_details):
        """
        Place an order using a quotation ID.
        """
        path = "/v3/orders"
        payload = {
            "data": {
                "quotationId": quotation_id,
                "sender": {
                    "stopId": sender_details.get('stopId'),
                    "name": sender_details.get('name'),
                    "phone": sender_details.get('phone')
                },
                "recipients": [
                    {
                        "stopId": recipient_details.get('stopId'),
                        "name": recipient_details.get('name'),
                        "phone": recipient_details.get('phone')
                    }
                ]
            }
        }
        return self._request("POST", path, payload)

    def get_order_details(self, order_id):
        """
        Get details of a specific order.
        """
        path = f"/v3/orders/{order_id}"
        return self._request("GET", path)
