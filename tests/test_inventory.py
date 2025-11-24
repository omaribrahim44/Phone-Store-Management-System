# tests/test_inventory.py
"""Property-based and unit tests for inventory operations"""

import pytest
from hypothesis import given, assume
import tests.generators as gen
from modules import models
from modules.db import get_conn


@pytest.mark.property
def test_inventory_non_negative(test_db):
    """
    **Feature: data-integrity-testing, Property 1: Non-negative inventory quantities**
    **Validates: Requirements 1.1**
    
    For any inventory item added to the system, the stored quantity must be 
    greater than or equal to zero.
    """
    @given(item=gen.inventory_item())
    def check_non_negative(item):
        # Clean up inventory table before each example
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM inventory")
        conn.commit()
        conn.close()
        
        # Add the inventory item
        result = models.add_inventory_item(
            sku=item['sku'],
            name=item['name'],
            qty=item['quantity'],
            buy=item['buy_price'],
            sell=item['sell_price'],
            category=item['category'],
            desc=item.get('description', '')
        )
        
        # Should succeed
        assert result is True
        
        # Verify the quantity in database is non-negative
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT quantity FROM inventory WHERE sku = ?", (item['sku'],))
        row = c.fetchone()
        conn.close()
        
        assert row is not None, f"Item with SKU {item['sku']} not found in database"
        stored_quantity = row[0]
        assert stored_quantity >= 0, f"Quantity {stored_quantity} is negative"
    
    check_non_negative()



@pytest.mark.property
def test_inventory_decrease_matches_sales(test_db):
    """
    **Feature: data-integrity-testing, Property 2: Inventory decrease matches sales**
    **Validates: Requirements 1.2**
    
    For any completed sale, the inventory quantity decrease for each item must
    exactly equal the quantity sold.
    """
    @given(item=gen.inventory_item_with_stock(min_quantity=10, max_quantity=100))
    def check_decrease_matches(item):
        # Clean database
        conn = get_conn()
        conn.execute("DELETE FROM inventory")
        conn.execute("DELETE FROM sales")
        conn.execute("DELETE FROM sale_items")
        conn.commit()
        conn.close()
        
        # Add inventory item
        models.add_inventory_item(
            sku=item['sku'],
            name=item['name'],
            qty=item['quantity'],
            buy=item['buy_price'],
            sell=item['sell_price'],
            category=item['category'],
            desc=item.get('description', '')
        )
        
        # Get item_id
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT item_id, quantity FROM inventory WHERE sku = ?", (item['sku'],))
        row = c.fetchone()
        item_id = row[0]
        initial_qty = row[1]
        conn.close()
        
        # Sell some quantity (less than available)
        sale_qty = min(5, initial_qty)
        
        # Decrease inventory
        result = models.decrease_inventory_quantity(item_id, sale_qty)
        assert result is True, "Failed to decrease inventory"
        
        # Verify the decrease matches exactly
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
        final_qty = c.fetchone()[0]
        conn.close()
        
        expected_qty = initial_qty - sale_qty
        assert final_qty == expected_qty, f"Inventory decrease mismatch: expected {expected_qty}, got {final_qty}"
    
    check_decrease_matches()


@pytest.mark.property
def test_sale_rollback_restores_inventory(test_db):
    """
    **Feature: data-integrity-testing, Property 3: Sale rollback restores inventory**
    **Validates: Requirements 1.4**
    
    For any sale transaction that fails, the inventory quantities must be
    identical to their state before the sale attempt.
    """
    @given(item=gen.inventory_item_with_stock(min_quantity=10, max_quantity=100))
    def check_rollback_restores(item):
        # Clean database
        conn = get_conn()
        conn.execute("DELETE FROM inventory")
        conn.commit()
        conn.close()
        
        # Add inventory item
        models.add_inventory_item(
            sku=item['sku'],
            name=item['name'],
            qty=item['quantity'],
            buy=item['buy_price'],
            sell=item['sell_price'],
            category=item['category'],
            desc=item.get('description', '')
        )
        
        # Get item_id and initial quantity
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT item_id, quantity FROM inventory WHERE sku = ?", (item['sku'],))
        row = c.fetchone()
        item_id = row[0]
        initial_qty = row[1]
        conn.close()
        
        # Attempt to decrease inventory but force a rollback
        from modules.transaction_manager import transaction
        try:
            with transaction() as conn:
                c = conn.cursor()
                # Decrease quantity
                c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?", (5, item_id))
                # Force error to trigger rollback
                raise RuntimeError("Forced rollback")
        except RuntimeError:
            pass
        
        # Verify quantity is restored to initial value
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
        final_qty = c.fetchone()[0]
        conn.close()
        
        assert final_qty == initial_qty, f"Inventory not restored after rollback: expected {initial_qty}, got {final_qty}"
    
    check_rollback_restores()


@pytest.mark.unit
def test_check_inventory_availability_sufficient_stock(test_db):
    """Test that availability check returns True when stock is sufficient"""
    # Add item with 10 units
    models.add_inventory_item("TEST-AVAIL-1", "Test Item", 10, 100.0, 150.0, "Test", "")
    
    # Get item_id
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TEST-AVAIL-1",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Check availability for 5 units (should be available)
    available = models.check_inventory_availability(item_id, 5)
    assert available is True


@pytest.mark.unit
def test_check_inventory_availability_insufficient_stock(test_db):
    """Test that availability check returns False when stock is insufficient"""
    # Add item with 10 units
    models.add_inventory_item("TEST-AVAIL-2", "Test Item", 10, 100.0, 150.0, "Test", "")
    
    # Get item_id
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TEST-AVAIL-2",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Check availability for 15 units (should NOT be available)
    available = models.check_inventory_availability(item_id, 15)
    assert available is False


@pytest.mark.unit
def test_decrease_inventory_prevents_negative(test_db):
    """Test that decreasing inventory below zero is prevented"""
    # Add item with 5 units
    models.add_inventory_item("TEST-NEG-1", "Test Item", 5, 100.0, 150.0, "Test", "")
    
    # Get item_id
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TEST-NEG-1",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Try to decrease by 10 (more than available)
    result = models.decrease_inventory_quantity(item_id, 10)
    
    # Should fail
    assert result is False
    
    # Verify quantity unchanged
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
    qty = c.fetchone()[0]
    conn.close()
    
    assert qty == 5  # Should still be 5


@pytest.mark.unit
def test_add_inventory_validates_negative_price(test_db):
    """Test that negative prices are rejected"""
    result = models.add_inventory_item("TEST-PRICE-1", "Test", 10, -50.0, 100.0, "Test", "")
    assert result is False


@pytest.mark.unit
def test_add_inventory_validates_negative_quantity(test_db):
    """Test that negative quantities are rejected"""
    result = models.add_inventory_item("TEST-QTY-1", "Test", -5, 50.0, 100.0, "Test", "")
    assert result is False


@pytest.mark.unit
def test_add_inventory_validates_empty_sku(test_db):
    """Test that empty SKUs are rejected"""
    result = models.add_inventory_item("", "Test", 10, 50.0, 100.0, "Test", "")
    assert result is False


@pytest.mark.unit
def test_add_inventory_validates_empty_name(test_db):
    """Test that empty names are rejected"""
    result = models.add_inventory_item("TEST-NAME-1", "", 10, 50.0, 100.0, "Test", "")
    assert result is False


@pytest.mark.unit
def test_get_inventory_item_by_id(test_db):
    """Test retrieving inventory item by ID"""
    models.add_inventory_item("TEST-GET-1", "Test Item", 10, 100.0, 150.0, "Test", "Description")
    
    # Get item_id
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TEST-GET-1",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Get item by ID
    item = models.get_inventory_item_by_id(item_id)
    
    assert item is not None
    assert item[1] == "TEST-GET-1"  # SKU
    assert item[2] == "Test Item"  # Name
    assert item[5] == 10  # Quantity


@pytest.mark.unit
def test_get_inventory_item_by_sku(test_db):
    """Test retrieving inventory item by SKU"""
    models.add_inventory_item("TEST-GET-2", "Test Item", 10, 100.0, 150.0, "Test", "Description")
    
    # Get item by SKU
    item = models.get_inventory_item_by_sku("TEST-GET-2")
    
    assert item is not None
    assert item[1] == "TEST-GET-2"  # SKU
    assert item[2] == "Test Item"  # Name
    assert item[5] == 10  # Quantity


@pytest.mark.unit
def test_update_inventory_quantity(test_db):
    """Test updating inventory quantity"""
    models.add_inventory_item("TEST-UPD-1", "Test Item", 10, 100.0, 150.0, "Test", "")
    
    # Get item_id
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TEST-UPD-1",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Update quantity
    result = models.update_inventory_quantity(item_id, 25)
    assert result is True
    
    # Verify updated
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
    qty = c.fetchone()[0]
    conn.close()
    
    assert qty == 25
