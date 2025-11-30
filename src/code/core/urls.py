from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('knowledge/', views.knowledge_base, name='knowledge_base'),
    path('knowledge/<str:article_id>/', views.article_detail, name='article_detail'),
    path('ai/', views.ai_assistant, name='ai_assistant'),
    path('ai/chat/', views.ai_chat, name='ai_chat'),
    path('ai/clear/', views.ai_clear_chat, name='ai_clear_chat'),
    path('ai/analyze/', views.ai_analyze, name='ai_analyze'),
]
