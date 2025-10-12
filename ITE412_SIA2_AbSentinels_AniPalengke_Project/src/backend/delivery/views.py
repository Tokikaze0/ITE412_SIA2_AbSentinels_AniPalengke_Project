from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from utils.jsondb import read_json, write_json
from utils.auth import require_auth
from pubsubapp.bus import publish, consume

# Process 4.0 Handle Logistics & Delivery

DELIVERIES_FILE = 'deliveries.json'

@csrf_exempt
@require_auth
def deliveries(request):
    db = read_json(DELIVERIES_FILE, [])
    if request.method == 'GET':
        return JsonResponse({'items': db})
    if request.method == 'POST':
        body = json.loads(request.body or '{}')
        required = ['orderId', 'address']
        if not all(k in body for k in required):
            return JsonResponse({'detail': 'Missing fields'}, status=400)
        delivery = {
            'id': len(db) + 1,
            'orderId': body['orderId'],
            'address': body['address'],
            'provider': 'LalamoveMock',
            'status': 'REQUESTED',
        }
        db.append(delivery)
        write_json(DELIVERIES_FILE, db)
        return JsonResponse(delivery, status=201)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

@csrf_exempt
@require_auth
def track(request):
    # consume any OrderCreated events to auto-create delivery requests
    for event in consume('OrderCreated'):
        db = read_json(DELIVERIES_FILE, [])
        delivery = {
            'id': len(db) + 1,
            'orderId': event['orderId'],
            'address': 'TBD',
            'provider': 'LalamoveMock',
            'status': 'REQUESTED',
        }
        db.append(delivery)
        write_json(DELIVERIES_FILE, db)
    # return current deliveries as tracking snapshot
    return JsonResponse({'items': read_json(DELIVERIES_FILE, [])})
