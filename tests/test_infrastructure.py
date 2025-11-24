# tests/test_infrastructure.py
"""Test that the testing infrastructure is working correctly"""

import pytest
from hypothesis import given, strategies as st


def test_pytest_works():
    """Basic test to verify pytest is working"""
    assert True


def test_fixtures_work(test_db):
    """Test that database fixture is working"""
    assert test_db.exists()
    assert str(test_db).endswith('.db')


def test_db_connection(db_conn):
    """Test that database connection fixture works"""
    cursor = db_conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1


@pytest.mark.property
@given(x=st.integers())
def test_hypothesis_works(x):
    """Test that Hypothesis is working"""
    assert isinstance(x, int)


def test_sample_fixtures(sample_inventory_item, sample_repair_order, sample_user):
    """Test that sample data fixtures are working"""
    assert sample_inventory_item['sku'] == 'TEST-001'
    assert sample_repair_order['order_number'] == 'REP-001'
    assert sample_user['username'] == 'testuser'
