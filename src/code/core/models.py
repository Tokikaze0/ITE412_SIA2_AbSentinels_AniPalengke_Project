from django.db import models
from django.utils import timezone

# Create your models here.

class Article(models.Model):
    title = models.CharField(max_length=200)
    summary = models.TextField(help_text="Short description for the card")
    content = models.TextField(help_text="Full article content")
    category = models.CharField(max_length=100, default="General")
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.title
