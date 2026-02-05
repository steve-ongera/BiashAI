"""
BiashAI - URL Configuration
Complete routing for face recognition shopping system
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

from pos_ai import views

urlpatterns = [


    # ==================== AUTHENTICATION ====================
    path('auth/', include([
        path('register/', views.register, name='register'),
        path('login/', views.user_login, name='login'),
        path('logout/', views.user_logout, name='logout'),
        # Future: Password reset, email verification, etc.
    ])),
    
    # ==================== CUSTOMER DASHBOARD ====================
    path('customer/', include([
        path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
        path('profile/', views.customer_profile, name='customer_profile'),
        path('transactions/', views.customer_transactions, name='customer_transactions'),
        path('transactions/<uuid:transaction_id>/', views.transaction_detail, name='transaction_detail'),
        
        # Face Registration
        path('face/', include([
            path('register/', views.face_registration, name='face_registration'),
            path('delete/', views.face_delete, name='face_delete'),
        ])),
        
        # Payment Accounts
        path('payments/', include([
            path('', views.payment_accounts, name='payment_accounts'),
            path('add/', views.add_payment_account, name='add_payment_account'),
            path('delete/<uuid:account_id>/', views.delete_payment_account, name='delete_payment_account'),
        ])),
        
        # Loyalty Program
        path('loyalty/', views.loyalty_dashboard, name='loyalty_dashboard'),
    ])),
    
    # ==================== SHOPPING ====================
    path('shop/', include([
        # Stores
        path('stores/', views.stores, name='stores'),
        path('stores/<uuid:store_id>/', views.store_detail, name='store_detail'),
        
        # Products
        path('products/', views.products, name='products'),
        path('products/<uuid:product_id>/', views.product_detail, name='product_detail'),
        
        # Shopping Session
        path('session/start/<uuid:store_id>/', views.start_shopping_session, name='start_shopping_session'),
        path('session/<uuid:session_id>/', views.shopping_session, name='shopping_session'),
        
        # Cart Management
        path('session/<uuid:session_id>/add/<uuid:product_id>/', views.add_to_cart, name='add_to_cart'),
        path('session/<uuid:session_id>/update/<uuid:cart_item_id>/', views.update_cart_item, name='update_cart_item'),
        path('session/<uuid:session_id>/remove/<uuid:cart_item_id>/', views.remove_from_cart, name='remove_from_cart'),
        
        # Checkout
        path('session/<uuid:session_id>/checkout/', views.checkout, name='checkout'),
        
        # Promotions
        path('promotions/', views.promotions_list, name='promotions_list'),
    ])),
    
    # ==================== STAFF/ADMIN DASHBOARD ====================
    path('dashboard/', include([
        path('', views.dashboard, name='dashboard'),
        path('analytics/', views.analytics, name='analytics'),
        
        # Store Management
        path('stores/', views.manage_stores, name='manage_stores'),
        path('stores/<uuid:store_id>/inventory/', views.manage_inventory, name='manage_inventory'),
        
        # Product Management
        path('products/', views.manage_products, name='manage_products'),
        
        # Customer Management
        path('customers/', views.customers_list, name='customers_list'),
        
        # Security
        path('security/alerts/', views.security_alerts_view, name='security_alerts'),
    ])),
    
    # ==================== API ENDPOINTS ====================
    path('api/v1/', include([
        # Face Recognition
        path('face/verify/', views.api_face_verify, name='api_face_verify'),
        
        # Store Status
        path('stores/<uuid:store_id>/status/', views.api_store_status, name='api_store_status'),
        
        # Product Availability
        path('products/<uuid:product_id>/availability/<uuid:store_id>/', 
             views.api_product_availability, name='api_product_availability'),
        
        # Future API endpoints:
        # - Shopping session management
        # - Transaction processing
        # - Payment gateway callbacks
        # - M-Pesa STK Push callbacks
        # - Real-time notifications
    ])),
]
