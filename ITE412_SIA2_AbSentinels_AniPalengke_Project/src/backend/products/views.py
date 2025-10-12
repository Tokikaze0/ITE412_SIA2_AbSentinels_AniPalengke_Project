from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from utils.jsondb import read_json, write_json
from utils.auth import require_auth

# Process 2.0 Manage Products & Inventory

PRODUCTS_FILE = 'products.json'

@csrf_exempt
def products_list(request):
    db = read_json(PRODUCTS_FILE, [])
    if request.method == 'GET':
        q = request.GET.get('q', '').lower()
        if q:
            filtered = [p for p in db if q in p.get('name', '').lower()]
            return JsonResponse({'items': filtered})
        return JsonResponse({'items': db})
    if request.method == 'POST':
        return create_product(request, db)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

@require_auth
def create_product(request, db):
    body = json.loads(request.body or '{}')
    required = ['name', 'price', 'stock']
    if not all(k in body for k in required):
        return JsonResponse({'detail': 'Missing fields'}, status=400)
    user = request.user_claims
    if user.get('role') != 'Farmer' and user.get('role') != 'Admin':
        return JsonResponse({'detail': 'Only farmers/admin can create'}, status=403)
    product = {
        'id': len(db) + 1,
        'name': body['name'],
        'price': body['price'],
        'stock': body['stock'],
        'ownerId': user['sub'],
    }
    db.append(product)
    write_json(PRODUCTS_FILE, db)
    return JsonResponse(product, status=201)

@csrf_exempt
def product_detail(request, product_id: int):
    db = read_json(PRODUCTS_FILE, [])
    product = next((p for p in db if p['id'] == product_id), None)
    if not product:
        return JsonResponse({'detail': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse(product)

    if request.method in ('PUT', 'PATCH', 'DELETE'):
        return modify_product(request, db, product)

    return JsonResponse({'detail': 'Method not allowed'}, status=405)

@require_auth
def modify_product(request, db, product):
    user = request.user_claims
    if user.get('role') not in ('Farmer', 'Admin'):
        return JsonResponse({'detail': 'Forbidden'}, status=403)
    if user.get('role') != 'Admin' and product['ownerId'] != user['sub']:
        return JsonResponse({'detail': 'Not owner'}, status=403)

    if request.method == 'DELETE':
        new_db = [p for p in db if p['id'] != product['id']]
        write_json(PRODUCTS_FILE, new_db)
        return JsonResponse({'detail': 'Deleted'})

    body = json.loads(request.body or '{}')
    for field in ['name', 'price', 'stock']:
        if field in body:
            product[field] = body[field]
    write_json(PRODUCTS_FILE, db)
    return JsonResponse(product)
