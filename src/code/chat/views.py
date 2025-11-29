from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Conversation, Message
from core.utils import get_user_by_id

@login_required
def inbox(request):
    # Filter conversations where current user is a participant
    # Note: For SQLite, JSONField lookups can be limited. 
    # We'll fetch all and filter in python if needed, but __contains usually works for lists in recent Django.
    all_conversations = Conversation.objects.all().order_by('-updated_at')
    user_conversations = []
    
    for conv in all_conversations:
        if request.user.id in conv.participants:
            user_conversations.append(conv)

    chat_data = []
    for chat in user_conversations:
        other_uid = next((uid for uid in chat.participants if uid != request.user.id), None)
        other_user = None
        if other_uid:
            other_user = get_user_by_id(other_uid)
        
        chat_data.append({
            'id': chat.id,
            'other_user': other_user,
            'last_message': chat.messages.last(),
            'updated_at': chat.updated_at
        })
        
    return render(request, 'chat/inbox.html', {'conversations': chat_data})

@login_required
def chat_room(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user.id not in conversation.participants:
        return redirect('inbox')
    
    messages = conversation.messages.all()
    
    # Mark unread messages as read
    # We can't use exclude(sender=request.user) because sender is now a CharField ID
    unread_messages = messages.filter(is_read=False).exclude(sender_id=request.user.id)
    unread_messages.update(is_read=True)
    
    other_uid = next((uid for uid in conversation.participants if uid != request.user.id), None)
    other_user = None
    if other_uid:
        other_user = get_user_by_id(other_uid)
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                conversation=conversation,
                sender_id=request.user.id,
                content=content
            )
            conversation.save() # Update updated_at
            return redirect('chat_room', conversation_id=conversation.id)
            
    return render(request, 'chat/room.html', {
        'conversation': conversation,
        'messages': messages,
        'other_user': other_user,
        'current_user_id': request.user.id
    })

@login_required
def start_chat(request, user_id):
    # user_id is the target Firestore User ID
    if user_id == request.user.id:
        return redirect('inbox')
        
    # Check if conversation already exists
    # We need to find a conversation that has EXACTLY these two participants
    # or at least contains both.
    
    all_conversations = Conversation.objects.all()
    existing_conv = None
    
    for conv in all_conversations:
        if request.user.id in conv.participants and user_id in conv.participants:
            existing_conv = conv
            break
    
    if existing_conv:
        return redirect('chat_room', conversation_id=existing_conv.id)
    else:
        conversation = Conversation.objects.create(
            participants=[request.user.id, user_id]
        )
        return redirect('chat_room', conversation_id=conversation.id)

@login_required
def get_messages(request, conversation_id):
    conversation = get_object_or_404(Conversation, id=conversation_id)
    if request.user.id not in conversation.participants:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    # We need to manually construct the response because we don't have sender__username relation anymore
    messages_data = []
    for msg in conversation.messages.all():
        # We might want to cache user names to avoid fetching for every message
        # For now, let's just send the ID and let the frontend handle it or send 'You'/'Them'
        is_me = (msg.sender_id == request.user.id)
        sender_name = "You" if is_me else "User" # Ideally fetch name
        
        messages_data.append({
            'sender__username': sender_name, # Frontend expects this key
            'sender_id': msg.sender_id,
            'content': msg.content,
            'timestamp': msg.timestamp
        })
        
    return JsonResponse({'messages': messages_data})
