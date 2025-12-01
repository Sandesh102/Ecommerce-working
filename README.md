# Django E-commerce Application

A full-featured e-commerce platform built with Django that includes product management, user authentication, shopping cart, order processing, and payment integration.

## Features

- **Product Management**: Create, view, and manage products with categories, images, and descriptions
- **User Authentication**: Register, login, and profile management with Google OAuth support
- **Shopping Cart**: Add/remove products, adjust quantities
- **Order Processing**: Place orders with delivery address management
- **Payment Integration**: Support for Khalti payment gateway and QR code payments
- **Admin Panel**: Manage products, orders, and users
- **Responsive Design**: Mobile-friendly interface

## Project Structure

```
ecommerce/
├── ecommerce/           # Main project settings and configuration
├── products/            # Products app - models, views, templates
├── users/               # Users app - authentication, profiles
├── media/               # Uploaded media files (images, payment proofs)
├── staticfiles/         # Collected static assets for production
├── templates/           # Base templates
├── manage.py            # Django management utility
└── requirements.txt     # Python dependencies
```

## Key Components

### Models
- **Category**: Product categories with descriptions
- **Product**: Products with multiple images, pricing, and stock management
- **CartItem**: Shopping cart items for each user
- **DeliveryAddress**: User delivery addresses
- **Order**: Order management with status tracking
- **UserProfile**: Extended user information

### Apps
1. **Products App**: Handles all product-related functionality
2. **Users App**: Manages user authentication and profiles

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ecommerce
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file based on `.env.example`:
   ```env
   SECRET_KEY=your-secret-key
   DEBUG=True
   ```

5. Run database migrations:
   ```bash
   python manage.py migrate
   ```

6. Load initial data (optional):
   ```bash
   python manage.py loaddata data.json
   ```

7. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```

8. Start the development server:
   ```bash
   python manage.py runserver
   ```
   
   Or use the convenience scripts:
   - On Windows: `runserver.bat`
   - On Linux/Mac: `runserver.sh`

## Deployment

This application is configured for deployment on Render with the following features:
- PostgreSQL database support
- Static file serving with WhiteNoise
- Media file storage
- Environment variable configuration
- Automated build process via `build.sh`

### Environment Variables for Production
- `SECRET_KEY`: Django secret key
- `DB_ENGINE`: Database engine (e.g., `django.db.backends.postgresql`)
- `DB_NAME`: Database name
- `DB_USER`: Database user
- `DB_PASSWORD`: Database password
- `DB_HOST`: Database host
- `DEBUG`: Should be False in production

## Google OAuth Setup

To enable Google login:
1. Set up credentials in Google Cloud Console
2. Add redirect URIs as specified in `GOOGLE_OAUTH_SETUP.md`
3. Configure environment variables:
   ```
   GOOGLE_OAUTH2_CLIENT_ID=your-client-id
   GOOGLE_OAUTH2_CLIENT_SECRET=your-client-secret
   ```

## Payment Integration

The application supports:
- **Khalti Payment Gateway**: Configure with `KHALTI_PUBLIC_KEY` and `KHALTI_SECRET_KEY`
- **QR Code Payments**: Manual verification process with payment proof uploads

## Key URLs

- `/` - Home page with products
- `/accounts/login/` - User login
- `/accounts/register/` - User registration
- `/cart/` - Shopping cart
- `/checkout/` - Checkout process
- `/payment/` - Payment processing
- `/admin/` - Administration panel

## Development Commands

- Run development server: `python manage.py runserver`
- Create migrations: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`
- Collect static files: `python manage.py collectstatic`
- Create superuser: `python manage.py createsuperuser`

## Requirements

- Python 3.13+
- Django 5.2+
- PostgreSQL (for production)
- Pillow for image processing
- Other dependencies listed in `requirements.txt`

## License

This project is proprietary and intended for educational purposes.
