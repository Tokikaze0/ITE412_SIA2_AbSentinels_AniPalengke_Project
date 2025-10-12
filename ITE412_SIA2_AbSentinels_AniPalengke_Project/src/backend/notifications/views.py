from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.jsondb import read_json, write_json
from utils.auth import require_auth
from pubsubapp.bus import consume

# Process 5.0 Notifications and Reports

NOTIFS_FILE = 'notifications.json'

@csrf_exempt
@require_auth
def notifications(request):
    db = read_json(NOTIFS_FILE, [])
    if request.method == 'GET':
        return JsonResponse({'items': db})
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

@csrf_exempt
@require_auth
def consume_events(request):
    db = read_json(NOTIFS_FILE, [])
    for event in consume('OrderCreated'):
        db.append({'type': 'OrderCreated', 'message': f"Order {event['orderId']} created", 'audience': 'Farmer/Buyer'})
    for event in consume('PaymentConfirmed'):
        db.append({'type': 'PaymentConfirmed', 'message': f"Payment for order {event['orderId']} confirmed", 'audience': 'Buyer'})
    for event in consume('NewAdvisoryPost'):
        db.append({'type': 'NewAdvisoryPost', 'message': 'New advisory content posted', 'audience': 'Subscribers'})
    write_json(NOTIFS_FILE, db)
    return JsonResponse({'consumed': True, 'count': len(db)})
