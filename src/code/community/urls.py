from django.urls import path
from . import views

urlpatterns = [
    path('', views.community_feed, name='community_feed'),
    path('create/', views.create_post, name='create_post'),
    path('post/<str:post_id>/', views.post_detail, name='post_detail'),
    path('post/<str:post_id>/comment/', views.add_comment, name='add_comment'),
]