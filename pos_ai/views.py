"""
BiashAI - Django Views
Comprehensive views for face recognition shopping system
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Sum, Count, Avg, F
from django.utils import timezone
from django.core.paginator import Paginator
from django.db import transaction
from decimal import Decimal
from datetime import datetime, timedelta
import json
import base64
import uuid

from .models import (
    CustomUser, FacialData, PaymentAccount, County, Store, Camera,
    ProductCategory, Product, StoreInventory, ShoppingSession, ShoppingCart,
    Transaction, TransactionItem, FaceRecognitionLog, SecurityAlert, AuditLog,
    DailySalesReport, CustomerBehavior, Promotion, LoyaltyProgram, LoyaltyTransaction
)


# ==================== HELPER FUNCTIONS ====================

def is_staff_or_superuser(user):
    """Check if user is staff or superuser"""
    return user.is_staff or user.is_superuser


def log_audit(user, action, model_name, object_id=None, changes=None, request=None):
    """Create audit log entry"""
    ip_address = None
    user_agent = None
    
    if request:
        ip_address = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
    
    AuditLog.objects.create(
        user=user,
        action=action,
        model_name=model_name,
        object_id=str(object_id) if object_id else None,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )


def create_security_alert(alert_type, severity, store, user=None, description="", 
                         session=None, transaction_obj=None):
    """Create security alert"""
    alert_code = f"ALERT-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    SecurityAlert.objects.create(
        alert_code=alert_code,
        alert_type=alert_type,
        severity=severity,
        store=store,
        user=user,
        session=session,
        transaction=transaction_obj,
        description=description
    )


# ==================== AUTHENTICATION VIEWS ====================

def home(request):
    """Landing page"""
    context = {
        'total_stores': Store.objects.filter(is_active=True).count(),
        'total_products': Product.objects.filter(is_active=True).count(),
        'active_sessions': ShoppingSession.objects.filter(status='ACTIVE').count(),
    }
    return render(request, 'home.html', context)


def register(request):
    """User registration"""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        id_number = request.POST.get('id_number')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        
        # Validation
        if password != password_confirm:
            messages.error(request, 'Passwords do not match')
            return render(request, 'auth/register.html')
        
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'auth/register.html')
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return render(request, 'auth/register.html')
        
        if CustomUser.objects.filter(phone_number=phone_number).exists():
            messages.error(request, 'Phone number already registered')
            return render(request, 'auth/register.html')
        
        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            id_number=id_number,
            date_of_birth=date_of_birth if date_of_birth else None,
            gender=gender
        )
        
        log_audit(user, 'CREATE', 'CustomUser', user.id, request=request)
        
        messages.success(request, 'Registration successful! Please login.')
        return redirect('login')
    
    return render(request, 'auth/register.html')


def user_login(request):
    """User login"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            log_audit(user, 'LOGIN', 'CustomUser', user.id, request=request)
            
            messages.success(request, f'Welcome back, {user.first_name}!')
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            
            if user.is_staff:
                return redirect('dashboard')
            return redirect('customer_dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'auth/login.html')


@login_required
def user_logout(request):
    """User logout"""
    log_audit(request.user, 'LOGOUT', 'CustomUser', request.user.id, request=request)
    logout(request)
    messages.success(request, 'You have been logged out successfully')
    return redirect('home')


# ==================== CUSTOMER DASHBOARD ====================

@login_required
def customer_dashboard(request):
    """Customer main dashboard"""
    user = request.user
    
    # Get customer statistics
    total_purchases = Transaction.objects.filter(user=user, status='COMPLETED').count()
    total_spent = Transaction.objects.filter(
        user=user, 
        status='COMPLETED'
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Recent transactions
    recent_transactions = Transaction.objects.filter(user=user).order_by('-initiated_at')[:5]
    
    # Active session
    active_session = ShoppingSession.objects.filter(user=user, status='ACTIVE').first()
    
    # Loyalty info
    try:
        loyalty = user.loyalty
    except LoyaltyProgram.DoesNotExist:
        loyalty = None
    
    # Payment accounts
    payment_accounts = PaymentAccount.objects.filter(user=user, is_active=True)
    
    # Facial data status
    has_facial_data = hasattr(user, 'facial_data') and user.facial_data.is_active
    
    context = {
        'total_purchases': total_purchases,
        'total_spent': total_spent,
        'recent_transactions': recent_transactions,
        'active_session': active_session,
        'loyalty': loyalty,
        'payment_accounts': payment_accounts,
        'has_facial_data': has_facial_data,
    }
    
    return render(request, 'customer/dashboard.html', context)


@login_required
def customer_profile(request):
    """Customer profile management"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.phone_number = request.POST.get('phone_number', user.phone_number)
        user.gender = request.POST.get('gender', user.gender)
        
        if request.FILES.get('profile_image'):
            user.profile_image = request.FILES['profile_image']
        
        user.save()
        log_audit(user, 'UPDATE', 'CustomUser', user.id, request=request)
        
        messages.success(request, 'Profile updated successfully')
        return redirect('customer_profile')
    
    context = {
        'user': request.user
    }
    return render(request, 'customer/profile.html', context)


@login_required
def customer_transactions(request):
    """Customer transaction history"""
    transactions = Transaction.objects.filter(user=request.user).order_by('-initiated_at')
    
    # Pagination
    paginator = Paginator(transactions, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'customer/transactions.html', context)


@login_required
def transaction_detail(request, transaction_id):
    """Transaction detail view"""
    transaction_obj = get_object_or_404(Transaction, id=transaction_id, user=request.user)
    items = TransactionItem.objects.filter(transaction=transaction_obj)
    
    context = {
        'transaction': transaction_obj,
        'items': items,
    }
    return render(request, 'customer/transaction_detail.html', context)


# ==================== FACIAL RECOGNITION VIEWS ====================

@login_required
def face_registration(request):
    """Register facial data"""
    if request.method == 'POST':
        # This would integrate with actual face recognition library
        face_image = request.FILES.get('face_image')
        
        if not face_image:
            messages.error(request, 'Please upload a face image')
            return render(request, 'customer/face_registration.html')
        
        # In production, you would:
        # 1. Extract face encoding using face_recognition library
        # 2. Validate face quality
        # 3. Check for duplicates
        
        # For now, create dummy encoding
        dummy_encoding = base64.b64encode(face_image.read()).decode('utf-8')
        
        # Create or update facial data
        facial_data, created = FacialData.objects.update_or_create(
            user=request.user,
            defaults={
                'face_encoding': dummy_encoding,
                'face_image_sample': face_image,
                'is_active': True,
                'confidence_threshold': Decimal('95.00')
            }
        )
        
        log_audit(request.user, 'CREATE' if created else 'UPDATE', 
                 'FacialData', facial_data.id, request=request)
        
        messages.success(request, 'Face registered successfully!')
        return redirect('customer_dashboard')
    
    # Check if already registered
    has_facial_data = hasattr(request.user, 'facial_data')
    
    context = {
        'has_facial_data': has_facial_data,
    }
    return render(request, 'customer/face_registration.html', context)


@login_required
def face_delete(request):
    """Delete facial data"""
    if request.method == 'POST':
        try:
            facial_data = request.user.facial_data
            facial_data.delete()
            
            log_audit(request.user, 'DELETE', 'FacialData', request=request)
            messages.success(request, 'Facial data deleted successfully')
        except FacialData.DoesNotExist:
            messages.error(request, 'No facial data found')
        
        return redirect('customer_dashboard')
    
    return render(request, 'customer/face_delete_confirm.html')


# ==================== PAYMENT ACCOUNT VIEWS ====================

@login_required
def payment_accounts(request):
    """Manage payment accounts"""
    accounts = PaymentAccount.objects.filter(user=request.user)
    
    context = {
        'accounts': accounts,
    }
    return render(request, 'customer/payment_accounts.html', context)


@login_required
def add_payment_account(request):
    """Add new payment account"""
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')
        account_number = request.POST.get('account_number')
        account_name = request.POST.get('account_name')
        is_primary = request.POST.get('is_primary') == 'on'
        
        # If setting as primary, unset other primary accounts
        if is_primary:
            PaymentAccount.objects.filter(user=request.user, is_primary=True).update(
                is_primary=False
            )
        
        account = PaymentAccount.objects.create(
            user=request.user,
            payment_method=payment_method,
            account_number=account_number,
            account_name=account_name,
            is_primary=is_primary,
            is_verified=False,  # Would need verification in production
            is_active=True
        )
        
        log_audit(request.user, 'CREATE', 'PaymentAccount', account.id, request=request)
        
        messages.success(request, 'Payment account added successfully')
        return redirect('payment_accounts')
    
    context = {
        'payment_methods': PaymentAccount.PAYMENT_METHOD_CHOICES,
    }
    return render(request, 'customer/add_payment_account.html', context)


@login_required
def delete_payment_account(request, account_id):
    """Delete payment account"""
    account = get_object_or_404(PaymentAccount, id=account_id, user=request.user)
    
    if request.method == 'POST':
        log_audit(request.user, 'DELETE', 'PaymentAccount', account.id, request=request)
        account.delete()
        messages.success(request, 'Payment account deleted successfully')
        return redirect('payment_accounts')
    
    context = {
        'account': account,
    }
    return render(request, 'customer/delete_payment_account_confirm.html', context)


# ==================== SHOPPING VIEWS ====================

def stores(request):
    """List all stores"""
    stores_list = Store.objects.filter(is_active=True)
    
    # Filter by county
    county_id = request.GET.get('county')
    if county_id:
        stores_list = stores_list.filter(county_id=county_id)
    
    # Filter by store type
    store_type = request.GET.get('store_type')
    if store_type:
        stores_list = stores_list.filter(store_type=store_type)
    
    # Search
    search = request.GET.get('search')
    if search:
        stores_list = stores_list.filter(
            Q(name__icontains=search) | 
            Q(store_code__icontains=search) |
            Q(address__icontains=search)
        )
    
    counties = County.objects.all()
    
    context = {
        'stores': stores_list,
        'counties': counties,
        'store_types': Store.STORE_TYPE_CHOICES,
    }
    return render(request, 'shopping/stores.html', context)


def store_detail(request, store_id):
    """Store detail page"""
    store = get_object_or_404(Store, id=store_id, is_active=True)
    
    # Get available products in this store
    inventory = StoreInventory.objects.filter(
        store=store, 
        is_available=True,
        quantity__gt=0
    ).select_related('product', 'product__category')[:20]
    
    context = {
        'store': store,
        'inventory': inventory,
    }
    return render(request, 'shopping/store_detail.html', context)


def products(request):
    """Product catalog"""
    products_list = Product.objects.filter(is_active=True)
    
    # Filter by category
    category_id = request.GET.get('category')
    if category_id:
        products_list = products_list.filter(category_id=category_id)
    
    # Search
    search = request.GET.get('search')
    if search:
        products_list = products_list.filter(
            Q(name__icontains=search) |
            Q(barcode__icontains=search) |
            Q(brand__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(products_list, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    categories = ProductCategory.objects.filter(parent__isnull=True)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
    }
    return render(request, 'shopping/products.html', context)


def product_detail(request, product_id):
    """Product detail page"""
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Get stores where this product is available
    available_stores = StoreInventory.objects.filter(
        product=product,
        is_available=True,
        quantity__gt=0
    ).select_related('store')
    
    context = {
        'product': product,
        'available_stores': available_stores,
    }
    return render(request, 'shopping/product_detail.html', context)


@login_required
def start_shopping_session(request, store_id):
    """Start a shopping session at a store"""
    store = get_object_or_404(Store, id=store_id, is_active=True)
    
    # Check if user has facial data
    if not hasattr(request.user, 'facial_data') or not request.user.facial_data.is_active:
        messages.error(request, 'Please register your face first')
        return redirect('face_registration')
    
    # Check for existing active session
    active_session = ShoppingSession.objects.filter(
        user=request.user, 
        status='ACTIVE'
    ).first()
    
    if active_session:
        messages.warning(request, 'You already have an active shopping session')
        return redirect('shopping_session', session_id=active_session.id)
    
    # Create new session
    session_code = f"SHOP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    # Get entry camera (first ENTRY camera at store)
    entry_camera = Camera.objects.filter(
        store=store, 
        camera_type='ENTRY',
        is_active=True
    ).first()
    
    session = ShoppingSession.objects.create(
        session_code=session_code,
        user=request.user,
        store=store,
        entry_camera=entry_camera,
        entry_face_confidence=Decimal('97.50'),  # Mock confidence
        status='ACTIVE'
    )
    
    # Log face recognition
    FaceRecognitionLog.objects.create(
        user=request.user,
        camera=entry_camera,
        store=store,
        recognition_type='ENTRY',
        result='SUCCESS',
        confidence_score=Decimal('97.50'),
        session=session,
        processing_time_ms=150
    )
    
    log_audit(request.user, 'CREATE', 'ShoppingSession', session.id, request=request)
    
    messages.success(request, f'Shopping session started at {store.name}')
    return redirect('shopping_session', session_id=session.id)


@login_required
def shopping_session(request, session_id):
    """View active shopping session"""
    session = get_object_or_404(
        ShoppingSession, 
        id=session_id, 
        user=request.user
    )
    
    cart_items = ShoppingCart.objects.filter(session=session).select_related('product')
    
    # Calculate totals
    subtotal = sum(item.subtotal for item in cart_items)
    vat_amount = sum(item.subtotal * item.product.vat_rate / 100 for item in cart_items)
    total = subtotal + vat_amount
    
    context = {
        'session': session,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'vat_amount': vat_amount,
        'total': total,
    }
    return render(request, 'shopping/session.html', context)


@login_required
def add_to_cart(request, session_id, product_id):
    """Add product to cart"""
    session = get_object_or_404(ShoppingSession, id=session_id, user=request.user, status='ACTIVE')
    product = get_object_or_404(Product, id=product_id, is_active=True)
    
    # Check inventory
    inventory = StoreInventory.objects.filter(
        store=session.store,
        product=product,
        is_available=True
    ).first()
    
    if not inventory or inventory.quantity <= 0:
        messages.error(request, 'Product not available in this store')
        return redirect('shopping_session', session_id=session.id)
    
    # Add or update cart item
    cart_item, created = ShoppingCart.objects.get_or_create(
        session=session,
        product=product,
        defaults={
            'quantity': 1,
            'unit_price': product.price
        }
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f'{product.name} added to cart')
    return redirect('shopping_session', session_id=session.id)


@login_required
def update_cart_item(request, session_id, cart_item_id):
    """Update cart item quantity"""
    session = get_object_or_404(ShoppingSession, id=session_id, user=request.user)
    cart_item = get_object_or_404(ShoppingCart, id=cart_item_id, session=session)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Item removed from cart')
        else:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated')
        
        return redirect('shopping_session', session_id=session.id)


@login_required
def remove_from_cart(request, session_id, cart_item_id):
    """Remove item from cart"""
    session = get_object_or_404(ShoppingSession, id=session_id, user=request.user)
    cart_item = get_object_or_404(ShoppingCart, id=cart_item_id, session=session)
    
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return redirect('shopping_session', session_id=session.id)


@login_required
def checkout(request, session_id):
    """Checkout and process payment"""
    session = get_object_or_404(
        ShoppingSession, 
        id=session_id, 
        user=request.user, 
        status='ACTIVE'
    )
    
    cart_items = ShoppingCart.objects.filter(session=session).select_related('product')
    
    if not cart_items.exists():
        messages.error(request, 'Your cart is empty')
        return redirect('shopping_session', session_id=session.id)
    
    # Calculate totals
    subtotal = sum(item.subtotal for item in cart_items)
    vat_amount = sum(item.subtotal * item.product.vat_rate / 100 for item in cart_items)
    total = subtotal + vat_amount
    
    if request.method == 'POST':
        payment_account_id = request.POST.get('payment_account')
        
        payment_account = get_object_or_404(
            PaymentAccount, 
            id=payment_account_id, 
            user=request.user,
            is_active=True
        )
        
        # Create transaction
        with transaction.atomic():
            transaction_code = f"TXN-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            receipt_number = f"RCP-{timezone.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
            
            # Get checkout camera
            checkout_camera = Camera.objects.filter(
                store=session.store,
                camera_type='CHECKOUT',
                is_active=True
            ).first()
            
            # Create transaction
            transaction_obj = Transaction.objects.create(
                transaction_code=transaction_code,
                session=session,
                user=request.user,
                store=session.store,
                payment_account=payment_account,
                payment_method=payment_account.payment_method,
                subtotal=subtotal,
                vat_amount=vat_amount,
                discount_amount=Decimal('0.00'),
                total_amount=total,
                checkout_camera=checkout_camera,
                face_recognition_confidence=Decimal('96.80'),  # Mock
                status='PENDING',
                receipt_number=receipt_number
            )
            
            # Create transaction items
            for cart_item in cart_items:
                item_vat = cart_item.subtotal * cart_item.product.vat_rate / 100
                item_total = cart_item.subtotal + item_vat
                
                TransactionItem.objects.create(
                    transaction=transaction_obj,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    vat_rate=cart_item.product.vat_rate,
                    subtotal=cart_item.subtotal,
                    vat_amount=item_vat,
                    total=item_total
                )
                
                # Update inventory
                inventory = StoreInventory.objects.get(
                    store=session.store,
                    product=cart_item.product
                )
                inventory.quantity -= cart_item.quantity
                inventory.save()
            
            # Update session
            session.status = 'COMPLETED'
            session.exit_time = timezone.now()
            session.save()
            
            # In production, process actual payment here
            # For now, mark as completed
            transaction_obj.status = 'COMPLETED'
            transaction_obj.completed_at = timezone.now()
            transaction_obj.provider_transaction_id = f"MPESA-{uuid.uuid4().hex[:10].upper()}"
            transaction_obj.save()
            
            # Log face recognition at checkout
            FaceRecognitionLog.objects.create(
                user=request.user,
                camera=checkout_camera,
                store=session.store,
                recognition_type='CHECKOUT',
                result='SUCCESS',
                confidence_score=Decimal('96.80'),
                session=session,
                transaction=transaction_obj,
                processing_time_ms=180
            )
            
            # Award loyalty points
            try:
                loyalty = request.user.loyalty
            except LoyaltyProgram.DoesNotExist:
                loyalty = LoyaltyProgram.objects.create(user=request.user)
            
            points_earned = int(total)  # 1 KES = 1 point
            loyalty.total_points_earned += points_earned
            loyalty.current_balance += points_earned
            loyalty.last_activity = timezone.now()
            loyalty.save()
            
            # Create loyalty transaction
            LoyaltyTransaction.objects.create(
                loyalty_program=loyalty,
                transaction_type='EARN',
                points=points_earned,
                balance_after=loyalty.current_balance,
                related_transaction=transaction_obj,
                description=f"Earned from purchase at {session.store.name}",
                expires_at=timezone.now().date() + timedelta(days=365)
            )
            
            log_audit(request.user, 'PAYMENT', 'Transaction', transaction_obj.id, request=request)
            
            messages.success(request, f'Payment successful! Receipt: {receipt_number}')
            return redirect('transaction_detail', transaction_id=transaction_obj.id)
    
    # Get user's payment accounts
    payment_accounts = PaymentAccount.objects.filter(
        user=request.user,
        is_active=True,
        is_verified=True
    )
    
    context = {
        'session': session,
        'cart_items': cart_items,
        'subtotal': subtotal,
        'vat_amount': vat_amount,
        'total': total,
        'payment_accounts': payment_accounts,
    }
    return render(request, 'shopping/checkout.html', context)


# ==================== LOYALTY VIEWS ====================

@login_required
def loyalty_dashboard(request):
    """Loyalty program dashboard"""
    try:
        loyalty = request.user.loyalty
    except LoyaltyProgram.DoesNotExist:
        loyalty = LoyaltyProgram.objects.create(user=request.user)
    
    # Get recent loyalty transactions
    recent_transactions = LoyaltyTransaction.objects.filter(
        loyalty_program=loyalty
    ).order_by('-created_at')[:10]
    
    context = {
        'loyalty': loyalty,
        'recent_transactions': recent_transactions,
    }
    return render(request, 'customer/loyalty.html', context)


# ==================== STAFF/ADMIN DASHBOARD ====================

@login_required
@user_passes_test(is_staff_or_superuser)
def dashboard(request):
    """Staff/Admin main dashboard"""
    today = timezone.now().date()
    
    # Today's stats
    today_transactions = Transaction.objects.filter(
        initiated_at__date=today,
        status='COMPLETED'
    )
    
    today_revenue = today_transactions.aggregate(
        total=Sum('total_amount')
    )['total'] or Decimal('0.00')
    
    today_count = today_transactions.count()
    
    # Active sessions
    active_sessions = ShoppingSession.objects.filter(status='ACTIVE').count()
    
    # Recent transactions
    recent_transactions = Transaction.objects.all().order_by('-initiated_at')[:10]
    
    # Recent security alerts
    recent_alerts = SecurityAlert.objects.filter(status='OPEN').order_by('-created_at')[:5]
    
    # Top stores by revenue
    top_stores = Store.objects.annotate(
        revenue=Sum('transactions__total_amount', filter=Q(transactions__status='COMPLETED'))
    ).order_by('-revenue')[:5]
    
    context = {
        'today_revenue': today_revenue,
        'today_count': today_count,
        'active_sessions': active_sessions,
        'recent_transactions': recent_transactions,
        'recent_alerts': recent_alerts,
        'top_stores': top_stores,
    }
    return render(request, 'dashboard/index.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def analytics(request):
    """Analytics and reporting"""
    # Date range
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Revenue trend
    daily_reports = DailySalesReport.objects.filter(
        report_date__gte=start_date,
        report_date__lte=end_date
    ).values('report_date').annotate(
        revenue=Sum('total_revenue')
    ).order_by('report_date')
    
    # Payment method breakdown
    payment_breakdown = Transaction.objects.filter(
        status='COMPLETED',
        initiated_at__date__gte=start_date
    ).values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    )
    
    # Face recognition stats
    recognition_stats = FaceRecognitionLog.objects.filter(
        timestamp__date__gte=start_date
    ).values('result').annotate(count=Count('id'))
    
    context = {
        'daily_reports': list(daily_reports),
        'payment_breakdown': list(payment_breakdown),
        'recognition_stats': list(recognition_stats),
        'start_date': start_date,
        'end_date': end_date,
    }
    return render(request, 'dashboard/analytics.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def manage_stores(request):
    """Store management"""
    stores_list = Store.objects.all().order_by('name')
    
    context = {
        'stores': stores_list,
    }
    return render(request, 'dashboard/stores.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def manage_products(request):
    """Product management"""
    products_list = Product.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(products_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'dashboard/products.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def manage_inventory(request, store_id):
    """Store inventory management"""
    store = get_object_or_404(Store, id=store_id)
    inventory = StoreInventory.objects.filter(store=store).select_related('product')
    
    # Low stock items
    low_stock = inventory.filter(quantity__lte=F('reorder_level'))
    
    context = {
        'store': store,
        'inventory': inventory,
        'low_stock': low_stock,
    }
    return render(request, 'dashboard/inventory.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def security_alerts_view(request):
    """Security alerts management"""
    alerts = SecurityAlert.objects.all().order_by('-created_at')
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        alerts = alerts.filter(status=status)
    
    # Filter by severity
    severity = request.GET.get('severity')
    if severity:
        alerts = alerts.filter(severity=severity)
    
    # Pagination
    paginator = Paginator(alerts, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'dashboard/security_alerts.html', context)


@login_required
@user_passes_test(is_staff_or_superuser)
def customers_list(request):
    """Customer management"""
    customers = CustomUser.objects.filter(is_staff=False).order_by('-created_at')
    
    # Search
    search = request.GET.get('search')
    if search:
        customers = customers.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(phone_number__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    # Pagination
    paginator = Paginator(customers, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'dashboard/customers.html', context)


# ==================== API ENDPOINTS (JSON) ====================

@require_http_methods(["POST"])
@csrf_exempt
def api_face_verify(request):
    """API endpoint for face verification"""
    # This would integrate with actual face recognition
    # For now, return mock response
    
    data = json.loads(request.body)
    user_id = data.get('user_id')
    face_data = data.get('face_data')
    
    # Mock verification
    response = {
        'success': True,
        'user_id': user_id,
        'confidence': 97.5,
        'verified': True
    }
    
    return JsonResponse(response)


@require_http_methods(["GET"])
def api_store_status(request, store_id):
    """Get real-time store status"""
    store = get_object_or_404(Store, id=store_id)
    
    # Active sessions
    active_sessions = ShoppingSession.objects.filter(
        store=store,
        status='ACTIVE'
    ).count()
    
    # Today's revenue
    today_revenue = Transaction.objects.filter(
        store=store,
        status='COMPLETED',
        initiated_at__date=timezone.now().date()
    ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0.00')
    
    # Camera status
    cameras = Camera.objects.filter(store=store)
    cameras_online = cameras.filter(is_online=True).count()
    cameras_total = cameras.count()
    
    response = {
        'store_id': str(store.id),
        'store_name': store.name,
        'is_open': store.is_24_hours or True,  # Simplified
        'active_sessions': active_sessions,
        'today_revenue': float(today_revenue),
        'cameras_online': cameras_online,
        'cameras_total': cameras_total,
    }
    
    return JsonResponse(response)


@require_http_methods(["GET"])
def api_product_availability(request, product_id, store_id):
    """Check product availability in store"""
    try:
        inventory = StoreInventory.objects.get(
            product_id=product_id,
            store_id=store_id
        )
        
        response = {
            'available': inventory.is_available and inventory.quantity > 0,
            'quantity': inventory.quantity,
            'location': inventory.shelf_location,
            'aisle': inventory.aisle,
        }
    except StoreInventory.DoesNotExist:
        response = {
            'available': False,
            'quantity': 0,
            'location': None,
            'aisle': None,
        }
    
    return JsonResponse(response)


# ==================== PROMOTIONS ====================

def promotions_list(request):
    """Active promotions"""
    now = timezone.now()
    active_promotions = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )
    
    context = {
        'promotions': active_promotions,
    }
    return render(request, 'shopping/promotions.html', context)


# ==================== ERROR HANDLERS ====================

def handler404(request, exception):
    """404 error handler"""
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    """500 error handler"""
    return render(request, 'errors/500.html', status=500)