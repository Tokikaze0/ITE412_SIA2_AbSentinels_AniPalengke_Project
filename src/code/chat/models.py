from django.db import models
from django.contrib.auth.models import User

class Conversation(models.Model):
    participants = models.JSONField(default=list)  # Stores list of Firestore user IDs
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Conversation {self.id}"

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender_id = models.CharField(max_length=255, default='unknown')  # Firestore User ID
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender_id} at {self.timestamp}"
