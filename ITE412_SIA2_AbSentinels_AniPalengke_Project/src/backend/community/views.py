from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from utils.jsondb import read_json, write_json
from utils.auth import require_auth
from pubsubapp.bus import publish

# Process 6.0 Advisory Content and Community

COMMUNITY_FILE = 'community.json'

@csrf_exempt
@require_auth
def community_posts(request):
    db = read_json(COMMUNITY_FILE, [])
    if request.method == 'GET':
        return JsonResponse({'items': db})
    if request.method == 'POST':
        body = json.loads(request.body or '{}')
        required = ['content']
        if not all(k in body for k in required):
            return JsonResponse({'detail': 'Missing fields'}, status=400)
        post = {
            'id': len(db) + 1,
            'authorId': request.user_claims['sub'],
            'content': body['content'],
            'type': 'community',
            'status': 'PUBLISHED',
        }
        db.append(post)
        write_json(COMMUNITY_FILE, db)
        return JsonResponse(post, status=201)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)

@csrf_exempt
@require_auth
def advisory(request):
    db = read_json(COMMUNITY_FILE, [])
    if request.method == 'GET':
        return JsonResponse({'items': [p for p in db if p['type'] == 'advisory']})
    if request.method == 'POST':
        body = json.loads(request.body or '{}')
        required = ['content']
        if not all(k in body for k in required):
            return JsonResponse({'detail': 'Missing fields'}, status=400)
        post = {
            'id': len(db) + 1,
            'authorId': request.user_claims['sub'],
            'content': body['content'],
            'type': 'advisory',
            'status': 'PUBLISHED',
        }
        db.append(post)
        write_json(COMMUNITY_FILE, db)
        publish('NewAdvisoryPost', {'postId': post['id']})
        return JsonResponse(post, status=201)
    return JsonResponse({'detail': 'Method not allowed'}, status=405)
