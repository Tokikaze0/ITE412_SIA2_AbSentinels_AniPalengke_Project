from django.urls import path
from . import views

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('room/<int:conversation_id>/', views.chat_room, name='chat_room'),
    path('start/<str:user_id>/', views.start_chat, name='start_chat'),
    path('api/messages/<int:conversation_id>/', views.get_messages, name='get_messages'),
]
