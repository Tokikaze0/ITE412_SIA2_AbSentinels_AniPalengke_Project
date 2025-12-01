from .models import Conversation, Message

def unread_messages_count(request):
    if not request.user.is_authenticated:
        return {'unread_messages_count': 0}
    
    count = 0
    # Iterate over all conversations to find ones where the user is a participant
    # Note: This is not efficient for large databases but works for this prototype structure
    all_conversations = Conversation.objects.all()
    
    for conv in all_conversations:
        if request.user.id in conv.participants:
            # Count unread messages sent by others
            count += conv.messages.filter(is_read=False).exclude(sender_id=request.user.id).count()
            
    return {'unread_messages_count': count}
