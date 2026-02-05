"""
BiashAI Seed Data Management Command
Populates all models with realistic Kenyan market data

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear  # Clear existing data first
    python manage.py seed_data --users=50 --products=200  # Custom counts
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
from datetime import datetime, timedelta
import base64
import os

# Import all models
from pos_ai.models import CustomUser, FacialData, PaymentAccount
from pos_ai.models import County, Store, Camera
from pos_ai.models import ProductCategory, Product, StoreInventory
from pos_ai.models import ShoppingSession, ShoppingCart
from pos_ai.models import Transaction, TransactionItem
from pos_ai.models import FaceRecognitionLog, SecurityAlert, AuditLog
from pos_ai.models import DailySalesReport, CustomerBehavior
from pos_ai.models import Promotion, LoyaltyProgram, LoyaltyTransaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Seeds the database with realistic Kenyan market data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )
        parser.add_argument(
            '--users',
            type=int,
            default=50,
            help='Number of users to create (default: 50)',
        )
        parser.add_argument(
            '--products',
            type=int,
            default=150,
            help='Number of products to create (default: 150)',
        )
        parser.add_argument(
            '--stores',
            type=int,
            default=10,
            help='Number of stores to create (default: 10)',
        )
        parser.add_argument(
            '--transactions',
            type=int,
            default=200,
            help='Number of transactions to create (default: 200)',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🌱 Starting BiashAI Data Seeding...'))
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('⚠️  Clearing existing data...'))
            self.clear_data()
        
        try:
            with transaction.atomic():
                # Seed in order of dependencies
                self.seed_counties()
                self.seed_users(options['users'])
                self.seed_facial_data()
                self.seed_payment_accounts()
                self.seed_stores(options['stores'])
                self.seed_cameras()
                self.seed_product_categories()
                self.seed_products(options['products'])
                self.seed_store_inventory()
                self.seed_shopping_sessions()
                self.seed_shopping_carts()
                self.seed_transactions(options['transactions'])
                self.seed_transaction_items()
                self.seed_face_recognition_logs()
                self.seed_security_alerts()
                self.seed_audit_logs()
                self.seed_daily_sales_reports()
                self.seed_customer_behavior()
                self.seed_promotions()
                self.seed_loyalty_programs()
                self.seed_loyalty_transactions()
                
                self.stdout.write(self.style.SUCCESS('✅ Database seeding completed successfully!'))
                self.print_summary()
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error during seeding: {str(e)}'))
            raise CommandError(f'Seeding failed: {str(e)}')

    def clear_data(self):
        """Clear all existing data"""
        models_to_clear = [
            LoyaltyTransaction, LoyaltyProgram, Promotion,
            CustomerBehavior, DailySalesReport, AuditLog,
            SecurityAlert, FaceRecognitionLog, TransactionItem,
            Transaction, ShoppingCart, ShoppingSession,
            StoreInventory, Product, ProductCategory,
            Camera, Store, PaymentAccount, FacialData,
            User, County
        ]
        
        for model in models_to_clear:
            count = model.objects.all().delete()[0]
            if count > 0:
                self.stdout.write(f'  Deleted {count} {model.__name__} records')

    # ==================== KENYA COUNTIES ====================
    
    def seed_counties(self):
        """Seed Kenya's 47 counties"""
        self.stdout.write('📍 Seeding Counties...')
        
        counties_data = [
            ('Mombasa', '001'), ('Kwale', '002'), ('Kilifi', '003'), ('Tana River', '004'),
            ('Lamu', '005'), ('Taita-Taveta', '006'), ('Garissa', '007'), ('Wajir', '008'),
            ('Mandera', '009'), ('Marsabit', '010'), ('Isiolo', '011'), ('Meru', '012'),
            ('Tharaka-Nithi', '013'), ('Embu', '014'), ('Kitui', '015'), ('Machakos', '016'),
            ('Makueni', '017'), ('Nyandarua', '018'), ('Nyeri', '019'), ('Kirinyaga', '020'),
            ('Murang\'a', '021'), ('Kiambu', '022'), ('Turkana', '023'), ('West Pokot', '024'),
            ('Samburu', '025'), ('Trans-Nzoia', '026'), ('Uasin Gishu', '027'), ('Elgeyo-Marakwet', '028'),
            ('Nandi', '029'), ('Baringo', '030'), ('Laikipia', '031'), ('Nakuru', '032'),
            ('Narok', '033'), ('Kajiado', '034'), ('Kericho', '035'), ('Bomet', '036'),
            ('Kakamega', '037'), ('Vihiga', '038'), ('Bungoma', '039'), ('Busia', '040'),
            ('Siaya', '041'), ('Kisumu', '042'), ('Homa Bay', '043'), ('Migori', '044'),
            ('Kisii', '045'), ('Nyamira', '046'), ('Nairobi', '047')
        ]
        
        for name, code in counties_data:
            County.objects.get_or_create(name=name, code=code)
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {len(counties_data)} counties'))

    # ==================== USERS ====================
    
    def seed_users(self, count):
        """Seed users with Kenyan names and phone numbers"""
        self.stdout.write(f'👥 Seeding {count} Users...')
        
        first_names = [
            'John', 'Mary', 'David', 'Grace', 'Peter', 'Jane', 'James', 'Lucy',
            'Daniel', 'Faith', 'Michael', 'Catherine', 'Joseph', 'Margaret', 'Samuel',
            'Ann', 'Paul', 'Elizabeth', 'Stephen', 'Joyce', 'Francis', 'Esther',
            'Patrick', 'Rose', 'Anthony', 'Susan', 'Moses', 'Nancy', 'George', 'Betty'
        ]
        
        last_names = [
            'Kamau', 'Wanjiku', 'Ochieng', 'Akinyi', 'Mwangi', 'Njeri', 'Otieno',
            'Adhiambo', 'Kipchoge', 'Chepkemoi', 'Kiplagat', 'Chebet', 'Mutua',
            'Muthoni', 'Wafula', 'Nafula', 'Kibet', 'Cherono', 'Kariuki', 'Wairimu',
            'Ndung\'u', 'Wambui', 'Kimani', 'Nyambura', 'Omondi', 'Atieno'
        ]
        
        genders = ['M', 'F', 'O']
        
        # Create superuser first
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@biashai.co.ke',
                password='admin123',
                phone_number='+254700000000',
                first_name='Admin',
                last_name='BiashAI',
                is_verified=True,
                kyc_verified=True
            )
            self.stdout.write('  Created superuser: admin/admin123')
        
        users_created = 0
        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            username = f"{first_name.lower()}_{last_name.lower()}_{i}"
            email = f"{username}@example.com"
            phone_number = f"+2547{random.randint(10000000, 99999999)}"
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'phone_number': phone_number,
                    'first_name': first_name,
                    'last_name': last_name,
                    'gender': random.choice(genders),
                    'date_of_birth': datetime(
                        random.randint(1970, 2000),
                        random.randint(1, 12),
                        random.randint(1, 28)
                    ).date(),
                    'id_number': f"{random.randint(10000000, 39999999)}",
                    'is_verified': random.choice([True, True, True, False]),
                    'kyc_verified': random.choice([True, True, False]),
                }
            )
            
            if created:
                user.set_password('password123')
                user.save()
                users_created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {users_created} users'))

    # ==================== FACIAL DATA ====================
    
    def seed_facial_data(self):
        """Seed facial data for users"""
        self.stdout.write('🎭 Seeding Facial Data...')
        
        users = User.objects.filter(is_verified=True)[:30]  # First 30 verified users
        created = 0
        
        for user in users:
            # Generate dummy base64 encoding (in production, this would be real facial encoding)
            dummy_encoding = base64.b64encode(os.urandom(128)).decode('utf-8')
            
            facial_data, created_new = FacialData.objects.get_or_create(
                user=user,
                defaults={
                    'face_encoding': dummy_encoding,
                    'confidence_threshold': Decimal(str(random.uniform(90.0, 98.0))),
                    'is_active': True,
                    'failed_recognition_attempts': random.randint(0, 2)
                }
            )
            
            if created_new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} facial data records'))

    # ==================== PAYMENT ACCOUNTS ====================
    
    def seed_payment_accounts(self):
        """Seed payment accounts"""
        self.stdout.write('💳 Seeding Payment Accounts...')
        
        users = User.objects.filter(is_verified=True)
        payment_methods = ['MPESA', 'AIRTEL', 'TKASH', 'CARD']
        created = 0
        
        for user in users:
            # Each user gets 1-3 payment accounts
            num_accounts = random.randint(1, 3)
            methods = random.sample(payment_methods, num_accounts)
            
            for idx, method in enumerate(methods):
                if method in ['MPESA', 'AIRTEL', 'TKASH']:
                    account_number = user.phone_number
                else:
                    account_number = f"{random.randint(4000, 4999)}{random.randint(1000000000, 9999999999)}"
                
                account, created_new = PaymentAccount.objects.get_or_create(
                    user=user,
                    account_number=account_number,
                    defaults={
                        'payment_method': method,
                        'account_name': f"{user.first_name} {user.last_name}",
                        'is_primary': idx == 0,
                        'is_verified': True,
                        'is_active': True,
                        'daily_limit': Decimal('50000.00'),
                        'transaction_limit': Decimal('10000.00')
                    }
                )
                
                if created_new:
                    created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} payment accounts'))

    # ==================== STORES ====================
    
    def seed_stores(self, count):
        """Seed stores across Kenya"""
        self.stdout.write(f'🏪 Seeding {count} Stores...')
        
        store_locations = [
            ('Westlands', 'Nairobi', -1.2645, 36.8065),
            ('Kilimani', 'Nairobi', -1.2921, 36.7854),
            ('Karen', 'Nairobi', -1.3196, 36.7045),
            ('Thika Road', 'Nairobi', -1.2567, 36.8876),
            ('Mombasa Road', 'Nairobi', -1.3167, 36.8564),
            ('Nyali', 'Mombasa', -4.0435, 39.7145),
            ('Diani', 'Kwale', -4.3166, 39.5833),
            ('Nakuru Town', 'Nakuru', -0.3031, 36.0800),
            ('Eldoret', 'Uasin Gishu', 0.5143, 35.2698),
            ('Kisumu', 'Kisumu', -0.0917, 34.7680),
            ('Meru', 'Meru', 0.0469, 37.6556),
            ('Thika', 'Kiambu', -1.0332, 37.0693),
            ('Machakos', 'Machakos', -1.5177, 37.2634),
            ('Kitale', 'Trans-Nzoia', 1.0194, 35.0063),
            ('Malindi', 'Kilifi', -3.2167, 40.1167),
        ]
        
        store_types = ['UNMANNED', 'HYBRID', 'ASSISTED']
        managers = list(User.objects.filter(is_staff=True))
        if not managers:
            managers = list(User.objects.all()[:5])
        
        created = 0
        for i in range(min(count, len(store_locations))):
            location_name, county_name, lat, lng = store_locations[i]
            county = County.objects.get(name=county_name)
            
            store, created_new = Store.objects.get_or_create(
                store_code=f"BIA-{county.code}-{str(i+1).zfill(3)}",
                defaults={
                    'name': f"BiashAI {location_name}",
                    'store_type': random.choice(store_types),
                    'county': county,
                    'address': f"{location_name} Shopping Centre, {county_name}",
                    'latitude': Decimal(str(lat)),
                    'longitude': Decimal(str(lng)),
                    'phone_number': f"+2547{random.randint(10000000, 99999999)}",
                    'email': f"{location_name.lower().replace(' ', '')}@biashai.co.ke",
                    'opening_time': '06:00:00',
                    'closing_time': '22:00:00',
                    'is_24_hours': random.choice([False, False, False, True]),
                    'is_active': True,
                    'date_opened': timezone.now().date() - timedelta(days=random.randint(30, 365)),
                    'manager': random.choice(managers) if managers else None
                }
            )
            
            if created_new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} stores'))

    # ==================== CAMERAS ====================
    
    def seed_cameras(self):
        """Seed cameras for each store"""
        self.stdout.write('📷 Seeding Cameras...')
        
        stores = Store.objects.all()
        camera_types = ['ENTRY', 'SHELF', 'CHECKOUT', 'SECURITY']
        created = 0
        
        for store in stores:
            # Each store gets 4-8 cameras
            num_cameras = random.randint(4, 8)
            
            for i in range(num_cameras):
                camera_type = random.choice(camera_types)
                camera_code = f"{store.store_code}-CAM-{str(i+1).zfill(3)}"
                
                camera, created_new = Camera.objects.get_or_create(
                    camera_code=camera_code,
                    defaults={
                        'store': store,
                        'camera_type': camera_type,
                        'ip_address': f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
                        'port': 554,
                        'stream_url': f"rtsp://192.168.1.{i}/stream",
                        'location_description': f"{camera_type} Camera {i+1}",
                        'zone': random.choice(['Entrance', 'Aisle A', 'Aisle B', 'Checkout', 'Exit']),
                        'is_active': True,
                        'is_online': random.choice([True, True, True, False]),
                        'installation_date': timezone.now().date() - timedelta(days=random.randint(10, 200)),
                        'last_ping': timezone.now() - timedelta(minutes=random.randint(1, 60))
                    }
                )
                
                if created_new:
                    created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} cameras'))

    # ==================== PRODUCT CATEGORIES ====================
    
    def seed_product_categories(self):
        """Seed product categories"""
        self.stdout.write('📦 Seeding Product Categories...')
        
        categories = [
            ('Dairy & Eggs', None),
            ('Fresh Milk', 'Dairy & Eggs'),
            ('Yogurt', 'Dairy & Eggs'),
            ('Cheese', 'Dairy & Eggs'),
            ('Eggs', 'Dairy & Eggs'),
            ('Beverages', None),
            ('Soft Drinks', 'Beverages'),
            ('Juices', 'Beverages'),
            ('Water', 'Beverages'),
            ('Tea & Coffee', 'Beverages'),
            ('Bakery', None),
            ('Bread', 'Bakery'),
            ('Cakes', 'Bakery'),
            ('Pastries', 'Bakery'),
            ('Pantry', None),
            ('Rice & Grains', 'Pantry'),
            ('Cooking Oil', 'Pantry'),
            ('Spices', 'Pantry'),
            ('Canned Foods', 'Pantry'),
            ('Snacks', None),
            ('Chips & Crisps', 'Snacks'),
            ('Biscuits', 'Snacks'),
            ('Nuts', 'Snacks'),
            ('Personal Care', None),
            ('Bath & Body', 'Personal Care'),
            ('Hair Care', 'Personal Care'),
            ('Oral Care', 'Personal Care'),
            ('Household', None),
            ('Cleaning Supplies', 'Household'),
            ('Laundry', 'Household'),
        ]
        
        created = 0
        category_map = {}
        
        for name, parent_name in categories:
            parent = category_map.get(parent_name) if parent_name else None
            slug = name.lower().replace(' & ', '-').replace(' ', '-')
            
            category, created_new = ProductCategory.objects.get_or_create(
                slug=slug,
                defaults={
                    'name': name,
                    'parent': parent,
                    'is_active': True
                }
            )
            
            category_map[name] = category
            if created_new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} categories'))

    # ==================== PRODUCTS ====================
    
    def seed_products(self, count):
        """Seed products"""
        self.stdout.write(f'🛍️ Seeding {count} Products...')
        
        kenyan_products = [
            ('Brookside Fresh Milk 500ml', 'Fresh Milk', 'Brookside', 120.00, 16.00),
            ('Brookside Fresh Milk 1L', 'Fresh Milk', 'Brookside', 210.00, 16.00),
            ('KCC Mala 500ml', 'Yogurt', 'KCC', 80.00, 16.00),
            ('Tuzo UHT Milk 500ml', 'Fresh Milk', 'Tuzo', 65.00, 16.00),
            ('Daima Milk 500ml', 'Fresh Milk', 'Daima', 55.00, 16.00),
            ('Coca-Cola 500ml', 'Soft Drinks', 'Coca-Cola', 60.00, 16.00),
            ('Fanta Orange 500ml', 'Soft Drinks', 'Coca-Cola', 60.00, 16.00),
            ('Sprite 500ml', 'Soft Drinks', 'Coca-Cola', 60.00, 16.00),
            ('Dasani Water 500ml', 'Water', 'Coca-Cola', 40.00, 0.00),
            ('Keringet Water 500ml', 'Water', 'Keringet', 50.00, 0.00),
            ('Ketepa Tea Bags', 'Tea & Coffee', 'Ketepa', 250.00, 16.00),
            ('Java Coffee 250g', 'Tea & Coffee', 'Java House', 450.00, 16.00),
            ('Pishori Rice 2kg', 'Rice & Grains', 'Pishori', 280.00, 0.00),
            ('Basmati Rice 1kg', 'Rice & Grains', 'Tilda', 320.00, 0.00),
            ('Fresh Fried Cooking Oil 2L', 'Cooking Oil', 'Fresh Fried', 520.00, 16.00),
            ('Elianto Cooking Oil 3L', 'Cooking Oil', 'Elianto', 680.00, 16.00),
            ('Royco Mchuzi Mix', 'Spices', 'Royco', 15.00, 16.00),
            ('Salit Cooking Salt 500g', 'Spices', 'Salit', 30.00, 0.00),
            ('Kimbo Cooking Fat 1kg', 'Cooking Oil', 'Kimbo', 280.00, 16.00),
            ('Pembe Wheat Flour 2kg', 'Rice & Grains', 'Pembe', 180.00, 0.00),
            ('Soko Ugali Maize Flour 2kg', 'Rice & Grains', 'Soko', 140.00, 0.00),
            ('Broadways Bread 400g', 'Bread', 'Broadways', 55.00, 0.00),
            ('Mini Loaf 400g', 'Bread', 'Mini', 50.00, 0.00),
            ('Lays Chips Salt 145g', 'Chips & Crisps', 'Lays', 120.00, 16.00),
            ('Tropical Heat Crisps', 'Chips & Crisps', 'Tropical Heat', 50.00, 16.00),
            ('Oreo Biscuits', 'Biscuits', 'Oreo', 100.00, 16.00),
            ('Ellipse Biscuits', 'Biscuits', 'Ellipse', 40.00, 16.00),
            ('Colgate Toothpaste 75ml', 'Oral Care', 'Colgate', 180.00, 16.00),
            ('Close Up Toothpaste 100ml', 'Oral Care', 'Close Up', 120.00, 16.00),
            ('Omo Washing Powder 1kg', 'Laundry', 'Omo', 320.00, 16.00),
            ('Sunlight Bar Soap', 'Laundry', 'Sunlight', 45.00, 16.00),
            ('Geisha Bathing Soap', 'Bath & Body', 'Geisha', 35.00, 16.00),
            ('Imperial Leather Soap', 'Bath & Body', 'Imperial Leather', 60.00, 16.00),
            ('Vaseline Petroleum Jelly', 'Bath & Body', 'Vaseline', 150.00, 16.00),
            ('Nivea Body Lotion 400ml', 'Bath & Body', 'Nivea', 450.00, 16.00),
        ]
        
        categories = {cat.name: cat for cat in ProductCategory.objects.all()}
        created = 0
        
        # Create products from kenyan_products list
        for name, category_name, brand, price, vat_rate in kenyan_products:
            category = categories.get(category_name)
            if not category:
                continue
            
            barcode = f"{random.randint(600000000000, 699999999999)}"
            sku = f"SKU-{random.randint(10000, 99999)}"
            slug = f"{name.lower().replace(' ', '-')}-{random.randint(1, 999)}"
            
            product, created_new = Product.objects.get_or_create(
                barcode=barcode,
                defaults={
                    'name': name,
                    'slug': slug,
                    'sku': sku,
                    'category': category,
                    'price': Decimal(str(price)),
                    'cost_price': Decimal(str(price * 0.7)),  # 30% markup
                    'vat_rate': Decimal(str(vat_rate)),
                    'brand': brand,
                    'manufacturer': brand,
                    'country_of_origin': 'Kenya',
                    'is_active': True,
                    'is_featured': random.choice([True, False, False, False])
                }
            )
            
            if created_new:
                created += 1
        
        # Generate additional random products if needed
        while created < count:
            category = random.choice(list(categories.values()))
            product_num = random.randint(1000, 9999)
            
            product, created_new = Product.objects.get_or_create(
                barcode=f"{random.randint(600000000000, 699999999999)}",
                defaults={
                    'name': f"{category.name} Product {product_num}",
                    'slug': f"product-{product_num}-{random.randint(1, 999)}",
                    'sku': f"SKU-{product_num}",
                    'category': category,
                    'price': Decimal(str(random.uniform(50, 1000))),
                    'cost_price': Decimal(str(random.uniform(30, 700))),
                    'vat_rate': Decimal('16.00') if random.random() > 0.3 else Decimal('0.00'),
                    'brand': random.choice(['Generic', 'Premium', 'Local']),
                    'manufacturer': 'Kenya Ltd',
                    'country_of_origin': 'Kenya',
                    'is_active': True,
                    'is_featured': random.choice([True, False, False, False])
                }
            )
            
            if created_new:
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} products'))

    # ==================== STORE INVENTORY ====================
    
    def seed_store_inventory(self):
        """Seed inventory for each store"""
        self.stdout.write('📊 Seeding Store Inventory...')
        
        stores = Store.objects.all()
        products = Product.objects.filter(is_active=True)
        created = 0
        
        for store in stores:
            # Each store stocks 60-80% of all products
            num_products = int(len(products) * random.uniform(0.6, 0.8))
            store_products = random.sample(list(products), num_products)
            
            for product in store_products:
                inventory, created_new = StoreInventory.objects.get_or_create(
                    store=store,
                    product=product,
                    defaults={
                        'quantity': random.randint(10, 200),
                        'reorder_level': random.randint(5, 20),
                        'max_stock_level': random.randint(100, 500),
                        'shelf_location': f"Aisle {random.choice(['A', 'B', 'C', 'D'])}-{random.randint(1, 20)}",
                        'aisle': random.choice(['A', 'B', 'C', 'D', 'E']),
                        'is_available': True,
                        'last_restocked': timezone.now() - timedelta(days=random.randint(1, 30))
                    }
                )
                
                if created_new:
                    created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} inventory records'))

    # ==================== SHOPPING SESSIONS ====================
    
    def seed_shopping_sessions(self):
        """Seed shopping sessions"""
        self.stdout.write('🛒 Seeding Shopping Sessions...')
        
        users_with_face = User.objects.filter(facial_data__isnull=False)
        stores = Store.objects.all()
        cameras = Camera.objects.filter(camera_type='ENTRY')
        
        created = 0
        self.sessions = []  # Store for later use
        
        for i in range(100):
            user = random.choice(users_with_face)
            store = random.choice(stores)
            entry_camera = random.choice(cameras.filter(store=store)) if cameras.filter(store=store).exists() else None
            
            entry_time = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            
            status = random.choice(['ACTIVE', 'COMPLETED', 'COMPLETED', 'COMPLETED', 'ABANDONED'])
            exit_time = entry_time + timedelta(minutes=random.randint(10, 60)) if status in ['COMPLETED', 'ABANDONED'] else None
            
            session = ShoppingSession.objects.create(
                session_code=f"SHOP-{timezone.now().strftime('%Y%m%d')}-{str(i+1).zfill(4)}",
                user=user,
                store=store,
                entry_time=entry_time,
                exit_time=exit_time,
                entry_camera=entry_camera,
                entry_face_confidence=Decimal(str(random.uniform(90.0, 99.9))),
                status=status
            )
            
            self.sessions.append(session)
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} shopping sessions'))

    # ==================== SHOPPING CARTS ====================
    
    def seed_shopping_carts(self):
        """Seed shopping cart items"""
        self.stdout.write('🛍️ Seeding Shopping Cart Items...')
        
        if not hasattr(self, 'sessions'):
            self.sessions = list(ShoppingSession.objects.all()[:50])
        
        created = 0
        
        for session in self.sessions:
            # Get products available in this store
            available_products = StoreInventory.objects.filter(
                store=session.store,
                is_available=True
            ).select_related('product')
            
            if not available_products.exists():
                continue
            
            # Each session has 2-10 items
            num_items = random.randint(2, 10)
            selected_inventories = random.sample(list(available_products), min(num_items, len(available_products)))
            
            for inventory in selected_inventories:
                ShoppingCart.objects.create(
                    session=session,
                    product=inventory.product,
                    quantity=random.randint(1, 3),
                    unit_price=inventory.product.price,
                    added_at=session.entry_time + timedelta(minutes=random.randint(1, 30))
                )
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} cart items'))

    # ==================== TRANSACTIONS ====================
    
    def seed_transactions(self, count):
        """Seed transactions"""
        self.stdout.write(f'💰 Seeding {count} Transactions...')
        
        completed_sessions = ShoppingSession.objects.filter(status='COMPLETED')
        payment_accounts = PaymentAccount.objects.filter(is_verified=True)
        checkout_cameras = Camera.objects.filter(camera_type='CHECKOUT')
        
        created = 0
        self.transactions = []  # Store for later use
        
        for session in completed_sessions[:count]:
            payment_account = payment_accounts.filter(user=session.user).first()
            if not payment_account:
                continue
            
            checkout_camera = random.choice(checkout_cameras.filter(store=session.store)) if checkout_cameras.filter(store=session.store).exists() else None
            
            # Calculate totals from cart
            cart_items = ShoppingCart.objects.filter(session=session)
            subtotal = sum(item.subtotal for item in cart_items)
            vat_amount = sum(item.subtotal * item.product.vat_rate / 100 for item in cart_items)
            discount = Decimal('0.00')
            total = subtotal + vat_amount - discount
            
            if total == 0:
                continue
            
            transaction = Transaction.objects.create(
                transaction_code=f"TXN-{timezone.now().strftime('%Y%m%d')}-{str(created+1).zfill(4)}",
                session=session,
                user=session.user,
                store=session.store,
                payment_account=payment_account,
                payment_method=payment_account.payment_method,
                subtotal=subtotal,
                vat_amount=vat_amount,
                discount_amount=discount,
                total_amount=total,
                provider_transaction_id=f"MPESA-{random.randint(1000000000, 9999999999)}",
                checkout_camera=checkout_camera,
                face_recognition_confidence=Decimal(str(random.uniform(92.0, 99.9))),
                status=random.choice(['COMPLETED', 'COMPLETED', 'COMPLETED', 'FAILED']),
                initiated_at=session.exit_time if session.exit_time else timezone.now(),
                completed_at=session.exit_time + timedelta(seconds=random.randint(2, 30)) if session.exit_time else None,
                receipt_number=f"RCP-{timezone.now().strftime('%Y%m%d')}-{str(created+1).zfill(4)}"
            )
            
            self.transactions.append(transaction)
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} transactions'))

    # ==================== TRANSACTION ITEMS ====================
    
    def seed_transaction_items(self):
        """Seed transaction items"""
        self.stdout.write('📄 Seeding Transaction Items...')
        
        if not hasattr(self, 'transactions'):
            self.transactions = list(Transaction.objects.all())
        
        created = 0
        
        for transaction in self.transactions:
            cart_items = ShoppingCart.objects.filter(session=transaction.session)
            
            for cart_item in cart_items:
                vat_amount = cart_item.subtotal * cart_item.product.vat_rate / 100
                total = cart_item.subtotal + vat_amount
                
                TransactionItem.objects.create(
                    transaction=transaction,
                    product=cart_item.product,
                    product_name=cart_item.product.name,
                    quantity=cart_item.quantity,
                    unit_price=cart_item.unit_price,
                    vat_rate=cart_item.product.vat_rate,
                    subtotal=cart_item.subtotal,
                    vat_amount=vat_amount,
                    total=total
                )
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} transaction items'))

    # ==================== FACE RECOGNITION LOGS ====================
    
    def seed_face_recognition_logs(self):
        """Seed face recognition logs"""
        self.stdout.write('📝 Seeding Face Recognition Logs...')
        
        users_with_face = User.objects.filter(facial_data__isnull=False)
        stores = Store.objects.all()
        cameras = Camera.objects.all()
        
        created = 0
        
        for i in range(500):
            user = random.choice(users_with_face)
            store = random.choice(stores)
            camera = random.choice(cameras.filter(store=store)) if cameras.filter(store=store).exists() else None
            
            recognition_type = random.choice(['ENTRY', 'CHECKOUT', 'VERIFICATION'])
            confidence = random.uniform(70.0, 99.9)
            
            if confidence >= user.facial_data.confidence_threshold:
                result = 'SUCCESS'
            elif confidence >= 80.0:
                result = 'REJECTED'
            else:
                result = 'FAILED'
            
            FaceRecognitionLog.objects.create(
                user=user,
                camera=camera,
                store=store,
                recognition_type=recognition_type,
                result=result,
                confidence_score=Decimal(str(confidence)),
                processing_time_ms=random.randint(50, 500),
                timestamp=timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} face recognition logs'))

    # ==================== SECURITY ALERTS ====================
    
    def seed_security_alerts(self):
        """Seed security alerts"""
        self.stdout.write('⚠️ Seeding Security Alerts...')
        
        stores = Store.objects.all()
        alert_types = ['FRAUD', 'MULTIPLE_FAIL', 'UNUSUAL_ACTIVITY', 'SYSTEM_ERROR']
        severities = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        statuses = ['OPEN', 'INVESTIGATING', 'RESOLVED', 'FALSE_ALARM']
        
        created = 0
        
        for i in range(30):
            store = random.choice(stores)
            alert_type = random.choice(alert_types)
            severity = random.choice(severities)
            status = random.choice(statuses)
            
            SecurityAlert.objects.create(
                alert_code=f"ALERT-{timezone.now().strftime('%Y%m%d')}-{str(i+1).zfill(4)}",
                alert_type=alert_type,
                severity=severity,
                status=status,
                store=store,
                description=f"{alert_type} detected at {store.name}",
                created_at=timezone.now() - timedelta(days=random.randint(0, 30)),
                resolved_at=timezone.now() - timedelta(days=random.randint(0, 15)) if status == 'RESOLVED' else None
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} security alerts'))

    # ==================== AUDIT LOGS ====================
    
    def seed_audit_logs(self):
        """Seed audit logs"""
        self.stdout.write('📋 Seeding Audit Logs...')
        
        users = User.objects.all()
        actions = ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'PAYMENT']
        models = ['Transaction', 'Product', 'Store', 'User', 'ShoppingSession']
        
        created = 0
        
        for i in range(200):
            AuditLog.objects.create(
                user=random.choice(users),
                action=random.choice(actions),
                model_name=random.choice(models),
                object_id=str(random.randint(1, 1000)),
                ip_address=f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                timestamp=timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} audit logs'))

    # ==================== DAILY SALES REPORTS ====================
    
    def seed_daily_sales_reports(self):
        """Seed daily sales reports"""
        self.stdout.write('📊 Seeding Daily Sales Reports...')
        
        stores = Store.objects.all()
        created = 0
        
        for store in stores:
            # Create reports for last 30 days
            for i in range(30):
                report_date = (timezone.now() - timedelta(days=i)).date()
                
                # Get transactions for this store on this date
                day_transactions = Transaction.objects.filter(
                    store=store,
                    status='COMPLETED',
                    initiated_at__date=report_date
                )
                
                total_transactions = day_transactions.count()
                total_revenue = sum(t.total_amount for t in day_transactions)
                total_vat = sum(t.vat_amount for t in day_transactions)
                unique_customers = day_transactions.values('user').distinct().count()
                
                DailySalesReport.objects.create(
                    store=store,
                    report_date=report_date,
                    total_transactions=total_transactions,
                    total_revenue=Decimal(str(total_revenue)),
                    total_vat=Decimal(str(total_vat)),
                    unique_customers=unique_customers,
                    new_customers=random.randint(0, unique_customers),
                    total_items_sold=random.randint(total_transactions * 2, total_transactions * 10),
                    average_basket_size=Decimal(str(total_revenue / total_transactions)) if total_transactions > 0 else Decimal('0.00'),
                    successful_recognitions=random.randint(total_transactions, total_transactions + 50),
                    failed_recognitions=random.randint(0, 10),
                    average_confidence=Decimal(str(random.uniform(94.0, 98.5)))
                )
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} daily sales reports'))

    # ==================== CUSTOMER BEHAVIOR ====================
    
    def seed_customer_behavior(self):
        """Seed customer behavior data"""
        self.stdout.write('👤 Seeding Customer Behavior...')
        
        users = User.objects.filter(is_verified=True)
        stores = Store.objects.all()
        categories = ProductCategory.objects.filter(parent__isnull=False)
        
        created = 0
        
        for user in users:
            user_transactions = Transaction.objects.filter(user=user, status='COMPLETED')
            user_sessions = ShoppingSession.objects.filter(user=user)
            
            CustomerBehavior.objects.create(
                user=user,
                total_visits=user_sessions.count(),
                total_purchases=user_transactions.count(),
                total_spent=sum(t.total_amount for t in user_transactions),
                favorite_store=random.choice(stores),
                favorite_categories=[str(c.id) for c in random.sample(list(categories), min(3, len(categories)))],
                last_visit=user_sessions.order_by('-entry_time').first().entry_time if user_sessions.exists() else None,
                last_purchase=user_transactions.order_by('-initiated_at').first().initiated_at if user_transactions.exists() else None,
                average_session_duration=random.randint(15, 45)
            )
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} customer behavior records'))

    # ==================== PROMOTIONS ====================
    
    def seed_promotions(self):
        """Seed promotions"""
        self.stdout.write('🎁 Seeding Promotions...')
        
        stores = Store.objects.all()
        products = Product.objects.all()
        categories = ProductCategory.objects.all()
        
        promotions_data = [
            ('Black Friday Sale', 'BF2024', 'PERCENTAGE', 20.00),
            ('Weekend Special', 'WEEKEND', 'PERCENTAGE', 10.00),
            ('New Customer Discount', 'NEWCUST', 'PERCENTAGE', 15.00),
            ('Buy 2 Get 10% Off', 'BUY2', 'PERCENTAGE', 10.00),
            ('Flash Sale', 'FLASH', 'FIXED', 100.00),
        ]
        
        created = 0
        
        for name, code, discount_type, discount_value in promotions_data:
            promotion, created_new = Promotion.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'description': f"{name} - Limited time offer!",
                    'discount_type': discount_type,
                    'discount_value': Decimal(str(discount_value)),
                    'minimum_purchase': Decimal('500.00'),
                    'start_date': timezone.now() - timedelta(days=random.randint(1, 30)),
                    'end_date': timezone.now() + timedelta(days=random.randint(30, 90)),
                    'is_active': True,
                    'usage_limit': random.randint(100, 1000),
                    'usage_per_customer': random.randint(1, 5),
                    'times_used': random.randint(0, 50)
                }
            )
            
            if created_new:
                # Add applicable stores and products
                promotion.applicable_stores.add(*random.sample(list(stores), random.randint(1, min(5, len(stores)))))
                promotion.applicable_products.add(*random.sample(list(products), random.randint(5, min(20, len(products)))))
                created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} promotions'))

    # ==================== LOYALTY PROGRAMS ====================
    
    def seed_loyalty_programs(self):
        """Seed loyalty programs"""
        self.stdout.write('⭐ Seeding Loyalty Programs...')
        
        users = User.objects.filter(is_verified=True)
        tiers = ['BRONZE', 'SILVER', 'GOLD', 'PLATINUM']
        
        created = 0
        self.loyalty_programs = []
        
        for user in users:
            user_transactions = Transaction.objects.filter(user=user, status='COMPLETED')
            total_spent = sum(t.total_amount for t in user_transactions)
            
            # Calculate tier based on spending
            if total_spent > 50000:
                tier = 'PLATINUM'
            elif total_spent > 25000:
                tier = 'GOLD'
            elif total_spent > 10000:
                tier = 'SILVER'
            else:
                tier = 'BRONZE'
            
            total_points = int(total_spent)  # 1 KES = 1 point
            redeemed_points = random.randint(0, total_points // 2)
            current_balance = total_points - redeemed_points
            
            loyalty = LoyaltyProgram.objects.create(
                user=user,
                total_points_earned=total_points,
                total_points_redeemed=redeemed_points,
                current_balance=current_balance,
                current_tier=tier,
                is_active=True,
                last_activity=user_transactions.order_by('-initiated_at').first().initiated_at if user_transactions.exists() else None
            )
            
            self.loyalty_programs.append(loyalty)
            created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} loyalty programs'))

    # ==================== LOYALTY TRANSACTIONS ====================
    
    def seed_loyalty_transactions(self):
        """Seed loyalty transactions"""
        self.stdout.write('💎 Seeding Loyalty Transactions...')
        
        if not hasattr(self, 'loyalty_programs'):
            self.loyalty_programs = list(LoyaltyProgram.objects.all())
        
        created = 0
        
        for loyalty in self.loyalty_programs:
            user_transactions = Transaction.objects.filter(user=loyalty.user, status='COMPLETED')
            
            balance = 0
            for transaction in user_transactions:
                # Earn points
                points_earned = int(transaction.total_amount)
                balance += points_earned
                
                LoyaltyTransaction.objects.create(
                    loyalty_program=loyalty,
                    transaction_type='EARN',
                    points=points_earned,
                    balance_after=balance,
                    related_transaction=transaction,
                    description=f"Earned from purchase at {transaction.store.name}",
                    expires_at=timezone.now().date() + timedelta(days=365)
                )
                created += 1
                
                # Occasionally redeem points
                if random.random() > 0.7 and balance > 100:
                    points_redeemed = random.randint(50, min(500, balance))
                    balance -= points_redeemed
                    
                    LoyaltyTransaction.objects.create(
                        loyalty_program=loyalty,
                        transaction_type='REDEEM',
                        points=points_redeemed,
                        balance_after=balance,
                        description="Points redeemed for discount"
                    )
                    created += 1
        
        self.stdout.write(self.style.SUCCESS(f'  ✓ Created {created} loyalty transactions'))

    def print_summary(self):
        """Print summary of seeded data"""
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('📊 SEEDING SUMMARY'))
        self.stdout.write('='*60)
        
        summary = [
            ('Counties', County.objects.count()),
            ('Users', User.objects.count()),
            ('Facial Data', FacialData.objects.count()),
            ('Payment Accounts', PaymentAccount.objects.count()),
            ('Stores', Store.objects.count()),
            ('Cameras', Camera.objects.count()),
            ('Product Categories', ProductCategory.objects.count()),
            ('Products', Product.objects.count()),
            ('Store Inventory', StoreInventory.objects.count()),
            ('Shopping Sessions', ShoppingSession.objects.count()),
            ('Shopping Cart Items', ShoppingCart.objects.count()),
            ('Transactions', Transaction.objects.count()),
            ('Transaction Items', TransactionItem.objects.count()),
            ('Face Recognition Logs', FaceRecognitionLog.objects.count()),
            ('Security Alerts', SecurityAlert.objects.count()),
            ('Audit Logs', AuditLog.objects.count()),
            ('Daily Sales Reports', DailySalesReport.objects.count()),
            ('Customer Behavior', CustomerBehavior.objects.count()),
            ('Promotions', Promotion.objects.count()),
            ('Loyalty Programs', LoyaltyProgram.objects.count()),
            ('Loyalty Transactions', LoyaltyTransaction.objects.count()),
        ]
        
        for model_name, count in summary:
            self.stdout.write(f'  {model_name:.<35} {count:>10,}')
        
        self.stdout.write('='*60)
        self.stdout.write('\n✨ Your BiashAI database is now fully populated!')
        self.stdout.write('🔐 Admin credentials: admin / admin123')
        self.stdout.write('👥 User credentials: Use any username with password: password123')
        self.stdout.write('\n')