from django.urls import path
from .views import orders_list

urlpatterns = [
    path('', orders_list, name='orders_list'),
]
