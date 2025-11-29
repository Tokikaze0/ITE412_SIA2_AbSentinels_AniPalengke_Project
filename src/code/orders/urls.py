from django.urls import path
from . import views

urlpatterns = [
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<str:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/apply-voucher/', views.apply_voucher, name='apply_voucher'),
    path('cart/remove-voucher/', views.remove_voucher, name='remove_voucher'),
    path('checkout/', views.checkout_view, name='checkout'),
    # path('place-order/', views.place_order, name='place_order'), # Deprecated, handled in checkout_view
    path('payment/process/', views.process_payment, name='process_payment'),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),
    path('payment/release/<str:order_id>/', views.release_funds, name='release_funds'),
    path('track/<str:order_id>/', views.track_order, name='track_order'),
    path('waybill/<str:order_id>/', views.print_waybill, name='print_waybill'),
    path('payment/gcash/mock/<str:payment_id>/', views.gcash_mock_view, name='gcash_mock'),
    path('payment/gcash/confirm/<str:payment_id>/', views.gcash_confirm_view, name='gcash_confirm'),
    path('history/', views.order_history, name='order_history'),
]
