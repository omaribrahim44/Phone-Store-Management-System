# tests/test_transactions.py
"""Property-based and unit tests for transaction management"""

import pytest
import sqlite3
from hypothesis import given, assume
import tests.generators as gen
from modules.transaction_manager import (
    transaction,
    transactional,
    execute_in_transaction,
    rollback_on_error,
    TransactionContext,
    verify_transaction_state,
    get_transaction_isolation_level,
    set_transaction_isolation_level
)
from modules.db import get_conn


# ==================== Basic Transaction Tests ====================

@pytest.mark.unit
def test_transaction_context_manager_commits_on_success(test_db):
    """Test that transaction commits when no exception occurs"""
    with transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      ("TEST-001", "Test Item", 10, 100.0, 150.0))
    
    # Verify data was committed
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-001",))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 1


@pytest.mark.unit
def test_transaction_context_manager_rolls_back_on_error(test_db):
    """Test that transaction rolls back when exception occurs"""
    try:
        with transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                          ("TEST-002", "Test Item", 10, 100.0, 150.0))
            # Force an error
            raise ValueError("Intentional error")
    except ValueError:
        pass  # Expected
    
    # Verify data was NOT committed
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-002",))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 0


@pytest.mark.property
def test_transaction_rollback_completeness(test_db):
    """
    **Feature: data-integrity-testing, Property 10: Transaction rollback completeness**
    **Validates: Requirements 3.4**
    
    For any database transaction that raises an exception, all changes within
    that transaction must be rolled back.
    """
    @given(item=gen.inventory_item())
    def check_rollback(item):
        # Clean database
        conn = get_conn()
        conn.execute("DELETE FROM inventory")
        conn.commit()
        conn.close()
        
        # Try to insert item but force error
        try:
            with transaction() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO inventory (sku, name, category, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?, ?)",
                    (item['sku'], item['name'], item['category'], item['quantity'], item['buy_price'], item['sell_price'])
                )
                # Force error after insert
                raise RuntimeError("Forced rollback")
        except RuntimeError:
            pass
        
        # Verify nothing was committed
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 0, f"Transaction not rolled back properly for SKU {item['sku']}"
    
    check_rollback()


# ==================== Decorator Tests ====================

@pytest.mark.unit
def test_transactional_decorator_commits_on_success(test_db):
    """Test that @transactional decorator commits on success"""
    @transactional
    def insert_item(conn, sku, name):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      (sku, name, 5, 50.0, 75.0))
        return True
    
    result = insert_item("TEST-003", "Decorated Item")
    assert result is True
    
    # Verify committed
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM inventory WHERE sku = ?", ("TEST-003",))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[0] == "Decorated Item"


@pytest.mark.unit
def test_transactional_decorator_rolls_back_on_error(test_db):
    """Test that @transactional decorator rolls back on error"""
    @transactional
    def insert_and_fail(conn, sku):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      (sku, "Will Fail", 5, 50.0, 75.0))
        raise ValueError("Intentional failure")
    
    try:
        insert_and_fail("TEST-004")
    except ValueError:
        pass
    
    # Verify rolled back
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-004",))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 0


# ==================== Execute in Transaction Tests ====================

@pytest.mark.unit
def test_execute_in_transaction_commits_on_success(test_db):
    """Test that execute_in_transaction commits on success"""
    def insert_item(conn, sku, name):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      (sku, name, 3, 30.0, 45.0))
        return sku
    
    result = execute_in_transaction(insert_item, "TEST-005", "Executed Item")
    assert result == "TEST-005"
    
    # Verify committed
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-005",))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 1


@pytest.mark.unit
def test_execute_in_transaction_rolls_back_on_error(test_db):
    """Test that execute_in_transaction rolls back on error"""
    def insert_and_fail(conn, sku):
        cursor = conn.cursor()
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      (sku, "Will Fail", 3, 30.0, 45.0))
        raise RuntimeError("Intentional error")
    
    try:
        execute_in_transaction(insert_and_fail, "TEST-006")
    except RuntimeError:
        pass
    
    # Verify rolled back
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-006",))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 0


# ==================== Rollback on Error Tests ====================

@pytest.mark.unit
def test_rollback_on_error_context_manager(test_db):
    """Test rollback_on_error context manager"""
    conn = get_conn()
    try:
        with rollback_on_error(conn):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                          ("TEST-007", "Test", 1, 10.0, 15.0))
            raise ValueError("Force rollback")
    except ValueError:
        pass
    finally:
        conn.close()
    
    # Verify rolled back
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-007",))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 0


# ==================== TransactionContext Tests ====================

@pytest.mark.unit
def test_transaction_context_class_commits(test_db):
    """Test TransactionContext class commits on success"""
    with TransactionContext() as tx:
        cursor = tx.cursor()
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      ("TEST-008", "Context Test", 2, 20.0, 30.0))
    
    # Verify committed
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-008",))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 1


@pytest.mark.unit
def test_transaction_context_class_rolls_back(test_db):
    """Test TransactionContext class rolls back on error"""
    try:
        with TransactionContext() as tx:
            cursor = tx.cursor()
            cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                          ("TEST-009", "Context Test", 2, 20.0, 30.0))
            raise ValueError("Force rollback")
    except ValueError:
        pass
    
    # Verify rolled back
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-009",))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 0


@pytest.mark.unit
def test_transaction_context_savepoints(test_db):
    """Test TransactionContext savepoint functionality"""
    with TransactionContext() as tx:
        cursor = tx.cursor()
        
        # Insert first item
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      ("TEST-010", "Item 1", 1, 10.0, 15.0))
        
        # Create savepoint
        sp = tx.savepoint("test_sp")
        
        # Insert second item
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      ("TEST-011", "Item 2", 1, 10.0, 15.0))
        
        # Rollback to savepoint (removes second item)
        tx.rollback_to_savepoint(sp)
    
    # Verify only first item exists
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku IN (?, ?)", ("TEST-010", "TEST-011"))
    count = cursor.fetchone()[0]
    conn.close()
    
    assert count == 1  # Only TEST-010 should exist


# ==================== Helper Function Tests ====================

@pytest.mark.unit
def test_verify_transaction_state(test_db):
    """Test verify_transaction_state helper"""
    with transaction() as conn:
        # Should be in transaction
        in_transaction = verify_transaction_state(conn)
        assert isinstance(in_transaction, bool)


@pytest.mark.unit
def test_get_transaction_isolation_level(test_db):
    """Test get_transaction_isolation_level helper"""
    conn = get_conn()
    level = get_transaction_isolation_level(conn)
    conn.close()
    
    assert level in ['DEFERRED', 'IMMEDIATE', 'EXCLUSIVE', None]


@pytest.mark.unit
def test_set_transaction_isolation_level(test_db):
    """Test set_transaction_isolation_level helper"""
    conn = get_conn()
    
    set_transaction_isolation_level(conn, 'IMMEDIATE')
    level = get_transaction_isolation_level(conn)
    
    conn.close()
    
    assert level == 'IMMEDIATE'


@pytest.mark.unit
def test_set_invalid_isolation_level_raises_error(test_db):
    """Test that invalid isolation level raises ValueError"""
    conn = get_conn()
    
    with pytest.raises(ValueError):
        set_transaction_isolation_level(conn, 'INVALID')
    
    conn.close()


# ==================== Multi-Operation Transaction Tests ====================

@pytest.mark.unit
def test_transaction_with_multiple_operations(test_db):
    """Test transaction with multiple related operations"""
    with transaction() as conn:
        cursor = conn.cursor()
        
        # Insert inventory item
        cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                      ("TEST-012", "Multi-Op Item", 10, 100.0, 150.0))
        
        # Get the item_id
        cursor.execute("SELECT item_id FROM inventory WHERE sku = ?", ("TEST-012",))
        item_id = cursor.fetchone()[0]
        
        # Create a sale
        cursor.execute("INSERT INTO sales (sale_date, customer_name, total_amount) VALUES (?, ?, ?)",
                      ("2024-01-01", "Test Customer", 150.0))
        sale_id = cursor.lastrowid
        
        # Add sale item
        cursor.execute("INSERT INTO sale_items (sale_id, item_id, quantity, unit_price, cost_price) VALUES (?, ?, ?, ?, ?)",
                      (sale_id, item_id, 1, 150.0, 100.0))
        
        # Update inventory
        cursor.execute("UPDATE inventory SET quantity = quantity - 1 WHERE item_id = ?", (item_id,))
    
    # Verify all operations committed
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT quantity FROM inventory WHERE sku = ?", ("TEST-012",))
    qty = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sales")
    sale_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sale_items")
    item_count = cursor.fetchone()[0]
    
    conn.close()
    
    assert qty == 9  # 10 - 1
    assert sale_count >= 1
    assert item_count >= 1


@pytest.mark.unit
def test_transaction_rolls_back_all_operations_on_error(test_db):
    """Test that all operations in a transaction are rolled back on error"""
    try:
        with transaction() as conn:
            cursor = conn.cursor()
            
            # Insert inventory item
            cursor.execute("INSERT INTO inventory (sku, name, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?)",
                          ("TEST-013", "Rollback Item", 10, 100.0, 150.0))
            
            # Create a sale
            cursor.execute("INSERT INTO sales (sale_date, customer_name, total_amount) VALUES (?, ?, ?)",
                          ("2024-01-01", "Test Customer", 150.0))
            
            # Force error
            raise RuntimeError("Force rollback of all operations")
    except RuntimeError:
        pass
    
    # Verify nothing was committed
    conn = get_conn()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM inventory WHERE sku = ?", ("TEST-013",))
    inv_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM sales WHERE customer_name = ?", ("Test Customer",))
    sale_count = cursor.fetchone()[0]
    
    conn.close()
    
    assert inv_count == 0
    assert sale_count == 0
