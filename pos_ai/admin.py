"""
BiashAI - Django Admin Configuration
Professional admin interface for managing the face recognition shopping system
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    CustomUser, FacialData, PaymentAccount, County, Store, Camera,
    ProductCategory, Product, StoreInventory, ShoppingSession, ShoppingCart,
    Transaction, TransactionItem, FaceRecognitionLog, SecurityAlert, AuditLog,
    DailySalesReport, CustomerBehavior, Promotion, LoyaltyProgram, LoyaltyTransaction
)


# ==================== USER MANAGEMENT ====================

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'phone_number', 'email', 'is_verified', 'kyc_verified', 'is_active', 'created_at']
    list_filter = ['is_verified', 'kyc_verified', 'is_active', 'is_staff', 'gender', 'created_at']
    search_fields = ['username', 'email', 'phone_number', 'id_number', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'username', 'email', 'phone_number')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'gender', 'id_number', 'profile_image')
        }),
        ('Verification Status', {
            'fields': ('is_verified', 'kyc_verified', 'is_active', 'is_staff', 'is_superuser')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_login'),
            'classes': ('collapse',)
        }),
    )
    
    def has_facial_data(self, obj):
        return hasattr(obj, 'facial_data')
    has_facial_data.boolean = True
    has_facial_data.short_description = 'Face Registered'


@admin.register(FacialData)
class FacialDataAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_active', 'confidence_threshold', 'failed_recognition_attempts', 
                    'is_locked', 'registration_date']
    list_filter = ['is_active', 'is_locked', 'registration_date']
    search_fields = ['user__username', 'user__phone_number', 'user__email']
    readonly_fields = ['id', 'registration_date', 'last_updated', 'last_recognition_attempt']
    
    fieldsets = (
        ('User Information', {
            'fields': ('id', 'user', 'face_image_sample')
        }),
        ('Recognition Settings', {
            'fields': ('face_encoding', 'confidence_threshold', 'is_active')
        }),
        ('Security', {
            'fields': ('failed_recognition_attempts', 'last_recognition_attempt', 'is_locked')
        }),
        ('Timestamps', {
            'fields': ('registration_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentAccount)
class PaymentAccountAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_method', 'masked_account_number', 'is_primary', 
                    'is_verified', 'is_active', 'created_at']
    list_filter = ['payment_method', 'is_primary', 'is_verified', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__phone_number', 'account_number', 'account_name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    def masked_account_number(self, obj):
        if len(obj.account_number) > 4:
            return f"****{obj.account_number[-4:]}"
        return "****"
    masked_account_number.short_description = 'Account Number'


# ==================== STORE MANAGEMENT ====================

@admin.register(County)
class CountyAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'store_count']
    search_fields = ['name', 'code']
    
    def store_count(self, obj):
        return obj.stores.count()
    store_count.short_description = 'Number of Stores'


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ['name', 'store_code', 'store_type', 'county', 'manager', 'is_active', 
                    'date_opened']
    list_filter = ['store_type', 'county', 'is_active', 'is_24_hours', 'date_opened']
    search_fields = ['name', 'store_code', 'address', 'phone_number']
    readonly_fields = ['id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'store_code', 'store_type')
        }),
        ('Location', {
            'fields': ('county', 'address', 'latitude', 'longitude')
        }),
        ('Contact', {
            'fields': ('phone_number', 'email')
        }),
        ('Operations', {
            'fields': ('opening_time', 'closing_time', 'is_24_hours', 'is_active', 
                      'date_opened', 'manager')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ['camera_code', 'store', 'camera_type', 'is_active', 'is_online', 
                    'location_description', 'last_ping']
    list_filter = ['camera_type', 'is_active', 'is_online', 'store', 'installation_date']
    search_fields = ['camera_code', 'store__name', 'location_description', 'ip_address']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_ping']
    
    def status_indicator(self, obj):
        if obj.is_online:
            return format_html('<span style="color: green;">●</span> Online')
        return format_html('<span style="color: red;">●</span> Offline')
    status_indicator.short_description = 'Status'


# ==================== PRODUCT MANAGEMENT ====================

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'product_count', 'is_active']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id']
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'barcode', 'sku', 'category', 'price', 'price_with_vat', 
                    'is_active', 'is_featured']
    list_filter = ['category', 'is_active', 'is_featured', 'brand', 'country_of_origin', 'created_at']
    search_fields = ['name', 'barcode', 'sku', 'brand', 'manufacturer']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['id', 'created_at', 'updated_at', 'price_with_vat']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'name', 'slug', 'description', 'category')
        }),
        ('Identifiers', {
            'fields': ('barcode', 'sku')
        }),
        ('Pricing', {
            'fields': ('price', 'cost_price', 'vat_rate', 'price_with_vat')
        }),
        ('Product Details', {
            'fields': ('brand', 'manufacturer', 'country_of_origin', 'weight', 'dimensions')
        }),
        ('Media & AI', {
            'fields': ('image', 'visual_signature')
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StoreInventory)
class StoreInventoryAdmin(admin.ModelAdmin):
    list_display = ['product', 'store', 'quantity', 'needs_reorder_indicator', 'shelf_location', 
                    'is_available', 'last_restocked']
    list_filter = ['store', 'is_available', 'product__category', 'last_restocked']
    search_fields = ['product__name', 'product__barcode', 'store__name', 'shelf_location']
    readonly_fields = ['id', 'created_at', 'updated_at', 'needs_reorder']
    
    def needs_reorder_indicator(self, obj):
        if obj.needs_reorder:
            return format_html('<span style="color: red; font-weight: bold;">⚠ Reorder</span>')
        return format_html('<span style="color: green;">✓ OK</span>')
    needs_reorder_indicator.short_description = 'Stock Status'


# ==================== SHOPPING SESSION ====================

@admin.register(ShoppingSession)
class ShoppingSessionAdmin(admin.ModelAdmin):
    list_display = ['session_code', 'user', 'store', 'status', 'entry_time', 'exit_time', 
                    'entry_face_confidence']
    list_filter = ['status', 'store', 'entry_time']
    search_fields = ['session_code', 'user__username', 'user__phone_number', 'store__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'entry_time'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['session', 'product', 'quantity', 'unit_price', 'subtotal', 'added_at']
    list_filter = ['session__store', 'added_at']
    search_fields = ['session__session_code', 'product__name', 'session__user__username']
    readonly_fields = ['id', 'added_at', 'updated_at', 'subtotal']


# ==================== TRANSACTIONS ====================

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_code', 'user', 'store', 'total_amount', 'payment_method', 
                    'status', 'initiated_at']
    list_filter = ['status', 'payment_method', 'store', 'initiated_at']
    search_fields = ['transaction_code', 'user__username', 'user__phone_number', 
                     'receipt_number', 'provider_transaction_id']
    readonly_fields = ['id', 'created_at', 'updated_at', 'initiated_at', 'completed_at']
    date_hierarchy = 'initiated_at'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('id', 'transaction_code', 'receipt_number')
        }),
        ('Parties', {
            'fields': ('user', 'store', 'session')
        }),
        ('Payment Details', {
            'fields': ('payment_account', 'payment_method', 'provider_transaction_id')
        }),
        ('Amounts', {
            'fields': ('subtotal', 'vat_amount', 'discount_amount', 'total_amount')
        }),
        ('Face Recognition', {
            'fields': ('checkout_camera', 'face_recognition_confidence')
        }),
        ('Status', {
            'fields': ('status', 'provider_response', 'notes')
        }),
        ('Timestamps', {
            'fields': ('initiated_at', 'completed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def colored_status(self, obj):
        colors = {
            'COMPLETED': 'green',
            'PENDING': 'orange',
            'PROCESSING': 'blue',
            'FAILED': 'red',
            'REFUNDED': 'purple',
            'CANCELLED': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    colored_status.short_description = 'Status'


@admin.register(TransactionItem)
class TransactionItemAdmin(admin.ModelAdmin):
    list_display = ['transaction', 'product_name', 'quantity', 'unit_price', 'total']
    list_filter = ['transaction__store', 'created_at']
    search_fields = ['transaction__transaction_code', 'product_name', 'product__name']
    readonly_fields = ['id', 'created_at']


# ==================== SECURITY & AUDIT ====================

@admin.register(FaceRecognitionLog)
class FaceRecognitionLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'recognition_type', 'result', 'confidence_score', 'camera', 
                    'store', 'timestamp']
    list_filter = ['recognition_type', 'result', 'store', 'timestamp']
    search_fields = ['user__username', 'user__phone_number', 'camera__camera_code']
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'
    
    def colored_result(self, obj):
        colors = {
            'SUCCESS': 'green',
            'FAILED': 'orange',
            'REJECTED': 'red',
            'BLOCKED': 'darkred',
        }
        color = colors.get(obj.result, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_result_display()
        )
    colored_result.short_description = 'Result'


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['alert_code', 'alert_type', 'severity', 'status', 'store', 'user', 
                    'created_at', 'assigned_to']
    list_filter = ['alert_type', 'severity', 'status', 'store', 'created_at']
    search_fields = ['alert_code', 'user__username', 'store__name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'resolved_at']
    date_hierarchy = 'created_at'
    
    def severity_indicator(self, obj):
        colors = {
            'LOW': 'blue',
            'MEDIUM': 'orange',
            'HIGH': 'red',
            'CRITICAL': 'darkred',
        }
        color = colors.get(obj.severity, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_severity_display()
        )
    severity_indicator.short_description = 'Severity'


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'action', 'model_name', 'object_id', 'ip_address', 'timestamp']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['user__username', 'model_name', 'object_id', 'ip_address']
    readonly_fields = ['id', 'timestamp']
    date_hierarchy = 'timestamp'


# ==================== ANALYTICS ====================

@admin.register(DailySalesReport)
class DailySalesReportAdmin(admin.ModelAdmin):
    list_display = ['store', 'report_date', 'total_transactions', 'total_revenue', 
                    'unique_customers', 'average_basket_size']
    list_filter = ['store', 'report_date']
    search_fields = ['store__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'report_date'


@admin.register(CustomerBehavior)
class CustomerBehaviorAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_visits', 'total_purchases', 'total_spent', 'favorite_store', 
                    'last_visit']
    list_filter = ['favorite_store', 'last_visit', 'last_purchase']
    search_fields = ['user__username', 'user__phone_number']
    readonly_fields = ['updated_at']


# ==================== PROMOTIONAL ====================

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'discount_type', 'discount_value', 'start_date', 
                    'end_date', 'is_active', 'times_used']
    list_filter = ['discount_type', 'is_active', 'start_date', 'end_date']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['id', 'times_used', 'created_at', 'updated_at']
    filter_horizontal = ['applicable_stores', 'applicable_products', 'applicable_categories']


@admin.register(LoyaltyProgram)
class LoyaltyProgramAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_tier', 'current_balance', 'total_points_earned', 
                    'total_points_redeemed', 'is_active']
    list_filter = ['current_tier', 'is_active', 'member_since']
    search_fields = ['user__username', 'user__phone_number']
    readonly_fields = ['id', 'member_since', 'created_at', 'updated_at']


@admin.register(LoyaltyTransaction)
class LoyaltyTransactionAdmin(admin.ModelAdmin):
    list_display = ['loyalty_program', 'transaction_type', 'points', 'balance_after', 
                    'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['loyalty_program__user__username', 'description']
    readonly_fields = ['id', 'created_at']
    date_hierarchy = 'created_at'


# Customize Admin Site
admin.site.site_header = "BiashAI Administration"
admin.site.site_title = "BiashAI Admin"
admin.site.index_title = "Welcome to BiashAI Management System"