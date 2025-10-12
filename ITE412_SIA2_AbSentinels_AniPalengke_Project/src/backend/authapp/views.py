from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from utils.jsondb import read_json, write_json
from utils.auth import create_token, require_auth

# Process 1.0 Authenticate User

USERS_FILE = 'users.json'

@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    body = json.loads(request.body or '{}')
    required = ['email', 'password', 'role']
    if not all(k in body for k in required):
        return JsonResponse({'detail': 'Missing fields'}, status=400)

    db = read_json(USERS_FILE, [])
    if any(u['email'] == body['email'] for u in db):
        return JsonResponse({'detail': 'Email already exists'}, status=400)

    user = {
        'id': len(db) + 1,
        'email': body['email'],
        'password': body['password'],  # For prototype only; do not store plain passwords in production
        'role': body['role'],  # Farmer, Buyer, Admin
        'name': body.get('name', ''),
    }
    db.append(user)
    write_json(USERS_FILE, db)

    token = create_token({'sub': user['id'], 'email': user['email'], 'role': user['role']})
    return JsonResponse({'token': token, 'user': {k: v for k, v in user.items() if k != 'password'}})

@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'Method not allowed'}, status=405)
    body = json.loads(request.body or '{}')
    email = body.get('email')
    password = body.get('password')
    db = read_json(USERS_FILE, [])
    user = next((u for u in db if u['email'] == email and u['password'] == password), None)
    if not user:
        return JsonResponse({'detail': 'Invalid credentials'}, status=401)
    token = create_token({'sub': user['id'], 'email': user['email'], 'role': user['role']})
    return JsonResponse({'token': token, 'user': {k: v for k, v in user.items() if k != 'password'}})

@csrf_exempt
@require_auth
def me(request):
    return JsonResponse({'claims': getattr(request, 'user_claims', {})})

@csrf_exempt
@require_auth
def logout_view(request):
    return JsonResponse({'detail': 'Logged out (client-side token discard)'})
