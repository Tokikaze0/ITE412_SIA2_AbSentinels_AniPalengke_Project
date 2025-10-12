from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Process 1.0 Authenticate User
    path('api/auth/', include('authapp.urls')),

    # Process 2.0 Manage Products & Inventory
    path('api/products/', include('products.urls')),

    # Process 3.0 Process Orders & Payments
    path('api/orders/', include('orders.urls')),
    path('api/payments/', include('orders.payments_urls')),

    # Process 4.0 Handle Logistics & Delivery
    path('api/delivery/', include('delivery.urls')),

    # Process 5.0 Notifications and Reports
    path('api/notifications/', include('notifications.urls')),

    # Process 6.0 Advisory Content and Community
    path('api/community/', include('community.urls')),
    path('api/advisory/', include('community.advisory_urls')),
]
