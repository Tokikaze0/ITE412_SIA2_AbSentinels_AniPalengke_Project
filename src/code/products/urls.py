from django.urls import path
from . import views

urlpatterns = [
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.add_product, name='add_product'),
    path('products/<str:product_id>/', views.product_detail, name='product_detail'),
    path('products/edit/<str:product_id>/', views.edit_product, name='edit_product'),
    path('products/delete/<str:product_id>/', views.delete_product_view, name='delete_product'),
]
