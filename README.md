# Seasonal Product Management System

A Flask-based e-commerce system that manages seasonal products, orders, and customer carts with features like OAuth authentication, admin controls, and coupon management.

## Features

### Authentication & Security

- Multi-provider OAuth support (Google, GitHub)
- Two-factor authentication (2FA)
- Password reset functionality
- CSRF protection using Flask-WTF
- Role-based access control (Admin/Customer)

### Shopping Experience

- Browse products by category and season
- View product availability and pricing
- Dark mode support

### Cart Management

- Multiple active carts per customer
- Add/remove products
- Update quantities
- Apply coupon codes
- Generate random cart within budget
- Cart naming and switching

### Admin Features

- Toggle product seasons
- Update inventory stock
- Manage seasonal product availability
- View customer orders and details

### Order System

- Order tracking
- Multiple pending orders (Carts)
- Order completion with inventory updates
- Order history

## Setup

```python
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # or Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Initialize database and load sample data
python manage.py reset

# Start the application
python app.py
```

## Technical Details

### Database Models

- **Product**: Name, price, inventory level, category, season status
- **Customer**: Profile, authentication, cart management
- **Order**: Shopping cart state, completed orders
- **Category**: Product categorization
- **Coupon**: Discount codes with minimum purchase requirements
- **Season**: Seasonal product groupings

### Tech Stack

- **Backend**: Flask, Python
- **Database**: SQLAlchemy ORM
- **Authentication**: Flask-Login, OAuth 2.0
- **Forms**: WTForms with CSRF protection
- **Email**: Flask-Mail for notifications
- **Frontend**: Bootstrap 5, Dark mode support

## Testing

Comprehensive test suite includes:

1. Authentication tests

   - Password hashing
   - Login functionality
   - Access control

2. Cart operation tests
   - Adding items
   - Updating quantities
   - Removing items
   - Budget-based cart generation

## Security Features

- CSRF Protection against cross-site request forgery
- Secure password hashing
- Two-factor authentication via email
- Session management
- OAuth integration for secure third-party authentication
