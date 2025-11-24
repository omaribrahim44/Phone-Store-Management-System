# tests/test_financial.py
"""Property-based and unit tests for financial calculations"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
import tests.generators as gen
from modules.financial import (
    calculate_sale_total,
    calculate_repair_total,
    calculate_profit,
    calculate_tax,
    apply_discount,
    calculate_total_with_tax,
    calculate_total_with_discount_and_tax,
    calculate_cost_from_items,
    calculate_margin
)


@pytest.mark.property
@given(revenue=gen.valid_price, cost=gen.valid_price)
def test_profit_calculation_correctness(revenue, cost):
    """
    **Feature: data-integrity-testing, Property 6: Profit calculation correctness**
    **Validates: Requirements 2.3**
    
    For any set of completed transactions, profit must equal total revenue minus total costs.
    """
    profit = calculate_profit(revenue, cost)
    expected = round(revenue - cost, 2)
    assert abs(profit - expected) < 0.01


@pytest.mark.property
@given(amount=gen.valid_price, tax_rate=st.floats(min_value=0, max_value=100, allow_nan=False))
def test_tax_calculation_correctness(amount, tax_rate):
    """
    **Feature: data-integrity-testing, Property 7: Tax calculation correctness**
    **Validates: Requirements 2.4**
    
    For any amount and configured tax rate, the calculated tax must equal amount × (tax_rate / 100).
    """
    tax = calculate_tax(amount, tax_rate)
    expected = round(amount * (tax_rate / 100.0), 2)
    assert abs(tax - expected) < 0.01


@pytest.mark.unit
def test_calculate_sale_total():
    """Test sale total calculation"""
    items = [
        (1, 2, 100.0, 50.0),  # 2 * 100 = 200
        (2, 3, 50.0, 25.0),   # 3 * 50 = 150
    ]
    total = calculate_sale_total(items)
    assert total == 350.0


@pytest.mark.unit
def test_calculate_repair_total():
    """Test repair total calculation"""
    parts = [
        ("Screen", 1, 200.0, 100.0),  # 1 * 200 = 200
        ("Battery", 2, 75.0, 40.0),   # 2 * 75 = 150
    ]
    total = calculate_repair_total(parts)
    assert total == 350.0


@pytest.mark.unit
def test_apply_discount_non_negative():
    """
    Test that discounts cannot create negative totals.
    Validates Requirements 2.5
    """
    # 100% discount should result in 0, not negative
    result = apply_discount(100.0, 100.0)
    assert result == 0.0
    
    # Even >100% discount should result in 0
    result = apply_discount(100.0, 150.0)
    assert result == 0.0


@pytest.mark.unit
def test_calculate_total_with_tax():
    """Test total calculation with tax"""
    total = calculate_total_with_tax(100.0, 14.0)
    assert total == 114.0  # 100 + (100 * 0.14)


@pytest.mark.unit
def test_calculate_total_with_discount_and_tax():
    """Test total with discount then tax"""
    # 100 - 10% = 90, then 90 + 14% tax = 102.60
    total = calculate_total_with_discount_and_tax(100.0, 10.0, 14.0)
    assert total == 102.60


@pytest.mark.unit
def test_calculate_cost_from_items():
    """Test cost calculation from items"""
    items = [
        (1, 2, 100.0, 50.0),  # cost: 2 * 50 = 100
        (2, 3, 75.0, 30.0),   # cost: 3 * 30 = 90
    ]
    cost = calculate_cost_from_items(items)
    assert cost == 190.0


@pytest.mark.unit
def test_calculate_margin():
    """Test profit margin calculation"""
    margin = calculate_margin(1000.0, 600.0)
    assert margin == 40.0  # (1000-600)/1000 * 100 = 40%


@pytest.mark.unit
def test_calculate_margin_zero_revenue():
    """Test margin calculation with zero revenue"""
    margin = calculate_margin(0.0, 100.0)
    assert margin == 0.0


@pytest.mark.unit
def test_calculate_sale_total_rejects_negative_quantity():
    """Test that negative quantities are rejected"""
    items = [(1, -5, 100.0, 50.0)]
    with pytest.raises(ValueError):
        calculate_sale_total(items)


@pytest.mark.unit
def test_calculate_sale_total_rejects_negative_price():
    """Test that negative prices are rejected"""
    items = [(1, 5, -100.0, 50.0)]
    with pytest.raises(ValueError):
        calculate_sale_total(items)


@pytest.mark.unit
def test_calculate_tax_rejects_invalid_rate():
    """Test that invalid tax rates are rejected"""
    with pytest.raises(ValueError):
        calculate_tax(100.0, -5.0)
    
    with pytest.raises(ValueError):
        calculate_tax(100.0, 150.0)


@pytest.mark.unit
def test_apply_discount_rejects_invalid_discount():
    """Test that invalid discount percentages are rejected"""
    with pytest.raises(ValueError):
        apply_discount(100.0, -10.0)
    
    with pytest.raises(ValueError):
        apply_discount(100.0, 150.0)
