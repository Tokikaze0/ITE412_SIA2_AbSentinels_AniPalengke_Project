from django.urls import path
from .views import community_posts

urlpatterns = [
    path('', community_posts, name='community_posts'),
]
