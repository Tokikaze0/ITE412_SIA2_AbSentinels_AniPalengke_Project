from django.urls import path
from .views import advisory

urlpatterns = [
    path('', advisory, name='advisory'),
]
