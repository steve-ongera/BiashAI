"""
BiashAI - Django Forms
Forms for user registration, profiles, and data input
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError
from .models import (
    CustomUser, FacialData, PaymentAccount, Store, Product,
    StoreInventory, Promotion
)


# ==================== USER FORMS ====================

class CustomUserCreationForm(UserCreationForm):
    """Form for user registration"""
    
    class Meta:
        model = CustomUser
        fields = (
            'username', 'email', 'phone_number', 'first_name', 'last_name',
            'date_of_birth', 'gender', 'id_number', 'profile_image'
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+254712345678'}),
            'id_number': forms.TextInput(attrs={'placeholder': 'National ID Number'}),
        }
    
    def clean_phone_number(self):
        """Validate phone number format"""
        phone_number = self.cleaned_data.get('phone_number')
        
        # Kenyan phone number validation
        if not phone_number.startswith('+254'):
            if phone_number.startswith('0'):
                phone_number = '+254' + phone_number[1:]
            elif phone_number.startswith('254'):
                phone_number = '+' + phone_number
            else:
                raise ValidationError('Invalid Kenyan phone number format')
        
        if len(phone_number) != 13:
            raise ValidationError('Phone number must be 13 digits including +254')
        
        return phone_number


class CustomUserChangeForm(UserChangeForm):
    """Form for user profile updates"""
    
    class Meta:
        model = CustomUser
        fields = (
            'first_name', 'last_name', 'email', 'phone_number',
            'date_of_birth', 'gender', 'profile_image'
        )
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }


class UserProfileForm(forms.ModelForm):
    """Simple profile update form"""
    
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'gender', 'profile_image']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'profile_image': forms.FileInput(attrs={'class': 'form-control'}),
        }


# ==================== FACIAL DATA FORMS ====================

class FacialDataRegistrationForm(forms.ModelForm):
    """Form for registering facial data"""
    
    class Meta:
        model = FacialData
        fields = ['face_image_sample', 'confidence_threshold']
        widgets = {
            'face_image_sample': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
                'capture': 'camera'  # Mobile camera capture
            }),
            'confidence_threshold': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '50.00',
                'max': '100.00',
                'step': '0.01'
            }),
        }
    
    def clean_face_image_sample(self):
        """Validate face image"""
        image = self.cleaned_data.get('face_image_sample')
        
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise ValidationError('Image file too large (max 5MB)')
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise ValidationError('File must be an image')
        
        return image


# ==================== PAYMENT ACCOUNT FORMS ====================

class PaymentAccountForm(forms.ModelForm):
    """Form for adding payment accounts"""
    
    class Meta:
        model = PaymentAccount
        fields = [
            'payment_method', 'account_number', 'account_name',
            'is_primary', 'daily_limit', 'transaction_limit'
        ]
        widgets = {
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'account_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone number or card number'
            }),
            'account_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Account holder name'
            }),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'daily_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
            'transaction_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '0.01'
            }),
        }
    
    def clean_account_number(self):
        """Validate account number based on payment method"""
        account_number = self.cleaned_data.get('account_number')
        payment_method = self.cleaned_data.get('payment_method')
        
        if payment_method in ['MPESA', 'AIRTEL', 'TKASH']:
            # Mobile money - validate phone number
            if not account_number.startswith('+254'):
                if account_number.startswith('0'):
                    account_number = '+254' + account_number[1:]
                elif account_number.startswith('254'):
                    account_number = '+' + account_number
                else:
                    raise ValidationError('Invalid phone number format')
            
            if len(account_number) != 13:
                raise ValidationError('Phone number must be valid Kenyan number')
        
        elif payment_method == 'CARD':
            # Card number validation (basic)
            account_number = account_number.replace(' ', '').replace('-', '')
            if not account_number.isdigit():
                raise ValidationError('Card number must contain only digits')
            if len(account_number) not in [13, 14, 15, 16, 19]:
                raise ValidationError('Invalid card number length')
        
        return account_number


# ==================== STORE FORMS ====================

class StoreForm(forms.ModelForm):
    """Form for creating/updating stores"""
    
    class Meta:
        model = Store
        fields = [
            'name', 'store_code', 'store_type', 'county', 'address',
            'latitude', 'longitude', 'phone_number', 'email',
            'opening_time', 'closing_time', 'is_24_hours',
            'is_active', 'date_opened', 'manager'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'store_code': forms.TextInput(attrs={'class': 'form-control'}),
            'store_type': forms.Select(attrs={'class': 'form-control'}),
            'county': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'latitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.000001'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'opening_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'is_24_hours': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'date_opened': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'manager': forms.Select(attrs={'class': 'form-control'}),
        }


# ==================== PRODUCT FORMS ====================

class ProductForm(forms.ModelForm):
    """Form for creating/updating products"""
    
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'category', 'barcode', 'sku',
            'price', 'cost_price', 'vat_rate', 'brand', 'manufacturer',
            'country_of_origin', 'weight', 'dimensions', 'image',
            'is_active', 'is_featured'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'slug': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'barcode': forms.TextInput(attrs={'class': 'form-control'}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'vat_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'brand': forms.TextInput(attrs={'class': 'form-control'}),
            'manufacturer': forms.TextInput(attrs={'class': 'form-control'}),
            'country_of_origin': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'L x W x H'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProductSearchForm(forms.Form):
    """Form for searching products"""
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search products by name, barcode, or brand...'
        })
    )
    category = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Min price',
            'step': '0.01'
        })
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Max price',
            'step': '0.01'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import ProductCategory
        self.fields['category'].queryset = ProductCategory.objects.filter(parent__isnull=True)


# ==================== INVENTORY FORMS ====================

class StoreInventoryForm(forms.ModelForm):
    """Form for managing store inventory"""
    
    class Meta:
        model = StoreInventory
        fields = [
            'product', 'quantity', 'reorder_level', 'max_stock_level',
            'shelf_location', 'aisle', 'is_available'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'reorder_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'max_stock_level': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'shelf_location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Aisle A-12'
            }),
            'aisle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., A, B, C'}),
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class InventoryUpdateForm(forms.Form):
    """Quick form for updating inventory quantity"""
    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'New quantity'
        })
    )
    reason = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reason for update (optional)'
        })
    )


# ==================== PROMOTION FORMS ====================

class PromotionForm(forms.ModelForm):
    """Form for creating/updating promotions"""
    
    class Meta:
        model = Promotion
        fields = [
            'name', 'code', 'description', 'discount_type', 'discount_value',
            'minimum_purchase', 'maximum_discount', 'start_date', 'end_date',
            'is_active', 'usage_limit', 'usage_per_customer',
            'applicable_stores', 'applicable_products', 'applicable_categories'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PROMO2024'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'discount_type': forms.Select(attrs={'class': 'form-control'}),
            'discount_value': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'minimum_purchase': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'maximum_discount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'start_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'end_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'usage_limit': forms.NumberInput(attrs={'class': 'form-control'}),
            'usage_per_customer': forms.NumberInput(attrs={'class': 'form-control'}),
            'applicable_stores': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'applicable_products': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'applicable_categories': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }


# ==================== CHECKOUT FORMS ====================

class CheckoutForm(forms.Form):
    """Form for checkout process"""
    payment_account = forms.ModelChoiceField(
        queryset=None,  # Will be set in __init__
        widget=forms.RadioSelect,
        label="Select Payment Method"
    )
    apply_promotion = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter promo code (optional)'
        })
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['payment_account'].queryset = PaymentAccount.objects.filter(
            user=user,
            is_active=True,
            is_verified=True
        )


# ==================== CONTACT FORMS ====================

class ContactForm(forms.Form):
    """Contact form for customer inquiries"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your Name'
        })
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+254712345678'
        })
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject'
        })
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message...'
        })
    )