from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from utils.jsondb import read_json, write_json
from utils.auth import require_auth
from pubsubapp.bus import publish

# Process 3.0 Process Orders & Payments

ORDERS_FILE = 'orders.json'
PAYMENTS_FILE = 'payments.json'

@csrf_exempt
@require_auth
def orders_list(request):
    db = read_json(ORDERS_FILE, [])
    user = request.user_claims
    if request.method == 'GET':
        # buyers see own orders; admin sees all
        if user.get('role') == 'Admin':
            return JsonResponse({'items': db})
        return JsonResponse({'items': [o for o in db if o['buyerId'] == user['sub']]})
    if request.method == 'POST':
        body = json.loads(request.body or '{}')
        required = ['items']
        if not all(k in body for k in required):
            return JsonResponse({'detail': 'Missing fields'}, status=400)
        order = {
            'id': len(db) + 1,
            'buyerId': user['sub'],
            'items': body['items'],  # [{productId, qty}]
            'status': 'CREATED',
        }
        db.append(order)
        write_json(ORDERS_FILE, db)
        publish('OrderCreated', {'orderId': order['id'], 'buyerId': user['sub']})
        return JsonResponse(order, status=201)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

@csrf_exempt
@require_auth
def payments(request):
    payments_db = read_json(PAYMENTS_FILE, [])
    orders_db = read_json(ORDERS_FILE, [])
    user = request.user_claims
    if request.method == 'POST':
        body = json.loads(request.body or '{}')
        required = ['orderId', 'amount']
        if not all(k in body for k in required):
            return JsonResponse({'detail': 'Missing fields'}, status=400)
        order = next((o for o in orders_db if o['id'] == body['orderId']), None)
        if not order:
            return JsonResponse({'detail': 'Order not found'}, status=404)
        if order['buyerId'] != user['sub'] and user.get('role') != 'Admin':
            return JsonResponse({'detail': 'Forbidden'}, status=403)
        payment = {
            'id': len(payments_db) + 1,
            'orderId': order['id'],
            'amount': body['amount'],
            'status': 'CONFIRMED',  # Simulate GCash success
            'provider': 'GCashMock',
        }
        payments_db.append(payment)
        write_json(PAYMENTS_FILE, payments_db)
        # update order status
        order['status'] = 'PAID'
        write_json(ORDERS_FILE, orders_db)
        publish('PaymentConfirmed', {'orderId': order['id'], 'buyerId': order['buyerId']})
        return JsonResponse(payment, status=201)

    if request.method == 'GET':
        if user.get('role') == 'Admin':
            return JsonResponse({'items': payments_db})
        user_orders = {o['id'] for o in orders_db if o['buyerId'] == user['sub']}
        return JsonResponse({'items': [p for p in payments_db if p['orderId'] in user_orders]})

    return JsonResponse({'detail': 'Method not allowed'}, status=405)
