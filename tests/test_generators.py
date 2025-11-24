# tests/test_generators.py
"""Tests to verify that test data generators work correctly"""

import pytest
from hypothesis import given, assume, settings, HealthCheck
import tests.generators as gen


@pytest.mark.unit
def test_generators_module_imports():
    """Test that all generators are importable"""
    assert hasattr(gen, 'inventory_item')
    assert hasattr(gen, 'sale_with_items')
    assert hasattr(gen, 'repair_order')
    assert hasattr(gen, 'repair_part')
    assert hasattr(gen, 'user')
    assert hasattr(gen, 'password')
    assert hasattr(gen, 'strong_password')


@pytest.mark.property
@given(item=gen.inventory_item())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_inventory_item_generator(item):
    """Test that inventory_item generator produces valid items"""
    assert 'sku' in item
    assert 'name' in item
    assert 'quantity' in item
    assert 'buy_price' in item
    assert 'sell_price' in item
    
    # Validate constraints
    assert len(item['sku']) >= 3
    assert len(item['name']) >= 1
    assert item['quantity'] >= 0
    assert item['buy_price'] >= 0.01
    assert item['sell_price'] >= 0.01
    assert item['sell_price'] >= item['buy_price']  # Realistic pricing


@pytest.mark.property
@given(item=gen.inventory_item_with_stock(min_quantity=5))
def test_inventory_item_with_stock_generator(item):
    """Test that inventory_item_with_stock ensures minimum stock"""
    assert item['quantity'] >= 5


@pytest.mark.property
@given(sale=gen.sale_with_items())
def test_sale_with_items_generator(sale):
    """Test that sale_with_items generator produces valid sales"""
    assert 'customer_name' in sale
    assert 'items' in sale
    assert len(sale['items']) >= 1
    
    for item in sale['items']:
        assert 'item_id' in item
        assert 'quantity' in item
        assert 'unit_price' in item
        assert 'cost_price' in item
        assert item['quantity'] >= 1
        assert item['unit_price'] >= item['cost_price']


@pytest.mark.property
@given(order=gen.repair_order())
def test_repair_order_generator(order):
    """Test that repair_order generator produces valid orders"""
    assert 'order_number' in order
    assert 'customer_name' in order
    assert 'customer_phone' in order
    assert 'device_model' in order
    assert 'imei' in order
    
    # Validate constraints
    assert len(order['order_number']) >= 5
    assert len(order['customer_phone']) >= 10
    assert len(order['imei']) == 15


@pytest.mark.property
@given(repair=gen.repair_with_parts())
def test_repair_with_parts_generator(repair):
    """Test that repair_with_parts generator produces consistent data"""
    order = repair['order']
    parts = repair['parts']
    
    # Calculate expected total
    expected_total = sum(p['qty'] * p['unit_price'] for p in parts)
    
    # Should match order total_estimate
    assert abs(order['total_estimate'] - expected_total) < 0.01


@pytest.mark.property
@given(user_data=gen.user())
def test_user_generator(user_data):
    """Test that user generator produces valid users"""
    assert 'username' in user_data
    assert 'password' in user_data
    assert 'full_name' in user_data
    assert 'role' in user_data
    
    assert len(user_data['username']) >= 3
    assert len(user_data['password']) >= 8
    assert user_data['role'] in ['Admin', 'Manager', 'Cashier', 'Technician']


@pytest.mark.property
@given(pwd=gen.strong_password())
def test_strong_password_generator(pwd):
    """Test that strong_password generator meets complexity requirements"""
    assert len(pwd) >= 8
    assert any(c.isupper() for c in pwd)
    assert any(c.islower() for c in pwd)
    assert any(c.isdigit() for c in pwd)
    assert any(c in '!@#$%^&*' for c in pwd)


@pytest.mark.property
@given(pwd=gen.weak_password())
def test_weak_password_generator(pwd):
    """Test that weak_password generator produces weak passwords"""
    # At least one of these should be true for a weak password
    is_weak = (
        len(pwd) < 8 or
        not any(c.isupper() for c in pwd) or
        not any(c.islower() for c in pwd) or
        not any(c.isdigit() for c in pwd) or
        pwd in ['password', '12345678']
    )
    assert is_weak


@pytest.mark.property
@given(phone=gen.phone_number_variants())
def test_phone_number_variants_generator(phone):
    """Test that phone_number_variants generates various formats"""
    # Just verify it generates something
    assert isinstance(phone, str)


@pytest.mark.property
@given(log=gen.audit_log_entry())
def test_audit_log_entry_generator(log):
    """Test that audit_log_entry generator produces valid entries"""
    assert 'timestamp' in log
    assert 'user' in log
    assert 'action_type' in log
    assert 'entity_type' in log
    assert 'entity_id' in log
    
    assert log['action_type'] in ['CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE']
    assert log['entity_type'] in ['repair', 'inventory', 'user', 'sale']


@pytest.mark.unit
def test_calculate_sale_total():
    """Test sale total calculation helper"""
    items = [
        {'quantity': 2, 'unit_price': 10.0, 'item_id': 1, 'cost_price': 5.0},
        {'quantity': 3, 'unit_price': 15.0, 'item_id': 2, 'cost_price': 8.0},
    ]
    total = gen.calculate_sale_total(items)
    assert total == 65.0  # (2*10) + (3*15)


@pytest.mark.unit
def test_calculate_repair_total():
    """Test repair total calculation helper"""
    parts = [
        {'qty': 1, 'unit_price': 100.0, 'part_name': 'Screen', 'repair_id': 1, 'cost_price': 50.0},
        {'qty': 2, 'unit_price': 25.0, 'part_name': 'Battery', 'repair_id': 1, 'cost_price': 15.0},
    ]
    total = gen.calculate_repair_total(parts)
    assert total == 150.0  # (1*100) + (2*25)


@pytest.mark.unit
def test_calculate_profit():
    """Test profit calculation helper"""
    profit = gen.calculate_profit(1000.0, 600.0)
    assert profit == 400.0
