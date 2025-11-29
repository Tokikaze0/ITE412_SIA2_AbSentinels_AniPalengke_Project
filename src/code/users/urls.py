from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('google-login/', views.google_login, name='google_login'),
    path('register/', views.register_view, name='register'),
    path('verify-registration/', views.verify_registration_view, name='verify_registration'),
    path('verify-email-change/', views.verify_email_change_view, name='verify_email_change'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('settings/', views.profile_settings, name='profile_settings'),
    path('admin/products/', views.admin_product_list, name='admin_product_list'),
    path('admin/products/check-ai/<str:product_id>/', views.admin_check_ai, name='admin_check_ai'),
    path('admin/products/approve/<str:product_id>/', views.approve_product_view, name='approve_product'),
    path('admin/products/<str:product_id>/<str:action>/', views.admin_product_action, name='admin_product_action'),
    path('admin/farmers/verify/<str:user_id>/', views.admin_verify_farmer, name='admin_verify_farmer'),
]
