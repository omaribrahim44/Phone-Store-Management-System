# tests/conftest.py
"""Pytest fixtures and configuration for test suite"""

import pytest
import sqlite3
import os
import tempfile
import shutil
from pathlib import Path
from contextlib import contextmanager

# Test database path
TEST_DB_PATH = None


@pytest.fixture(scope="session")
def test_db_dir():
    """Create a temporary directory for test databases"""
    temp_dir = tempfile.mkdtemp(prefix="phone_mgmt_test_")
    yield temp_dir
    # Cleanup after all tests
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def test_db(test_db_dir, monkeypatch):
    """
    Create a fresh test database for each test function.
    This ensures test isolation.
    """
    # Create unique database for this test
    db_path = Path(test_db_dir) / f"test_{os.getpid()}_{id(test_db)}.db"
    
    # Patch the DB_PATH in modules.db to use test database
    import modules.db as db_module
    original_path = db_module.DB_PATH
    monkeypatch.setattr(db_module, "DB_PATH", db_path)
    
    # Initialize the test database with full schema
    conn = sqlite3.connect(str(db_path))
    c = conn.cursor()
    
    # Create all tables
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        full_name TEXT,
        role TEXT DEFAULT 'Cashier',
        created_at TEXT
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sku TEXT UNIQUE,
        name TEXT,
        category TEXT DEFAULT 'General',
        description TEXT,
        quantity INTEGER DEFAULT 0,
        buy_price REAL DEFAULT 0,
        sell_price REAL DEFAULT 0,
        barcode TEXT
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_date TEXT,
        customer_name TEXT,
        total_amount REAL
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS sale_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sale_id INTEGER,
        item_id INTEGER,
        quantity INTEGER,
        unit_price REAL,
        cost_price REAL DEFAULT 0,
        FOREIGN KEY(sale_id) REFERENCES sales(sale_id),
        FOREIGN KEY(item_id) REFERENCES inventory(item_id)
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS repair_orders (
        repair_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE,
        customer_name TEXT,
        customer_phone TEXT,
        device_model TEXT,
        imei TEXT,
        reported_problem TEXT,
        received_date TEXT,
        estimated_delivery TEXT,
        status TEXT DEFAULT 'Received',
        technician TEXT,
        total_estimate REAL DEFAULT 0,
        notes TEXT
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS repair_parts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repair_id INTEGER,
        item_id INTEGER,
        part_name TEXT,
        qty INTEGER DEFAULT 1,
        unit_price REAL DEFAULT 0,
        cost_price REAL DEFAULT 0,
        FOREIGN KEY(repair_id) REFERENCES repair_orders(repair_id),
        FOREIGN KEY(item_id) REFERENCES inventory(item_id)
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS repair_history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        repair_id INTEGER,
        action_date TEXT,
        action_by TEXT,
        status_from TEXT,
        status_to TEXT,
        comment TEXT,
        FOREIGN KEY(repair_id) REFERENCES repair_orders(repair_id)
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        user TEXT,
        action_type TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id INTEGER,
        old_value TEXT,
        new_value TEXT,
        description TEXT
    )""")
    
    c.execute("""
    CREATE TABLE IF NOT EXISTS scan_log (
        scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_date TEXT NOT NULL,
        barcode TEXT NOT NULL,
        scan_type TEXT,
        user TEXT,
        module TEXT
    )""")
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    # Cleanup: close any open connections and remove database
    try:
        if db_path.exists():
            db_path.unlink()
    except Exception as e:
        print(f"Warning: Could not cleanup test database: {e}")


@pytest.fixture
def db_conn(test_db):
    """Provide a database connection for tests"""
    conn = sqlite3.connect(str(test_db))
    yield conn
    conn.close()


@pytest.fixture
def sample_inventory_item():
    """Provide a sample inventory item for testing"""
    return {
        'sku': 'TEST-001',
        'name': 'Test Phone',
        'category': 'Phones',
        'description': 'Test phone for testing',
        'quantity': 10,
        'buy_price': 100.0,
        'sell_price': 150.0
    }


@pytest.fixture
def sample_repair_order():
    """Provide a sample repair order for testing"""
    return {
        'order_number': 'REP-001',
        'customer_name': 'Test Customer',
        'customer_phone': '1234567890',
        'device_model': 'iPhone 12',
        'imei': '123456789012345',
        'reported_problem': 'Screen broken',
        'estimated_delivery': '2024-12-31',
        'technician': 'Test Tech',
        'total_estimate': 200.0,
        'notes': 'Test repair'
    }


@pytest.fixture
def sample_user():
    """Provide a sample user for testing"""
    return {
        'username': 'testuser',
        'password': 'TestPass123!',
        'full_name': 'Test User',
        'role': 'Cashier'
    }


@contextmanager
def transaction_context(db_path):
    """Context manager for database transactions in tests"""
    conn = sqlite3.connect(str(db_path))
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# Hypothesis settings for property-based tests
from hypothesis import settings, Verbosity

# Register custom profile for property tests
settings.register_profile("default", max_examples=100, verbosity=Verbosity.normal)
settings.register_profile("ci", max_examples=200, verbosity=Verbosity.verbose)
settings.register_profile("dev", max_examples=50, verbosity=Verbosity.normal)
settings.register_profile("debug", max_examples=10, verbosity=Verbosity.verbose)

# Load profile from environment or use default
settings.load_profile(os.getenv("HYPOTHESIS_PROFILE", "default"))
