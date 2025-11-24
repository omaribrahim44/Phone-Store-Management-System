# tests/test_repairs.py
"""Property-based and unit tests for repair operations"""

import pytest
from hypothesis import given
import tests.generators as gen
from modules import models
from modules.db import get_conn


@pytest.mark.property
def test_repair_total_equals_parts_sum(test_db):
    """
    **Feature: data-integrity-testing, Property 5: Repair total equals parts sum**
    **Validates: Requirements 2.2**
    
    For any repair order with any parts, the total_estimate must equal the sum of
    (qty × unit_price) for all parts.
    """
    from hypothesis import settings, HealthCheck
    
    @given(repair=gen.repair_with_parts(min_parts=1, max_parts=3))
    @settings(suppress_health_check=[HealthCheck.too_slow])
    def check_total(repair):
        # Clean database
        conn = get_conn()
        conn.execute("DELETE FROM repair_orders")
        conn.execute("DELETE FROM repair_parts")
        conn.execute("DELETE FROM repair_history")
        conn.commit()
        conn.close()
        
        order = repair['order']
        parts = repair['parts']
        
        # Create repair order
        try:
            repair_id = models.create_repair_order(
                order_number=order['order_number'],
                customer_name=order['customer_name'],
                phone=order['customer_phone'],
                model=order['device_model'],
                imei=order['imei'],
                problem=order['reported_problem'],
                est_date=order['estimated_delivery'],
                tech=order['technician'],
                note=order['notes'],
                total_est=0.0  # Will be recalculated
            )
        except Exception:
            # Skip if validation fails
            return
        
        # Add parts
        for part in parts:
            models.add_repair_part(
                repair_id=repair_id,
                part_name=part['part_name'],
                qty=part['qty'],
                unit_price=part['unit_price'],
                cost_price=part['cost_price']
            )
        
        # Get repair details
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT total_estimate FROM repair_orders WHERE repair_id = ?", (repair_id,))
        stored_total = c.fetchone()[0]
        conn.close()
        
        # Calculate expected total
        expected_total = sum(p['qty'] * p['unit_price'] for p in parts)
        
        assert abs(stored_total - expected_total) < 0.01, f"Total mismatch: expected {expected_total}, got {stored_total}"
    
    check_total()


@pytest.mark.property
def test_repair_order_atomicity(test_db):
    """
    **Feature: data-integrity-testing, Property 9: Repair order atomicity**
    **Validates: Requirements 3.2**
    
    For any repair order creation that encounters an error, either all related records
    (repair_order, repair_parts, repair_history) exist or none exist.
    """
    @given(order=gen.repair_order())
    def check_atomicity(order):
        # Clean database
        conn = get_conn()
        conn.execute("DELETE FROM repair_orders")
        conn.execute("DELETE FROM repair_history")
        conn.commit()
        conn.close()
        
        # Try to create repair with invalid phone (empty)
        try:
            models.create_repair_order(
                order_number=order['order_number'],
                customer_name=order['customer_name'],
                phone="",  # Invalid - will fail validation
                model=order['device_model'],
                imei=order['imei'],
                problem=order['reported_problem'],
                est_date=order['estimated_delivery'],
                tech=order['technician'],
                note=order['notes'],
                total_est=order['total_estimate']
            )
        except ValueError:
            pass  # Expected
        
        # Verify NO records exist
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM repair_orders")
        order_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM repair_history")
        history_count = c.fetchone()[0]
        conn.close()
        
        assert order_count == 0, "No repair orders should exist after failed transaction"
        assert history_count == 0, "No history should exist after failed transaction"
    
    check_atomicity()


@pytest.mark.unit
def test_create_repair_order_with_valid_data(test_db):
    """Test creating a repair order with valid data"""
    repair_id = models.create_repair_order(
        order_number="REP-001",
        customer_name="John Doe",
        phone="1234567890",
        model="iPhone 12",
        imei="123456789012345",
        problem="Screen broken",
        est_date="2024-12-31",
        tech="Tech Mike",
        note="Handle with care",
        total_est=200.0
    )
    
    assert repair_id is not None
    
    # Verify repair was created
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT customer_name, device_model, status FROM repair_orders WHERE repair_id = ?", (repair_id,))
    row = c.fetchone()
    conn.close()
    
    assert row[0] == "John Doe"
    assert row[1] == "iPhone 12"
    assert row[2] == "Received"


@pytest.mark.unit
def test_create_repair_order_creates_history(test_db):
    """Test that creating a repair order creates initial history entry"""
    repair_id = models.create_repair_order(
        order_number="REP-002",
        customer_name="Jane Smith",
        phone="9876543210",
        model="Samsung S21",
        imei="987654321098765",
        problem="Battery issue",
        est_date="2024-12-31",
        tech="Tech Sarah",
        note="",
        total_est=150.0
    )
    
    # Verify history entry exists
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM repair_history WHERE repair_id = ?", (repair_id,))
    count = c.fetchone()[0]
    conn.close()
    
    assert count >= 1


@pytest.mark.unit
def test_add_repair_part_recalculates_total(test_db):
    """Test that adding parts recalculates the repair total"""
    # Create repair
    repair_id = models.create_repair_order(
        order_number="REP-003",
        customer_name="Bob Johnson",
        phone="5551234567",
        model="Pixel 6",
        imei="555123456789012",
        problem="Camera not working",
        est_date="2024-12-31",
        tech="Tech Alex",
        note="",
        total_est=0.0
    )
    
    # Add parts
    models.add_repair_part(repair_id, "Screen", 1, 100.0, 50.0)
    models.add_repair_part(repair_id, "Battery", 1, 75.0, 40.0)
    
    # Verify total was recalculated
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT total_estimate FROM repair_orders WHERE repair_id = ?", (repair_id,))
    total = c.fetchone()[0]
    conn.close()
    
    assert total == 175.0  # 100 + 75


@pytest.mark.unit
def test_update_repair_status_creates_history(test_db):
    """Test that updating status creates history entry"""
    # Create repair
    repair_id = models.create_repair_order(
        order_number="REP-004",
        customer_name="Alice Brown",
        phone="5559876543",
        model="OnePlus 9",
        imei="555987654321098",
        problem="Software issue",
        est_date="2024-12-31",
        tech="Tech Chris",
        note="",
        total_est=50.0
    )
    
    # Update status
    result = models.update_repair_status(repair_id, "In Progress", "Tech Chris", "Started work")
    assert result is True
    
    # Verify history entry
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM repair_history WHERE repair_id = ? AND status_to = ?", (repair_id, "In Progress"))
    count = c.fetchone()[0]
    conn.close()
    
    assert count >= 1


@pytest.mark.unit
def test_create_repair_validates_empty_customer_name(test_db):
    """Test that empty customer names are rejected"""
    try:
        models.create_repair_order(
            order_number="REP-005",
            customer_name="",  # Invalid
            phone="1234567890",
            model="iPhone 12",
            imei="123456789012345",
            problem="Screen broken",
            est_date="2024-12-31",
            tech="Tech Mike",
            note="",
            total_est=200.0
        )
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


@pytest.mark.unit
def test_create_repair_validates_phone_number(test_db):
    """Test that invalid phone numbers are rejected"""
    try:
        models.create_repair_order(
            order_number="REP-006",
            customer_name="John Doe",
            phone="123",  # Too short
            model="iPhone 12",
            imei="123456789012345",
            problem="Screen broken",
            est_date="2024-12-31",
            tech="Tech Mike",
            note="",
            total_est=200.0
        )
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


@pytest.mark.unit
def test_add_repair_part_validates_negative_quantity(test_db):
    """Test that negative quantities are rejected"""
    # Create repair
    repair_id = models.create_repair_order(
        order_number="REP-007",
        customer_name="Test User",
        phone="1234567890",
        model="Test Phone",
        imei="123456789012345",
        problem="Test",
        est_date="2024-12-31",
        tech="Tech Test",
        note="",
        total_est=0.0
    )
    
    # Try to add part with negative quantity
    result = models.add_repair_part(repair_id, "Part", -5, 100.0, 50.0)
    assert result is False


@pytest.mark.unit
def test_add_repair_part_validates_negative_price(test_db):
    """Test that negative prices are rejected"""
    # Create repair
    repair_id = models.create_repair_order(
        order_number="REP-008",
        customer_name="Test User",
        phone="1234567890",
        model="Test Phone",
        imei="123456789012345",
        problem="Test",
        est_date="2024-12-31",
        tech="Tech Test",
        note="",
        total_est=0.0
    )
    
    # Try to add part with negative price
    result = models.add_repair_part(repair_id, "Part", 1, -100.0, 50.0)
    assert result is False


@pytest.mark.unit
def test_get_repair_parts_total(test_db):
    """Test calculating repair parts total"""
    # Create repair
    repair_id = models.create_repair_order(
        order_number="REP-009",
        customer_name="Test User",
        phone="1234567890",
        model="Test Phone",
        imei="123456789012345",
        problem="Test",
        est_date="2024-12-31",
        tech="Tech Test",
        note="",
        total_est=0.0
    )
    
    # Add parts
    models.add_repair_part(repair_id, "Part 1", 2, 50.0, 25.0)
    models.add_repair_part(repair_id, "Part 2", 1, 100.0, 60.0)
    
    # Get total
    total = models.get_repair_parts_total(repair_id)
    
    assert total == 200.0  # (2*50) + (1*100)
