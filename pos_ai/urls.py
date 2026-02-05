"""
BiashAI - URL Configuration
Complete routing for face recognition shopping system
"""

from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from pos_ai import views

urlpatterns = [

    # ==================== AUTHENTICATION ====================
    path('auth/register/', views.register, name='register'),
    path('auth/login/', views.user_login, name='login'),
    path('auth/logout/', views.user_logout, name='logout'),

    # ==================== CUSTOMER DASHBOARD ====================
    path('customer/dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/profile/', views.customer_profile, name='customer_profile'),
    path('customer/transactions/', views.customer_transactions, name='customer_transactions'),
    path('customer/transactions/<uuid:transaction_id>/',views.transaction_detail,name='transaction_detail'),

    # Face Registration
    path('customer/face/register/', views.face_registration, name='face_registration'),
    path('customer/face/delete/', views.face_delete, name='face_delete'),

    # Payment Accounts
    path('customer/payments/', views.payment_accounts, name='payment_accounts'),
    path('customer/payments/add/', views.add_payment_account, name='add_payment_account'),
    path('customer/payments/delete/<uuid:account_id>/',views.delete_payment_account,name='delete_payment_account'),

    # Loyalty
    path('customer/loyalty/', views.loyalty_dashboard, name='loyalty_dashboard'),

    # ==================== SHOPPING ====================
    # Stores
    path('shop/stores/', views.stores, name='stores'),
    path('shop/stores/<uuid:store_id>/', views.store_detail, name='store_detail'),

    # Products
    path('shop/products/', views.products, name='products'),
    path('shop/products/<uuid:product_id>/', views.product_detail, name='product_detail'),

    # Shopping Session
    path('shop/session/start/<uuid:store_id>/',views.start_shopping_session, name='start_shopping_session'),
    path('shop/session/<uuid:session_id>/',views.shopping_session,name='shopping_session'),

    # Cart
    path('shop/session/<uuid:session_id>/add/<uuid:product_id>/',views.add_to_cart,name='add_to_cart'),
    path('shop/session/<uuid:session_id>/update/<uuid:cart_item_id>/',views.update_cart_item,name='update_cart_item'),
    path('shop/session/<uuid:session_id>/remove/<uuid:cart_item_id>/',views.remove_from_cart,name='remove_from_cart'),

    # Checkout
    path('shop/session/<uuid:session_id>/checkout/',views.checkout,name='checkout'),

    # Promotions
    path('shop/promotions/', views.promotions_list, name='promotions_list'),

    # ==================== STAFF / ADMIN DASHBOARD ====================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/analytics/', views.analytics, name='analytics'),

    # Store Management
    path('dashboard/stores/', views.manage_stores, name='manage_stores'),
    path('dashboard/stores/<uuid:store_id>/inventory/',views.manage_inventory,name='manage_inventory'),

    # Product Management
    path('dashboard/products/', views.manage_products, name='manage_products'),

    # Customer Management
    path('dashboard/customers/', views.customers_list, name='customers_list'),

    # Security
    path('dashboard/security/alerts/',views.security_alerts_view,name='security_alerts'),

    # ==================== API v1 ====================
    path('api/v1/face/verify/', views.api_face_verify, name='api_face_verify'),
    path('api/v1/stores/<uuid:store_id>/status/',views.api_store_status,name='api_store_status'),
    path('api/v1/products/<uuid:product_id>/availability/<uuid:store_id>/',views.api_product_availability,name='api_product_availability'),
]

# ==================== STATIC & MEDIA ====================
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
