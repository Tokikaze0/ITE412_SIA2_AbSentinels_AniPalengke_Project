import time
import jwt
from typing import Dict, Any
from django.conf import settings
from django.http import JsonResponse

# Simple JWT helpers for prototype

def create_token(payload: Dict[str, Any], expires_in_seconds: int = 3600) -> str:
    to_encode = {
        **payload,
        'exp': int(time.time()) + expires_in_seconds,
        'iat': int(time.time()),
    }
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

def decode_token(token: str) -> Dict[str, Any]:
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

def require_auth(view_func):
    def _wrapped(request, *args, **kwargs):
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'detail': 'Unauthorized'}, status=401)
        token = auth_header.replace('Bearer ', '').strip()
        try:
            request.user_claims = decode_token(token)
        except Exception:
            return JsonResponse({'detail': 'Invalid token'}, status=401)
        return view_func(request, *args, **kwargs)
    return _wrapped
