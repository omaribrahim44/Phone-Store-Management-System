# tests/generators.py
"""Hypothesis test data generators for property-based testing"""

from hypothesis import strategies as st
from datetime import datetime, timedelta
import string


# ==================== Basic Strategies ====================

# Valid SKU: alphanumeric with hyphens, 3-20 chars
valid_sku = st.text(
    alphabet=string.ascii_uppercase + string.digits + '-',
    min_size=3,
    max_size=20
).filter(lambda x: x and not x.startswith('-') and not x.endswith('-'))

# Valid names: non-empty strings
valid_name = st.text(min_size=1, max_size=100).filter(lambda x: x.strip())

# Valid descriptions
valid_description = st.text(min_size=0, max_size=500)

# Valid categories
categories = st.sampled_from(['Phones', 'Accessories', 'Parts', 'Services', 'Repairs', 'General'])

# Non-negative quantities
non_negative_quantity = st.integers(min_value=0, max_value=10000)

# Positive quantities (for sales)
positive_quantity = st.integers(min_value=1, max_value=100)

# Valid prices (non-negative, reasonable range)
valid_price = st.floats(
    min_value=0.01,
    max_value=100000.0,
    allow_nan=False,
    allow_infinity=False
).map(lambda x: round(x, 2))

# Phone numbers (10-15 digits)
phone_number = st.from_regex(r'\d{10,15}', fullmatch=True)

# IMEI numbers (15 digits)
imei_number = st.from_regex(r'\d{15}', fullmatch=True)

# Device models
device_models = st.sampled_from([
    'iPhone 12', 'iPhone 13', 'iPhone 14', 'iPhone 15',
    'Samsung S21', 'Samsung S22', 'Samsung S23', 'Samsung S24',
    'Google Pixel 6', 'Google Pixel 7', 'Google Pixel 8',
    'OnePlus 9', 'OnePlus 10', 'OnePlus 11',
    'Xiaomi Mi 11', 'Xiaomi Mi 12', 'Xiaomi Mi 13'
])

# Repair statuses
repair_statuses = st.sampled_from([
    'Received', 'Diagnosed', 'In Progress', 'Waiting Parts',
    'Completed', 'Delivered', 'Cancelled'
])

# User roles
user_roles = st.sampled_from(['Admin', 'Manager', 'Cashier', 'Technician'])

# Dates (ISO format) - using fixed reference date to avoid flakiness
_REFERENCE_DATE = datetime(2024, 1, 1)

def date_strategy(days_back=365, days_forward=365):
    """Generate dates within a range from a fixed reference date"""
    return st.datetimes(
        min_value=_REFERENCE_DATE - timedelta(days=days_back),
        max_value=_REFERENCE_DATE + timedelta(days=days_forward)
    ).map(lambda dt: dt.date().isoformat())


# ==================== Composite Strategies ====================

@st.composite
def inventory_item(draw, with_id=False):
    """
    Generate a valid inventory item.
    
    Args:
        with_id: If True, include item_id (for existing items)
    """
    item = {
        'sku': draw(valid_sku),
        'name': draw(valid_name),
        'category': draw(categories),
        'description': draw(valid_description),
        'quantity': draw(non_negative_quantity),
        'buy_price': draw(valid_price),
        'sell_price': draw(valid_price),
    }
    
    if with_id:
        item['item_id'] = draw(st.integers(min_value=1, max_value=100000))
    
    # Ensure sell_price >= buy_price for realistic data
    if item['sell_price'] < item['buy_price']:
        item['sell_price'] = item['buy_price'] * 1.2
    
    return item


@st.composite
def inventory_item_with_stock(draw, min_quantity=1, max_quantity=100):
    """Generate inventory item with guaranteed stock"""
    item = draw(inventory_item())
    item['quantity'] = draw(st.integers(min_value=min_quantity, max_value=max_quantity))
    return item


@st.composite
def sale_item(draw, item_id=None, max_quantity=10):
    """
    Generate a sale item (for sale_items table).
    
    Args:
        item_id: Specific item_id to use, or None to generate
        max_quantity: Maximum quantity to sell
    """
    if item_id is None:
        item_id = draw(st.integers(min_value=1, max_value=1000))
    
    unit_price = draw(valid_price)
    cost_price = draw(valid_price)
    
    # Ensure unit_price >= cost_price
    if unit_price < cost_price:
        unit_price = cost_price * 1.3
    
    return {
        'item_id': item_id,
        'quantity': draw(st.integers(min_value=1, max_value=max_quantity)),
        'unit_price': round(unit_price, 2),
        'cost_price': round(cost_price, 2)
    }


@st.composite
def sale_with_items(draw, min_items=1, max_items=10):
    """
    Generate a complete sale with items.
    
    Returns dict with customer_name and items list.
    """
    num_items = draw(st.integers(min_value=min_items, max_value=max_items))
    
    # Generate unique item_ids for this sale
    item_ids = draw(st.lists(
        st.integers(min_value=1, max_value=1000),
        min_size=num_items,
        max_size=num_items,
        unique=True
    ))
    
    items = [draw(sale_item(item_id=iid)) for iid in item_ids]
    
    return {
        'customer_name': draw(valid_name),
        'items': items
    }


@st.composite
def repair_order(draw, with_id=False):
    """
    Generate a repair order.
    
    Args:
        with_id: If True, include repair_id
    """
    order = {
        'order_number': draw(st.text(
            alphabet=string.ascii_uppercase + string.digits,
            min_size=5,
            max_size=20
        )),
        'customer_name': draw(valid_name),
        'customer_phone': draw(phone_number),
        'device_model': draw(device_models),
        'imei': draw(imei_number),
        'reported_problem': draw(st.text(min_size=10, max_size=200)),
        'received_date': datetime.now().isoformat(),
        'estimated_delivery': draw(date_strategy(days_back=0, days_forward=30)),
        'status': draw(repair_statuses),
        'technician': draw(valid_name),
        'total_estimate': draw(valid_price),
        'notes': draw(valid_description)
    }
    
    if with_id:
        order['repair_id'] = draw(st.integers(min_value=1, max_value=100000))
    
    return order


@st.composite
def repair_part(draw, repair_id=None):
    """
    Generate a repair part.
    
    Args:
        repair_id: Specific repair_id to use, or None to generate
    """
    if repair_id is None:
        repair_id = draw(st.integers(min_value=1, max_value=10000))
    
    unit_price = draw(valid_price)
    cost_price = draw(valid_price)
    
    # Ensure unit_price >= cost_price
    if unit_price < cost_price:
        unit_price = cost_price * 1.5
    
    return {
        'repair_id': repair_id,
        'part_name': draw(valid_name),
        'qty': draw(positive_quantity),
        'unit_price': round(unit_price, 2),
        'cost_price': round(cost_price, 2)
    }


@st.composite
def repair_with_parts(draw, min_parts=0, max_parts=5):
    """
    Generate a repair order with parts.
    
    Returns dict with order and parts list.
    """
    order = draw(repair_order())
    num_parts = draw(st.integers(min_value=min_parts, max_value=max_parts))
    
    parts = []
    total = 0.0
    
    for _ in range(num_parts):
        part = draw(repair_part())
        parts.append(part)
        total += part['qty'] * part['unit_price']
    
    # Update total_estimate to match parts
    order['total_estimate'] = round(total, 2)
    
    return {
        'order': order,
        'parts': parts
    }


@st.composite
def user(draw, with_id=False):
    """
    Generate a user.
    
    Args:
        with_id: If True, include user_id
    """
    user_data = {
        'username': draw(st.text(
            alphabet=string.ascii_lowercase + string.digits,
            min_size=3,
            max_size=20
        )),
        'password': draw(st.text(min_size=8, max_size=50)),
        'full_name': draw(valid_name),
        'role': draw(user_roles),
        'created_at': datetime.now().isoformat()
    }
    
    if with_id:
        user_data['user_id'] = draw(st.integers(min_value=1, max_value=100000))
    
    return user_data


@st.composite
def password(draw, min_length=8, max_length=50):
    """Generate a password string"""
    return draw(st.text(
        alphabet=string.ascii_letters + string.digits + string.punctuation,
        min_size=min_length,
        max_size=max_length
    ))


@st.composite
def strong_password(draw):
    """
    Generate a strong password that meets complexity requirements.
    At least 8 chars, with uppercase, lowercase, digit, and special char.
    """
    # Ensure at least one of each required character type
    upper = draw(st.text(alphabet=string.ascii_uppercase, min_size=1, max_size=1))
    lower = draw(st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=1))
    digit = draw(st.text(alphabet=string.digits, min_size=1, max_size=1))
    special = draw(st.text(alphabet='!@#$%^&*', min_size=1, max_size=1))
    
    # Add random additional characters
    extra = draw(st.text(
        alphabet=string.ascii_letters + string.digits + '!@#$%^&*',
        min_size=4,
        max_size=20
    ))
    
    # Combine and shuffle
    chars = list(upper + lower + digit + special + extra)
    draw(st.randoms()).shuffle(chars)
    
    return ''.join(chars)


@st.composite
def weak_password(draw):
    """Generate a weak password that fails complexity requirements"""
    return draw(st.one_of(
        st.text(alphabet=string.ascii_lowercase, min_size=1, max_size=7),  # Too short
        st.text(alphabet=string.ascii_lowercase, min_size=8, max_size=20),  # No uppercase/digits
        st.text(alphabet=string.digits, min_size=8, max_size=20),  # Only digits
        st.just('password'),  # Common password
        st.just('12345678'),  # Common password
    ))


@st.composite
def phone_number_variants(draw):
    """
    Generate phone numbers in various formats (some valid, some invalid).
    Used for testing phone number validation and normalization.
    """
    return draw(st.one_of(
        # Valid formats
        st.from_regex(r'\d{10}', fullmatch=True),  # 10 digits
        st.from_regex(r'\d{11}', fullmatch=True),  # 11 digits
        st.from_regex(r'\d{3}-\d{3}-\d{4}', fullmatch=True),  # With dashes
        st.from_regex(r'\(\d{3}\) \d{3}-\d{4}', fullmatch=True),  # With parens
        st.from_regex(r'\+\d{1,3} \d{10}', fullmatch=True),  # With country code
        # Invalid formats
        st.text(alphabet=string.ascii_letters, min_size=5, max_size=15),  # Letters
        st.text(alphabet=string.digits, min_size=1, max_size=5),  # Too short
        st.text(alphabet=string.digits, min_size=20, max_size=30),  # Too long
        st.just(''),  # Empty
    ))


@st.composite
def audit_log_entry(draw):
    """Generate an audit log entry"""
    return {
        'timestamp': datetime.now().isoformat(),
        'user': draw(valid_name),
        'action_type': draw(st.sampled_from(['CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE'])),
        'entity_type': draw(st.sampled_from(['repair', 'inventory', 'user', 'sale'])),
        'entity_id': draw(st.integers(min_value=1, max_value=100000)),
        'old_value': draw(st.one_of(st.none(), st.text(max_size=100))),
        'new_value': draw(st.one_of(st.none(), st.text(max_size=100))),
        'description': draw(valid_description)
    }


# ==================== Helper Functions ====================

def calculate_sale_total(items):
    """Calculate total for a list of sale items"""
    return sum(item['quantity'] * item['unit_price'] for item in items)


def calculate_repair_total(parts):
    """Calculate total for a list of repair parts"""
    return sum(part['qty'] * part['unit_price'] for part in parts)


def calculate_profit(revenue, cost):
    """Calculate profit"""
    return revenue - cost
