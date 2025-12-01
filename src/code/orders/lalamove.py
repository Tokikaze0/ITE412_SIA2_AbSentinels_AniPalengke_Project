import requests
import random
import uuid

class LalamoveService:
    """
    Integration with JSONPlaceholder to simulate a Logistics API.
    Base URL: https://jsonplaceholder.typicode.com
    """
    BASE_URL = "https://jsonplaceholder.typicode.com"

    def __init__(self):
        pass

    def get_quotation(self, pickup_address, delivery_address):
        """
        Simulates getting a quote. 
        Since JSONPlaceholder doesn't have a quote endpoint, we just mock the calculation 
        but still make a GET request to ensure connectivity.
        """
        try:
            # Make a dummy request to check API availability
            response = requests.get(f"{self.BASE_URL}/posts/1")
            response.raise_for_status()
            
            # Mock logic for fee
            fee = random.randint(60, 250)
            
            return {
                "quotation_id": f"Q-{uuid.uuid4().hex[:8].upper()}",
                "price_breakdown": {
                    "total": fee,
                    "currency": "PHP"
                },
                "stops": [
                    {"address": pickup_address},
                    {"address": delivery_address}
                ]
            }
        except requests.RequestException as e:
            print(f"Logistics API Error: {e}")
            return None

    def place_order(self, quotation_id, sender_details, recipient_details):
        """
        Simulates placing an order by creating a 'Post' on JSONPlaceholder.
        """
        endpoint = f"{self.BASE_URL}/posts"
        payload = {
            "title": f"Delivery for {recipient_details.get('name')}",
            "body": f"From: {sender_details.get('name')} To: {recipient_details.get('name')}",
            "userId": 1 # Mock user ID
        }
        
        try:
            response = requests.post(endpoint, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # JSONPlaceholder always returns id 101 for new posts, so we randomize it for realism
            fake_order_id = random.randint(1, 10) # Use 1-10 to match 'users' endpoint for driver details
            
            return {
                "order_id": str(fake_order_id),
                "status": "ASSIGNING_DRIVER",
                "tracking_url": f"https://anipalengke.com/track/{fake_order_id}"
            }
        except requests.RequestException as e:
            print(f"Logistics API Error: {e}")
            return None

    def get_order_details(self, order_id):
        """
        Simulates getting order/driver details.
        We map 'User' data from JSONPlaceholder to 'Driver' data.
        """
        # Ensure order_id is within 1-10 for JSONPlaceholder users
        safe_id = int(order_id) if str(order_id).isdigit() and 1 <= int(order_id) <= 10 else 1
        
        user_endpoint = f"{self.BASE_URL}/users/{safe_id}"
        todo_endpoint = f"{self.BASE_URL}/todos/{safe_id}"
        
        try:
            # Fetch "Driver" (User)
            user_resp = requests.get(user_endpoint)
            user_data = user_resp.json()
            
            # Fetch "Status" (Todo)
            todo_resp = requests.get(todo_endpoint)
            todo_data = todo_resp.json()
            
            # Map the data
            status = "DELIVERED" if todo_data.get('completed') else "OUT_FOR_DELIVERY"
            
            return {
                "orderId": str(order_id),
                "status": status,
                "driver": {
                    "name": user_data.get('name'),
                    "phone": user_data.get('phone'),
                    "plateNumber": f"ABC {random.randint(100, 999)}" # Mock plate
                },
                "location": {
                    "lat": user_data['address']['geo']['lat'],
                    "lng": user_data['address']['geo']['lng']
                }
            }
        except requests.RequestException:
            return {
                "status": "PENDING",
                "driver": {"name": "Searching..."}
            }
