# BiashAI - Face Recognition Shopping System

<div align="center">

![BiashAI Logo](docs/logo.png)

**Revolutionary Shopping Experience for Kenya**

*Shop Smart. Pay Fast. Live Free.*

[![Django](https://img.shields.io/badge/Django-5.0-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 🌟 Overview

**BiashAI** (from Swahili "Biashara" - Business + AI) is a cutting-edge Django-based face recognition shopping system designed specifically for the Kenyan market. It enables customers to shop in supermarkets using facial recognition technology for seamless, cashless, and cardless payments.

### Key Features

- 🎭 **Facial Recognition Payment** - Pay with your face, no cards or cash needed
- 📱 **M-Pesa Integration** - Seamless integration with Kenya's leading mobile money platform
- 🏪 **Multiple Store Types** - Support for unmanned, hybrid, and staff-assisted stores
- 🔐 **Advanced Security** - Multi-layer security with KYC verification and fraud detection
- 📊 **Real-time Analytics** - Comprehensive reporting and customer behavior insights
- 🎁 **Loyalty & Rewards** - Built-in loyalty program with tier-based benefits
- 🌍 **Kenya-Specific** - Designed for all 47 counties with local payment methods

---

## 🏗️ System Architecture

### Technology Stack

- **Backend Framework**: Django 5.0+
- **Database**: PostgreSQL (recommended) / MySQL / SQLite
- **Face Recognition**: OpenCV + dlib / Face Recognition library
- **Payment Integration**: M-Pesa Daraja API, Airtel Money API
- **Real-time Processing**: Django Channels (WebSocket)
- **Task Queue**: Celery + Redis
- **Storage**: AWS S3 / Local storage for media
- **API**: Django REST Framework

### Store Types Supported

1. **Unmanned Stores** 🤖
   - Fully automated checkout
   - Camera-based product tracking
   - AI-powered inventory management

2. **Hybrid Stores** 🔄
   - Staff present with automated systems
   - Faster checkout with face recognition
   - Manual override capabilities

3. **Assisted Stores** 👥
   - Staff-operated with face pay option
   - Traditional checkout enhanced with technology
   - Suitable for gradual technology adoption

---

## 📋 Database Models

### User Management
- `CustomUser` - Extended user model with Kenyan specifics (phone, ID number, M-Pesa)
- `FacialData` - Stores encrypted facial encodings and recognition settings
- `PaymentAccount` - Manages M-Pesa, Airtel Money, bank cards, etc.

### Store Management
- `County` - Kenya's 47 counties for location management
- `Store` - Physical store locations with operational details
- `Camera` - Surveillance and recognition cameras in stores

### Product Management
- `ProductCategory` - Hierarchical product categorization
- `Product` - Product catalog with barcode, SKU, pricing
- `StoreInventory` - Store-specific inventory levels

### Shopping & Transactions
- `ShoppingSession` - Tracks customer's in-store journey
- `ShoppingCart` - Real-time cart items during shopping
- `Transaction` - Payment transactions with full audit trail
- `TransactionItem` - Line items in each transaction

### Security & Compliance
- `FaceRecognitionLog` - Detailed logs of all recognition attempts
- `SecurityAlert` - Automated security incident detection
- `AuditLog` - Comprehensive audit trail for compliance

### Analytics & Marketing
- `DailySalesReport` - Aggregated daily store performance
- `CustomerBehavior` - Shopping patterns and preferences
- `Promotion` - Promotional campaigns and discounts
- `LoyaltyProgram` - Customer loyalty and rewards system

---

## 🚀 Getting Started

### Prerequisites

```bash
Python 3.11+
PostgreSQL 14+ (or MySQL 8+)
Redis 6+
Git
```

### Installation

1. **Clone the Repository**
```bash
git clone https://github.com/yourusername/biashai.git
cd biashai
```

2. **Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure Environment Variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. **Database Setup**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Create Superuser**
```bash
python manage.py createsuperuser
```

7. **Load Initial Data (Counties)**
```bash
python manage.py loaddata counties
```

8. **Run Development Server**
```bash
python manage.py runserver
```

Visit `http://localhost:8000/admin` to access the admin panel.

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=biashai_db
DB_USER=biashai_user
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# M-Pesa Configuration
MPESA_CONSUMER_KEY=your-consumer-key
MPESA_CONSUMER_SECRET=your-consumer-secret
MPESA_SHORTCODE=your-shortcode
MPESA_PASSKEY=your-passkey
MPESA_CALLBACK_URL=https://yourdomain.com/api/mpesa/callback

# Airtel Money Configuration
AIRTEL_CLIENT_ID=your-client-id
AIRTEL_CLIENT_SECRET=your-client-secret

# Face Recognition
FACE_RECOGNITION_THRESHOLD=0.95
FACE_MAX_FAILED_ATTEMPTS=3
FACE_LOCK_DURATION=1800  # 30 minutes in seconds

# Redis
REDIS_URL=redis://localhost:6379/0

# AWS S3 (if using)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=biashai-media
AWS_S3_REGION_NAME=eu-west-1

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## 💳 Payment Integration

### M-Pesa Integration

BiashAI integrates with Safaricom's M-Pesa Daraja API for seamless mobile money payments.

**Setup Steps:**

1. Register for Daraja API at [developer.safaricom.co.ke](https://developer.safaricom.co.ke)
2. Create an app and obtain Consumer Key & Secret
3. Configure STK Push for instant payments
4. Set up callback URLs for payment confirmation

**Example Payment Flow:**

```python
from payments.mpesa import MPesaClient

mpesa = MPesaClient()
response = mpesa.stk_push(
    phone_number='254712345678',
    amount=1500.00,
    account_reference='BiashAI-TRANS-001',
    transaction_desc='Shopping at BiashAI Westlands'
)
```

### Airtel Money Integration

Similar integration available for Airtel Money users.

### Supported Payment Methods

- ✅ M-Pesa
- ✅ Airtel Money
- ✅ T-Kash
- ✅ Debit/Credit Cards (via payment gateway)
- ✅ Bank Accounts (direct debit)

---

## 🎭 Face Recognition System

### How It Works

1. **Registration Phase**
   - User uploads clear face photo
   - System extracts 128-dimensional face encoding
   - Encoding stored encrypted in database
   - Linked to payment account

2. **Shopping Phase**
   - Customer enters store
   - Entry camera recognizes face
   - Shopping session initiated
   - Cameras track picked items (unmanned stores)

3. **Checkout Phase**
   - Customer scans face at checkout kiosk
   - System verifies identity (>95% confidence default)
   - Retrieves linked payment account
   - Processes payment automatically
   - Receipt sent via SMS/email

### Privacy & Security

- ✅ Only facial encodings stored (not actual images)
- ✅ End-to-end encryption
- ✅ GDPR/Kenya DPA compliant
- ✅ User consent required
- ✅ Data deletion on account closure
- ✅ Regular security audits

### Face Recognition Settings

```python
# In models.py - FacialData
confidence_threshold = 95.00  # Minimum match confidence
failed_recognition_attempts = 0  # Auto-lock after 3 failed attempts
is_locked = False  # Account lock status
```

---

## 📊 API Documentation

### REST API Endpoints

BiashAI provides a comprehensive REST API for mobile apps and third-party integrations.

**Base URL**: `https://api.biashai.co.ke/v1/`

#### Authentication
```bash
POST /api/auth/register/
POST /api/auth/login/
POST /api/auth/logout/
POST /api/auth/verify-phone/
```

#### Face Registration
```bash
POST /api/face/register/
GET /api/face/status/
PUT /api/face/update/
DELETE /api/face/delete/
```

#### Payment Accounts
```bash
GET /api/payments/accounts/
POST /api/payments/accounts/
PUT /api/payments/accounts/{id}/
DELETE /api/payments/accounts/{id}/
POST /api/payments/verify-mpesa/
```

#### Shopping
```bash
POST /api/shopping/session/start/
GET /api/shopping/session/{id}/
POST /api/shopping/cart/add/
GET /api/shopping/cart/{session_id}/
POST /api/shopping/checkout/
```

#### Transactions
```bash
GET /api/transactions/
GET /api/transactions/{id}/
GET /api/transactions/{id}/receipt/
POST /api/transactions/{id}/refund/
```

#### Stores
```bash
GET /api/stores/
GET /api/stores/{id}/
GET /api/stores/nearby/?lat={lat}&lng={lng}&radius={radius}
```

---

## 🛠️ Management Commands

### Custom Django Management Commands

```bash
# Populate Kenya counties
python manage.py load_counties

# Generate daily sales reports
python manage.py generate_daily_reports --date=2024-01-15

# Clean up expired face encodings
python manage.py cleanup_face_data --days=90

# Sync camera status
python manage.py check_cameras

# Generate loyalty points
python manage.py calculate_loyalty_points

# Export transaction data
python manage.py export_transactions --start=2024-01-01 --end=2024-12-31 --format=csv
```

---

## 🔐 Security Best Practices

### Implementation Checklist

- ✅ **Encryption**: All facial data encrypted at rest
- ✅ **HTTPS**: Enforce SSL/TLS for all connections
- ✅ **Rate Limiting**: Prevent brute force attacks
- ✅ **2FA**: Two-factor authentication for admin users
- ✅ **Input Validation**: Sanitize all user inputs
- ✅ **SQL Injection**: Use ORM parameterized queries
- ✅ **XSS Protection**: Content Security Policy headers
- ✅ **CSRF Tokens**: Django's built-in CSRF protection
- ✅ **Audit Logs**: Track all sensitive operations
- ✅ **Data Backup**: Regular automated backups

### Fraud Detection

The system includes automated fraud detection:

```python
# SecurityAlert model triggers
- Multiple failed face recognition attempts
- Unusual transaction patterns
- Geographic anomalies
- High-value transactions
- Account takeover attempts
```

---

## 📈 Analytics & Reporting

### Dashboard Metrics

- **Real-time Sales**: Live transaction tracking
- **Customer Insights**: Shopping behavior analysis
- **Inventory Management**: Stock level monitoring
- **Payment Analytics**: Payment method breakdown
- **Face Recognition Stats**: Success rates and performance
- **Store Performance**: Comparative store metrics

### Report Generation

```python
# Generate monthly sales report
from analytics.reports import SalesReport

report = SalesReport(
    store_id='uuid-here',
    start_date='2024-01-01',
    end_date='2024-01-31'
)
report.generate()
```

---

## 🎯 Roadmap

### Phase 1 - MVP (Current)
- ✅ Core face recognition system
- ✅ M-Pesa integration
- ✅ Basic admin dashboard
- ✅ Store management
- ✅ Transaction processing

### Phase 2 - Enhancement (Q2 2024)
- 🔄 Mobile app (iOS/Android)
- 🔄 Advanced analytics dashboard
- 🔄 Multi-language support (Swahili, English)
- 🔄 Voice-activated shopping
- 🔄 AR product visualization

### Phase 3 - Scale (Q3 2024)
- ⏳ Franchise management system
- ⏳ AI-powered product recommendations
- ⏳ Dynamic pricing engine
- ⏳ Supply chain integration
- ⏳ Blockchain-based receipts

### Phase 4 - Innovation (Q4 2024)
- ⏳ Smart shopping carts
- ⏳ Drone delivery integration
- ⏳ Cryptocurrency payment option
- ⏳ Social shopping features
- ⏳ Sustainability tracking

---

## 🧪 Testing

### Run Tests

```bash
# All tests
python manage.py test

# Specific app tests
python manage.py test shopping
python manage.py test payments

# Coverage report
coverage run --source='.' manage.py test
coverage report
coverage html
```

### Test Data

```bash
# Load test fixtures
python manage.py loaddata test_users
python manage.py loaddata test_products
python manage.py loaddata test_stores
```

---

## 📱 Mobile App Integration

BiashAI provides native mobile apps for customers and store managers.

### Customer App Features
- Face registration & verification
- Store locator
- Real-time cart tracking
- Digital receipts
- Loyalty points dashboard
- Transaction history
- Payment method management

### Manager App Features
- Real-time sales monitoring
- Inventory management
- Staff management
- Customer analytics
- Alert notifications
- Report generation

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md).

### Development Setup

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Standards

- Follow PEP 8 style guide
- Write docstrings for all functions
- Add unit tests for new features
- Update documentation

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

### Core Development Team
- **Project Lead**: [Your Name]
- **Lead Developer**: [Developer Name]
- **ML Engineer**: [ML Engineer Name]
- **Security Expert**: [Security Expert Name]

### Contributors
See [CONTRIBUTORS.md](CONTRIBUTORS.md) for full list.

---

## 📞 Support

### Technical Support
- **Email**: support@biashai.co.ke
- **Phone**: +254 700 000 000
- **WhatsApp**: +254 700 000 001

### Documentation
- **User Guide**: [docs.biashai.co.ke/user](https://docs.biashai.co.ke/user)
- **Developer Docs**: [docs.biashai.co.ke/dev](https://docs.biashai.co.ke/dev)
- **API Reference**: [docs.biashai.co.ke/api](https://docs.biashai.co.ke/api)

### Community
- **Discord**: [discord.gg/biashai](https://discord.gg/biashai)
- **Twitter**: [@BiashAI_Kenya](https://twitter.com/BiashAI_Kenya)
- **LinkedIn**: [BiashAI](https://linkedin.com/company/biashai)

---

## 🏆 Achievements

- 🥇 **TechCrunch Battlefield Africa 2024** - Finalist
- 🥈 **Kenya Innovation Week** - Best Retail Tech
- 🥉 **Safaricom Hackathon** - People's Choice Award

---

## 📸 Screenshots

### Customer Flow
![Customer Registration](docs/screenshots/registration.png)
![Shopping Session](docs/screenshots/shopping.png)
![Face Payment](docs/screenshots/checkout.png)

### Admin Dashboard
![Dashboard](docs/screenshots/dashboard.png)
![Analytics](docs/screenshots/analytics.png)
![Store Management](docs/screenshots/stores.png)

---

## 🔗 Related Projects

- [BiashAI Mobile App](https://github.com/biashai/mobile-app)
- [BiashAI Camera SDK](https://github.com/biashai/camera-sdk)
- [BiashAI Analytics Engine](https://github.com/biashai/analytics)

---

## 📚 Resources

### Kenyan Market Research
- Kenya Retail Trade Survey 2023
- Digital Payment Adoption in Kenya
- Privacy & Data Protection Guidelines

### Technology References
- [Django Documentation](https://docs.djangoproject.com/)
- [Face Recognition Library](https://github.com/ageitgey/face_recognition)
- [M-Pesa Daraja API](https://developer.safaricom.co.ke/)

---

<div align="center">

**Made with Love in Kenya**

*Transforming Retail, One Face at a Time*

[Website](https://biashai.co.ke) • [Documentation](https://docs.biashai.co.ke) • [Blog](https://blog.biashai.co.ke)

</div>