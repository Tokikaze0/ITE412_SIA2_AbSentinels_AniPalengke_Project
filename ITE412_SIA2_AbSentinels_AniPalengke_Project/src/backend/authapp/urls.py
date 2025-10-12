from django.urls import path
from .views import register, login_view, me, logout_view

urlpatterns = [
    path('register', register, name='register'),
    path('login', login_view, name='login'),
    path('logout', logout_view, name='logout'),
    path('me', me, name='me'),
]
