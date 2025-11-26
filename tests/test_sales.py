# tests/test_sales.py
"""Property-based and unit tests for sales operations"""

import pytest
from hypothesis import given, assume
import tests.generators as gen
from modules import models
from modules.db import get_conn


@pytest.mark.unit
def test_sale_total_equals_item_sum(test_db):
    """
    **Feature: data-integrity-testing, Property 4: Sale total equals item sum**
    **Validates: Requirements 2.1**
    
    For any sale with any items, the total_amount must equal the sum of
    (quantity × unit_price) for all items.
    """
    # Add inventory items
    models.add_inventory_item("TOTAL-001", "Item 1", 20, 50.0, 100.0, "Test", "")
    models.add_inventory_item("TOTAL-002", "Item 2", 15, 30.0, 75.0, "Test", "")
    models.add_inventory_item("TOTAL-003", "Item 3", 10, 20.0, 50.0, "Test", "")
    
    # Get item IDs
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TOTAL-001",))
    item1_id = c.fetchone()[0]
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TOTAL-002",))
    item2_id = c.fetchone()[0]
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TOTAL-003",))
    item3_id = c.fetchone()[0]
    conn.close()
    
    # Create sale with multiple items
    items = [
        (item1_id, 2, 100.0, 50.0),  # 2 * 100 = 200
        (item2_id, 3, 75.0, 30.0),   # 3 * 75 = 225
        (item3_id, 1, 50.0, 20.0)    # 1 * 50 = 50
    ]
    sale_id = models.create_sale("Customer", items)
    
    assert sale_id is not None
    
    # Get sale total
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT total_amount FROM sales WHERE sale_id = ?", (sale_id,))
    stored_total = c.fetchone()[0]
    conn.close()
    
    # Calculate expected total
    expected_total = 200.0 + 225.0 + 50.0  # 475.0
    
    assert abs(stored_total - expected_total) < 0.01


@pytest.mark.property
def test_sale_atomicity(test_db):
    """
    **Feature: data-integrity-testing, Property 8: Sale atomicity**
    **Validates: Requirements 3.1, 3.3**
    
    For any sale creation that encounters an error, either all related records
    (sale, sale_items, inventory updates) exist in the database or none exist.
    """
    @given(item=gen.inventory_item_with_stock(min_quantity=10, max_quantity=50))
    def check_atomicity(item):
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
            desc=""
        )
        
        # Get item_id
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT item_id FROM inventory WHERE sku = ?", (item['sku'],))
        item_id = c.fetchone()[0]
        conn.close()
        
        # Try to create a sale that will fail (request more than available)
        sale_items = [(item_id, item['quantity'] + 100, item['sell_price'], item['buy_price'])]
        sale_id = models.create_sale("Test Customer", sale_items)
        
        # Sale should fail
        assert sale_id is None, "Sale should have failed due to insufficient inventory"
        
        # Verify NO sale records exist
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM sales")
        sale_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM sale_items")
        item_count = c.fetchone()[0]
        conn.close()
        
        assert sale_count == 0, "No sales should exist after failed transaction"
        assert item_count == 0, "No sale items should exist after failed transaction"
    
    check_atomicity()


@pytest.mark.unit
def test_create_sale_with_valid_items(test_db):
    """Test creating a sale with valid items"""
    # Add inventory items
    models.add_inventory_item("SALE-001", "Item 1", 20, 50.0, 100.0, "Test", "")
    models.add_inventory_item("SALE-002", "Item 2", 15, 30.0, 60.0, "Test", "")
    
    # Get item IDs
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-001",))
    item1_id = c.fetchone()[0]
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-002",))
    item2_id = c.fetchone()[0]
    conn.close()
    
    # Create sale
    items = [
        (item1_id, 2, 100.0, 50.0),
        (item2_id, 3, 60.0, 30.0)
    ]
    sale_id = models.create_sale("John Doe", items)
    
    assert sale_id is not None
    
    # Verify sale was created
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT customer_name, total_amount FROM sales WHERE sale_id = ?", (sale_id,))
    row = c.fetchone()
    conn.close()
    
    assert row[0] == "John Doe"
    assert row[1] == 380.0  # (2*100) + (3*60)


@pytest.mark.unit
def test_create_sale_updates_inventory(test_db):
    """Test that creating a sale updates inventory quantities"""
    # Add inventory item
    models.add_inventory_item("SALE-003", "Item", 20, 50.0, 100.0, "Test", "")
    
    # Get item ID
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-003",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Create sale
    items = [(item_id, 5, 100.0, 50.0)]
    sale_id = models.create_sale("Customer", items)
    
    assert sale_id is not None
    
    # Verify inventory was decreased
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
    qty = c.fetchone()[0]
    conn.close()
    
    assert qty == 15  # 20 - 5


@pytest.mark.unit
def test_create_sale_rejects_insufficient_inventory(test_db):
    """Test that sales are rejected when inventory is insufficient"""
    # Add inventory item with only 5 units
    models.add_inventory_item("SALE-004", "Item", 5, 50.0, 100.0, "Test", "")
    
    # Get item ID
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-004",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Try to sell 10 units (more than available)
    items = [(item_id, 10, 100.0, 50.0)]
    sale_id = models.create_sale("Customer", items)
    
    # Should fail
    assert sale_id is None
    
    # Verify inventory unchanged
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
    qty = c.fetchone()[0]
    conn.close()
    
    assert qty == 5  # Should still be 5


@pytest.mark.unit
def test_create_sale_rejects_zero_inventory(test_db):
    """
    Test that sales are rejected when inventory quantity is zero.
    **Validates: Requirements 1.3**
    """
    # Add inventory item with zero quantity
    models.add_inventory_item("SALE-ZERO", "Zero Stock Item", 0, 50.0, 100.0, "Test", "")
    
    # Get item ID
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-ZERO",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Try to sell 1 unit when inventory is zero
    items = [(item_id, 1, 100.0, 50.0)]
    sale_id = models.create_sale("Customer", items)
    
    # Should fail
    assert sale_id is None, "Sale should be rejected when inventory is zero"
    
    # Verify inventory still zero
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
    qty = c.fetchone()[0]
    conn.close()
    
    assert qty == 0, "Inventory should remain zero after rejected sale"


@pytest.mark.unit
def test_create_sale_validates_empty_customer_name(test_db):
    """Test that empty customer names are rejected"""
    # Add inventory item
    models.add_inventory_item("SALE-005", "Item", 10, 50.0, 100.0, "Test", "")
    
    # Get item ID
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-005",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Try to create sale with empty customer name
    items = [(item_id, 1, 100.0, 50.0)]
    sale_id = models.create_sale("", items)
    
    # Should fail
    assert sale_id is None


@pytest.mark.unit
def test_create_sale_validates_empty_items_list(test_db):
    """Test that empty items list is rejected"""
    sale_id = models.create_sale("Customer", [])
    assert sale_id is None


@pytest.mark.unit
def test_create_sale_validates_negative_quantity(test_db):
    """Test that negative quantities are rejected"""
    # Add inventory item
    models.add_inventory_item("SALE-006", "Item", 10, 50.0, 100.0, "Test", "")
    
    # Get item ID
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-006",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Try to create sale with negative quantity
    items = [(item_id, -5, 100.0, 50.0)]
    sale_id = models.create_sale("Customer", items)
    
    # Should fail
    assert sale_id is None


@pytest.mark.unit
def test_create_sale_validates_negative_price(test_db):
    """Test that negative prices are rejected"""
    # Add inventory item
    models.add_inventory_item("SALE-007", "Item", 10, 50.0, 100.0, "Test", "")
    
    # Get item ID
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-007",))
    item_id = c.fetchone()[0]
    conn.close()
    
    # Try to create sale with negative price
    items = [(item_id, 1, -100.0, 50.0)]
    sale_id = models.create_sale("Customer", items)
    
    # Should fail
    assert sale_id is None


@pytest.mark.unit
def test_create_sale_with_nonexistent_item(test_db):
    """Test that sales with nonexistent items are rejected"""
    # Try to create sale with item ID that doesn't exist
    items = [(99999, 1, 100.0, 50.0)]
    sale_id = models.create_sale("Customer", items)
    
    # Should fail
    assert sale_id is None


@pytest.mark.unit
def test_get_sales_history(test_db):
    """Test retrieving sales history"""
    # Add inventory and create a sale
    models.add_inventory_item("SALE-008", "Item", 10, 50.0, 100.0, "Test", "")
    
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-008",))
    item_id = c.fetchone()[0]
    conn.close()
    
    items = [(item_id, 1, 100.0, 50.0)]
    sale_id = models.create_sale("Customer", items)
    
    # Get sales history
    history = models.get_sales_history()
    
    assert len(history) >= 1
    assert any(row[0] == sale_id for row in history)


@pytest.mark.unit
def test_get_sale_details(test_db):
    """Test retrieving sale details"""
    # Add inventory and create a sale
    models.add_inventory_item("SALE-009", "Item", 10, 50.0, 100.0, "Test", "")
    
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id FROM inventory WHERE sku = ?", ("SALE-009",))
    item_id = c.fetchone()[0]
    conn.close()
    
    items = [(item_id, 2, 100.0, 50.0)]
    sale_id = models.create_sale("Test Customer", items)
    
    # Get sale details
    sale_info, sale_items = models.get_sale_details(sale_id)
    
    assert sale_info is not None
    assert sale_info[2] == "Test Customer"  # customer_name
    assert sale_info[3] == 200.0  # total_amount (2 * 100)
    
    assert len(sale_items) == 1
    assert sale_items[0][3] == 2  # quantity
    assert sale_items[0][4] == 100.0  # unit_price
