"""
BiashAI - Face Recognition Shopping System
Django Models for Kenya Market

This file contains all the models needed for a comprehensive
face recognition-based shopping system.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
import uuid


# ==================== USER MANAGEMENT ====================

class CustomUser(AbstractUser):
    """
    Extended User model with Kenyan market specifics
    """
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone_number = models.CharField(max_length=15, unique=True)  # For M-Pesa integration
    id_number = models.CharField(max_length=20, unique=True, null=True, blank=True)  # National ID
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', null=True, blank=True)
    is_verified = models.BooleanField(default=False)
    kyc_verified = models.BooleanField(default=False)  # Know Your Customer verification
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return f"{self.username} - {self.phone_number}"


class FacialData(models.Model):
    """
    Stores facial recognition data for each user
    Uses encoding/embedding approach for privacy and security
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='facial_data')
    
    # Store facial embeddings (encrypted) - actual implementation would use binary field
    face_encoding = models.TextField()  # Base64 encoded facial features
    face_image_sample = models.ImageField(upload_to='face_samples/', null=True, blank=True)
    
    # Metadata
    registration_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    confidence_threshold = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=95.00,
        validators=[MinValueValidator(50.00), MaxValueValidator(100.00)]
    )
    
    # Security
    failed_recognition_attempts = models.IntegerField(default=0)
    last_recognition_attempt = models.DateTimeField(null=True, blank=True)
    is_locked = models.BooleanField(default=False)  # Lock after too many failed attempts
    
    class Meta:
        db_table = 'facial_data'
        verbose_name = _('Facial Data')
        verbose_name_plural = _('Facial Data')
    
    def __str__(self):
        return f"Face data for {self.user.username}"


class PaymentAccount(models.Model):
    """
    Manages payment accounts linked to users
    Supports M-Pesa, bank cards, and other Kenyan payment methods
    """
    PAYMENT_METHOD_CHOICES = [
        ('MPESA', 'M-Pesa'),
        ('AIRTEL', 'Airtel Money'),
        ('TKASH', 'T-Kash'),
        ('CARD', 'Debit/Credit Card'),
        ('BANK', 'Bank Account'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_accounts')
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    
    # Account details (encrypted in production)
    account_number = models.CharField(max_length=100)  # Phone number or card number
    account_name = models.CharField(max_length=200)
    
    # For mobile money
    provider_reference = models.CharField(max_length=100, null=True, blank=True)
    
    # Status
    is_primary = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # Limits (in KES)
    daily_limit = models.DecimalField(max_digits=10, decimal_places=2, default=50000.00)
    transaction_limit = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_accounts'
        verbose_name = _('Payment Account')
        verbose_name_plural = _('Payment Accounts')
        unique_together = ['user', 'account_number']
    
    def __str__(self):
        return f"{self.user.username} - {self.payment_method} - {self.account_number[-4:]}"


# ==================== STORE MANAGEMENT ====================

class County(models.Model):
    """
    Kenya's 47 counties for location management
    """
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True)
    
    class Meta:
        db_table = 'counties'
        verbose_name = _('County')
        verbose_name_plural = _('Counties')
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Store(models.Model):
    """
    Physical store locations
    """
    STORE_TYPE_CHOICES = [
        ('UNMANNED', 'Fully Automated (Unmanned)'),
        ('HYBRID', 'Hybrid (Staff + Automation)'),
        ('ASSISTED', 'Staff Assisted with Face Pay'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    store_code = models.CharField(max_length=20, unique=True)
    store_type = models.CharField(max_length=20, choices=STORE_TYPE_CHOICES)
    
    # Location
    county = models.ForeignKey(County, on_delete=models.PROTECT, related_name='stores')
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Contact
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    
    # Operational details
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_24_hours = models.BooleanField(default=False)
    
    # Status
    is_active = models.BooleanField(default=True)
    date_opened = models.DateField()
    
    # Manager
    manager = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='managed_stores'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stores'
        verbose_name = _('Store')
        verbose_name_plural = _('Stores')
    
    def __str__(self):
        return f"{self.name} ({self.store_code})"


class Camera(models.Model):
    """
    Cameras installed in stores for face recognition and product tracking
    """
    CAMERA_TYPE_CHOICES = [
        ('ENTRY', 'Entry/Exit Camera'),
        ('SHELF', 'Shelf Monitoring Camera'),
        ('CHECKOUT', 'Checkout Camera'),
        ('SECURITY', 'Security Camera'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='cameras')
    camera_code = models.CharField(max_length=50, unique=True)
    camera_type = models.CharField(max_length=20, choices=CAMERA_TYPE_CHOICES)
    
    # Technical details
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(default=554)
    stream_url = models.URLField()
    
    # Location within store
    location_description = models.CharField(max_length=200)
    zone = models.CharField(max_length=50, null=True, blank=True)  # e.g., "Dairy Section", "Entrance A"
    
    # Status
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    last_ping = models.DateTimeField(null=True, blank=True)
    
    # Maintenance
    installation_date = models.DateField()
    last_maintenance = models.DateField(null=True, blank=True)
    next_maintenance = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cameras'
        verbose_name = _('Camera')
        verbose_name_plural = _('Cameras')
    
    def __str__(self):
        return f"{self.camera_code} - {self.store.name}"


# ==================== PRODUCT MANAGEMENT ====================

class ProductCategory(models.Model):
    """
    Product categories (hierarchical)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True, 
        related_name='subcategories'
    )
    image = models.ImageField(upload_to='categories/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'product_categories'
        verbose_name = _('Product Category')
        verbose_name_plural = _('Product Categories')
        ordering = ['name']
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name


class Product(models.Model):
    """
    Products available in stores
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    
    # Categorization
    category = models.ForeignKey(
        ProductCategory, 
        on_delete=models.PROTECT, 
        related_name='products'
    )
    
    # Identifiers
    barcode = models.CharField(max_length=100, unique=True)
    sku = models.CharField(max_length=100, unique=True)
    
    # Pricing (in KES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # VAT
    vat_rate = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=16.00,  # Kenya VAT standard rate
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    
    # Product details
    brand = models.CharField(max_length=100, null=True, blank=True)
    manufacturer = models.CharField(max_length=200, null=True, blank=True)
    country_of_origin = models.CharField(max_length=100, default='Kenya')
    
    # Physical attributes
    weight = models.DecimalField(
        max_digits=10, 
        decimal_places=3, 
        null=True, 
        blank=True,
        help_text="Weight in kg"
    )
    dimensions = models.CharField(max_length=100, null=True, blank=True)  # L x W x H
    
    # Media
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    
    # AI/Computer Vision attributes
    visual_signature = models.TextField(
        null=True, 
        blank=True,
        help_text="Encoded visual features for product recognition"
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = _('Product')
        verbose_name_plural = _('Products')
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.barcode})"
    
    @property
    def price_with_vat(self):
        """Calculate price including VAT"""
        return self.price * (1 + self.vat_rate / 100)


class StoreInventory(models.Model):
    """
    Product inventory per store
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='inventory')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='store_inventory')
    
    # Stock levels
    quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    reorder_level = models.IntegerField(default=10)
    max_stock_level = models.IntegerField(default=100)
    
    # Location in store
    shelf_location = models.CharField(max_length=100, null=True, blank=True)
    aisle = models.CharField(max_length=50, null=True, blank=True)
    
    # Stock status
    is_available = models.BooleanField(default=True)
    last_restocked = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'store_inventory'
        verbose_name = _('Store Inventory')
        verbose_name_plural = _('Store Inventories')
        unique_together = ['store', 'product']
    
    def __str__(self):
        return f"{self.product.name} @ {self.store.name} - Qty: {self.quantity}"
    
    @property
    def needs_reorder(self):
        """Check if stock needs reordering"""
        return self.quantity <= self.reorder_level


# ==================== SHOPPING SESSION MANAGEMENT ====================

class ShoppingSession(models.Model):
    """
    Tracks a customer's shopping session in a store
    """
    SESSION_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session_code = models.CharField(max_length=50, unique=True)
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='shopping_sessions')
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='shopping_sessions')
    
    # Session timing
    entry_time = models.DateTimeField(auto_now_add=True)
    exit_time = models.DateTimeField(null=True, blank=True)
    
    # Face recognition
    entry_camera = models.ForeignKey(
        Camera, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='entry_sessions'
    )
    entry_face_confidence = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    
    # Status
    status = models.CharField(max_length=20, choices=SESSION_STATUS_CHOICES, default='ACTIVE')
    
    # Notes
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shopping_sessions'
        verbose_name = _('Shopping Session')
        verbose_name_plural = _('Shopping Sessions')
        ordering = ['-entry_time']
    
    def __str__(self):
        return f"{self.session_code} - {self.user.username} @ {self.store.name}"


class ShoppingCart(models.Model):
    """
    Items in customer's virtual cart during shopping session
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        ShoppingSession, 
        on_delete=models.CASCADE, 
        related_name='cart_items'
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Quantity
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    # Price snapshot (in case of price changes during session)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Detection metadata
    detected_by_camera = models.ForeignKey(
        Camera, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    detection_confidence = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    
    added_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'shopping_cart'
        verbose_name = _('Shopping Cart Item')
        verbose_name_plural = _('Shopping Cart Items')
        unique_together = ['session', 'product']
    
    def __str__(self):
        return f"{self.product.name} x{self.quantity} - {self.session.session_code}"
    
    @property
    def subtotal(self):
        """Calculate subtotal for this cart item"""
        return self.unit_price * self.quantity


# ==================== TRANSACTION MANAGEMENT ====================

class Transaction(models.Model):
    """
    Payment transactions
    """
    TRANSACTION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('MPESA', 'M-Pesa'),
        ('AIRTEL', 'Airtel Money'),
        ('TKASH', 'T-Kash'),
        ('CARD', 'Debit/Credit Card'),
        ('BANK', 'Bank Account'),
        ('CASH', 'Cash'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_code = models.CharField(max_length=100, unique=True)
    
    # Session and user
    session = models.OneToOneField(
        ShoppingSession, 
        on_delete=models.PROTECT, 
        related_name='transaction'
    )
    user = models.ForeignKey(CustomUser, on_delete=models.PROTECT, related_name='transactions')
    store = models.ForeignKey(Store, on_delete=models.PROTECT, related_name='transactions')
    
    # Payment details
    payment_account = models.ForeignKey(
        PaymentAccount, 
        on_delete=models.PROTECT, 
        related_name='transactions'
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    
    # Amounts (in KES)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Provider details
    provider_transaction_id = models.CharField(max_length=200, null=True, blank=True)
    provider_response = models.TextField(null=True, blank=True)
    
    # Face recognition at checkout
    checkout_camera = models.ForeignKey(
        Camera, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='checkout_transactions'
    )
    face_recognition_confidence = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    
    # Status
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS_CHOICES, default='PENDING')
    
    # Timestamps
    initiated_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Receipt
    receipt_number = models.CharField(max_length=100, unique=True, null=True, blank=True)
    receipt_url = models.URLField(null=True, blank=True)
    
    # Notes
    notes = models.TextField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'transactions'
        verbose_name = _('Transaction')
        verbose_name_plural = _('Transactions')
        ordering = ['-initiated_at']
        indexes = [
            models.Index(fields=['-initiated_at']),
            models.Index(fields=['status']),
            models.Index(fields=['user', '-initiated_at']),
        ]
    
    def __str__(self):
        return f"{self.transaction_code} - KES {self.total_amount} - {self.status}"


class TransactionItem(models.Model):
    """
    Individual items in a transaction (for receipt and reporting)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.CASCADE, 
        related_name='items'
    )
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    
    # Item details (snapshot at time of purchase)
    product_name = models.CharField(max_length=200)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2)
    
    # Calculated fields
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    vat_amount = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'transaction_items'
        verbose_name = _('Transaction Item')
        verbose_name_plural = _('Transaction Items')
    
    def __str__(self):
        return f"{self.product_name} x{self.quantity} - {self.transaction.transaction_code}"


# ==================== SECURITY & AUDIT ====================

class FaceRecognitionLog(models.Model):
    """
    Logs all face recognition attempts for security and auditing
    """
    RECOGNITION_TYPE_CHOICES = [
        ('ENTRY', 'Store Entry'),
        ('CHECKOUT', 'Checkout'),
        ('VERIFICATION', 'Identity Verification'),
    ]
    
    RESULT_CHOICES = [
        ('SUCCESS', 'Successful'),
        ('FAILED', 'Failed'),
        ('REJECTED', 'Rejected (Low Confidence)'),
        ('BLOCKED', 'Blocked (Account Locked)'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='recognition_logs',
        null=True,
        blank=True
    )
    camera = models.ForeignKey(Camera, on_delete=models.SET_NULL, null=True)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='recognition_logs')
    
    # Recognition details
    recognition_type = models.CharField(max_length=20, choices=RECOGNITION_TYPE_CHOICES)
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    confidence_score = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(0.00), MaxValueValidator(100.00)]
    )
    
    # Associated records
    session = models.ForeignKey(
        ShoppingSession, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Technical details
    processing_time_ms = models.IntegerField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'face_recognition_logs'
        verbose_name = _('Face Recognition Log')
        verbose_name_plural = _('Face Recognition Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['result']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else "Unknown"
        return f"{self.recognition_type} - {user_info} - {self.result}"


class SecurityAlert(models.Model):
    """
    Security alerts and incidents
    """
    ALERT_TYPE_CHOICES = [
        ('FRAUD', 'Suspected Fraud'),
        ('MULTIPLE_FAIL', 'Multiple Failed Recognitions'),
        ('UNUSUAL_ACTIVITY', 'Unusual Activity'),
        ('SYSTEM_ERROR', 'System Error'),
        ('THEFT', 'Suspected Theft'),
        ('UNAUTHORIZED', 'Unauthorized Access'),
    ]
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('INVESTIGATING', 'Under Investigation'),
        ('RESOLVED', 'Resolved'),
        ('FALSE_ALARM', 'False Alarm'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_code = models.CharField(max_length=50, unique=True)
    
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPE_CHOICES)
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')
    
    # Related entities
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name='security_alerts',
        null=True,
        blank=True
    )
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='security_alerts')
    session = models.ForeignKey(
        ShoppingSession, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    # Alert details
    description = models.TextField()
    resolution_notes = models.TextField(null=True, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_alerts'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'security_alerts'
        verbose_name = _('Security Alert')
        verbose_name_plural = _('Security Alerts')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_code} - {self.alert_type} - {self.severity}"


class AuditLog(models.Model):
    """
    Comprehensive audit trail for compliance
    """
    ACTION_CHOICES = [
        ('CREATE', 'Create'),
        ('UPDATE', 'Update'),
        ('DELETE', 'Delete'),
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('PAYMENT', 'Payment'),
        ('REFUND', 'Refund'),
        ('ACCESS', 'Access'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='audit_logs'
    )
    
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_name = models.CharField(max_length=100)
    object_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Details
    changes = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]
    
    def __str__(self):
        user_info = self.user.username if self.user else "System"
        return f"{user_info} - {self.action} - {self.model_name}"


# ==================== ANALYTICS & REPORTING ====================

class DailySalesReport(models.Model):
    """
    Aggregated daily sales data per store
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, related_name='daily_reports')
    report_date = models.DateField()
    
    # Sales metrics
    total_transactions = models.IntegerField(default=0)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    total_vat = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Customer metrics
    unique_customers = models.IntegerField(default=0)
    new_customers = models.IntegerField(default=0)
    
    # Product metrics
    total_items_sold = models.IntegerField(default=0)
    average_basket_size = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    # Payment methods breakdown (JSON field)
    payment_breakdown = models.JSONField(default=dict)
    
    # Face recognition stats
    successful_recognitions = models.IntegerField(default=0)
    failed_recognitions = models.IntegerField(default=0)
    average_confidence = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        default=0.00
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_sales_reports'
        verbose_name = _('Daily Sales Report')
        verbose_name_plural = _('Daily Sales Reports')
        unique_together = ['store', 'report_date']
        ordering = ['-report_date']
    
    def __str__(self):
        return f"{self.store.name} - {self.report_date}"


class CustomerBehavior(models.Model):
    """
    Track customer shopping patterns and preferences
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='behavior')
    
    # Shopping frequency
    total_visits = models.IntegerField(default=0)
    total_purchases = models.IntegerField(default=0)
    total_spent = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    # Preferences
    favorite_store = models.ForeignKey(
        Store, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='favorite_customers'
    )
    favorite_categories = models.JSONField(default=list)  # List of category IDs
    
    # Timing patterns
    preferred_shopping_time = models.CharField(max_length=20, null=True, blank=True)
    average_session_duration = models.IntegerField(default=0)  # in minutes
    
    # Last activity
    last_visit = models.DateTimeField(null=True, blank=True)
    last_purchase = models.DateTimeField(null=True, blank=True)
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'customer_behavior'
        verbose_name = _('Customer Behavior')
        verbose_name_plural = _('Customer Behaviors')
    
    def __str__(self):
        return f"Behavior profile for {self.user.username}"


# ==================== PROMOTIONAL & LOYALTY ====================

class Promotion(models.Model):
    """
    Promotional campaigns and discounts
    """
    DISCOUNT_TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage Discount'),
        ('FIXED', 'Fixed Amount Discount'),
        ('BOGO', 'Buy One Get One'),
        ('BUNDLE', 'Bundle Offer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Applicability
    applicable_stores = models.ManyToManyField(Store, related_name='promotions', blank=True)
    applicable_products = models.ManyToManyField(Product, related_name='promotions', blank=True)
    applicable_categories = models.ManyToManyField(
        ProductCategory, 
        related_name='promotions', 
        blank=True
    )
    
    # Conditions
    minimum_purchase = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00
    )
    maximum_discount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True
    )
    
    # Validity
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    
    # Usage limits
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_per_customer = models.IntegerField(default=1)
    times_used = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'promotions'
        verbose_name = _('Promotion')
        verbose_name_plural = _('Promotions')
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class LoyaltyProgram(models.Model):
    """
    Loyalty points and rewards program
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='loyalty')
    
    # Points
    total_points_earned = models.IntegerField(default=0)
    total_points_redeemed = models.IntegerField(default=0)
    current_balance = models.IntegerField(default=0)
    
    # Tier system
    TIER_CHOICES = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
    ]
    current_tier = models.CharField(max_length=10, choices=TIER_CHOICES, default='BRONZE')
    
    # Membership
    member_since = models.DateField(auto_now_add=True)
    last_activity = models.DateTimeField(null=True, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'loyalty_programs'
        verbose_name = _('Loyalty Program')
        verbose_name_plural = _('Loyalty Programs')
    
    def __str__(self):
        return f"{self.user.username} - {self.current_tier} - {self.current_balance} pts"


class LoyaltyTransaction(models.Model):
    """
    Individual loyalty point transactions
    """
    TRANSACTION_TYPE_CHOICES = [
        ('EARN', 'Points Earned'),
        ('REDEEM', 'Points Redeemed'),
        ('EXPIRE', 'Points Expired'),
        ('ADJUST', 'Manual Adjustment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    loyalty_program = models.ForeignKey(
        LoyaltyProgram, 
        on_delete=models.CASCADE, 
        related_name='point_transactions'
    )
    
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    points = models.IntegerField()
    balance_after = models.IntegerField()
    
    # Related transaction (if applicable)
    related_transaction = models.ForeignKey(
        Transaction, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='loyalty_transactions'
    )
    
    description = models.CharField(max_length=200)
    
    # Expiry (for earned points)
    expires_at = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'loyalty_transactions'
        verbose_name = _('Loyalty Transaction')
        verbose_name_plural = _('Loyalty Transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        sign = '+' if self.transaction_type == 'EARN' else '-'
        return f"{self.loyalty_program.user.username} - {sign}{self.points} pts"