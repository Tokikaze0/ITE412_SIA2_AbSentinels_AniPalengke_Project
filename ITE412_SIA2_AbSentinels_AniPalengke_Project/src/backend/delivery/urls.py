from django.urls import path
from .views import deliveries, track

urlpatterns = [
    path('', deliveries, name='deliveries'),
    path('track', track, name='track'),
]
