from django.urls import path
from .views import notifications, consume_events

urlpatterns = [
    path('', notifications, name='notifications'),
    path('consume', consume_events, name='consume_events'),
]
