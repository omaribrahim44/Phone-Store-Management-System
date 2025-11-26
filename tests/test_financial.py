# tests/test_financial.py
"""Property-based and unit tests for financial calculations"""

import pytest
from hypothesis import given
from hypothesis import strategies as st
from modules import financial


# ==================== Sale Total Tests ====================

@pytest.mark.unit
def test_calculate_sale_total_single_item():
    """Test calculating total for a single item"""
    items = [(2, 100.0, 50.0)]  # 2 items at $100 each
    total = financial.calculate_sale_total(items)
    assert total == 200.0


@pytest.mark.unit
def test_calculate_sale_total_multiple_items():
    """Test calculating total for multiple items"""
    items = [
        (2, 100.0, 50.0),  # 2 * 100 = 200
        (3, 75.0, 40.0),   # 3 * 75 = 225
        (1, 50.0, 25.0)    # 1 * 50 = 50
    ]
    total = financial.calculate_sale_total(items)
    assert total == 475.0


@pytest.mark.unit
def test_calculate_sale_total_rejects_negative_quantity():
    """Test that negative quantities are rejected"""
    items = [(-1, 100.0, 50.0)]
    with pytest.raises(ValueError):
        financial.calculate_sale_total(items)


@pytest.mark.unit
def test_calculate_sale_total_rejects_negative_price():
    """Test that negative prices are rejected"""
    items = [(1, -100.0, 50.0)]
    with pytest.raises(ValueError):
        financial.calculate_sale_total(items)


# ==================== Repair Total Tests ====================

@pytest.mark.unit
def test_calculate_repair_total_single_part():
    """Test calculating total for a single part"""
    parts = [(1, 150.0)]
    total = financial.calculate_repair_total(parts)
    assert total == 150.0


@pytest.mark.unit
def test_calculate_repair_total_multiple_parts():
    """Test calculating total for multiple parts"""
    parts = [
        (1, 100.0),  # 1 * 100 = 100
        (2, 50.0),   # 2 * 50 = 100
        (1, 75.0)    # 1 * 75 = 75
    ]
    total = financial.calculate_repair_total(parts)
    assert total == 275.0


# ==================== Profit Calculation Tests ====================

@pytest.mark.property
@given(
    revenue=st.floats(min_value=0, max_value=100000, allow_nan=False, allow_infinity=False),
    cost=st.floats(min_value=0, max_value=100000, allow_nan=False, allow_infinity=False)
)
def test_profit_calculation_correctness(revenue, cost):
    """
    **Feature: data-integrity-testing, Property 6: Profit calculation correctness**
    **Validates: Requirements 2.3**
    
    For any set of completed transactions, profit must equal total revenue minus total costs.
    """
    profit = financial.calculate_profit(revenue, cost)
    expected = round(revenue - cost, 2)
    assert abs(profit - expected) < 0.02


@pytest.mark.unit
def test_calculate_profit_positive():
    """Test profit calculation with positive profit"""
    profit = financial.calculate_profit(1000.0, 600.0)
    assert profit == 400.0


@pytest.mark.unit
def test_calculate_profit_negative():
    """Test profit calculation with loss"""
    profit = financial.calculate_profit(500.0, 800.0)
    assert profit == -300.0


@pytest.mark.unit
def test_calculate_profit_zero():
    """Test profit calculation with break-even"""
    profit = financial.calculate_profit(500.0, 500.0)
    assert profit == 0.0


# ==================== Tax Calculation Tests ====================

@pytest.mark.property
@given(
    amount=st.floats(min_value=0.01, max_value=10000, allow_nan=False, allow_infinity=False),
    tax_rate=st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False)
)
def test_tax_calculation_correctness(amount, tax_rate):
    """
    **Feature: data-integrity-testing, Property 7: Tax calculation correctness**
    **Validates: Requirements 2.4**
    
    For any amount and configured tax rate, the calculated tax must equal amount × (tax_rate / 100).
    """
    tax = financial.calculate_tax(amount, tax_rate)
    expected = round(amount * (tax_rate / 100.0), 2)
    assert abs(tax - expected) < 0.02


@pytest.mark.unit
def test_calculate_tax_15_percent():
    """Test tax calculation with 15% rate"""
    tax = financial.calculate_tax(100.0, 15.0)
    assert tax == 15.0


@pytest.mark.unit
def test_calculate_tax_zero_rate():
    """Test tax calculation with 0% rate"""
    tax = financial.calculate_tax(100.0, 0.0)
    assert tax == 0.0


@pytest.mark.unit
def test_calculate_tax_rejects_negative_rate():
    """Test that negative tax rates are rejected"""
    with pytest.raises(ValueError):
        financial.calculate_tax(100.0, -5.0)


@pytest.mark.unit
def test_calculate_tax_rejects_rate_over_100():
    """Test that tax rates over 100% are rejected"""
    with pytest.raises(ValueError):
        financial.calculate_tax(100.0, 150.0)


# ==================== Discount Tests ====================

@pytest.mark.unit
def test_apply_discount_10_percent():
    """Test applying 10% discount"""
    final = financial.apply_discount(100.0, 10.0)
    assert final == 90.0


@pytest.mark.unit
def test_apply_discount_50_percent():
    """Test applying 50% discount"""
    final = financial.apply_discount(200.0, 50.0)
    assert final == 100.0


@pytest.mark.unit
def test_apply_discount_100_percent():
    """Test applying 100% discount"""
    final = financial.apply_discount(100.0, 100.0)
    assert final == 0.0


@pytest.mark.unit
def test_apply_discount_non_negative_enforcement():
    """
    Test that discounts cannot create negative totals.
    **Validates: Requirements 2.5**
    """
    # Even with 100% discount, result should be 0, not negative
    final = financial.apply_discount(100.0, 100.0)
    assert final >= 0.0


@pytest.mark.unit
def test_apply_discount_rejects_negative_discount():
    """Test that negative discounts are rejected"""
    with pytest.raises(ValueError):
        financial.apply_discount(100.0, -10.0)


@pytest.mark.unit
def test_apply_discount_rejects_discount_over_100():
    """Test that discounts over 100% are rejected"""
    with pytest.raises(ValueError):
        financial.apply_discount(100.0, 150.0)


# ==================== Sale Profit Tests ====================

@pytest.mark.unit
def test_calculate_sale_profit():
    """Test calculating profit for a sale"""
    items = [
        (2, 100.0, 60.0),  # Revenue: 200, Cost: 120, Profit: 80
        (1, 50.0, 30.0)    # Revenue: 50, Cost: 30, Profit: 20
    ]
    profit = financial.calculate_sale_profit(items)
    assert profit == 100.0  # 80 + 20


@pytest.mark.unit
def test_calculate_sale_profit_with_loss():
    """Test calculating profit when there's a loss"""
    items = [
        (1, 50.0, 80.0)  # Revenue: 50, Cost: 80, Loss: -30
    ]
    profit = financial.calculate_sale_profit(items)
    assert profit == -30.0


# ==================== Repair Profit Tests ====================

@pytest.mark.unit
def test_calculate_repair_profit():
    """Test calculating profit for a repair"""
    parts = [
        (1, 150.0, 80.0),  # Revenue: 150, Cost: 80, Profit: 70
        (2, 50.0, 25.0)    # Revenue: 100, Cost: 50, Profit: 50
    ]
    profit = financial.calculate_repair_profit(parts)
    assert profit == 120.0  # 70 + 50


# ==================== Edge Cases ====================

@pytest.mark.unit
def test_calculate_sale_total_empty_list():
    """Test calculating total with empty items list"""
    total = financial.calculate_sale_total([])
    assert total == 0.0


@pytest.mark.unit
def test_calculate_repair_total_empty_list():
    """Test calculating total with empty parts list"""
    total = financial.calculate_repair_total([])
    assert total == 0.0


@pytest.mark.unit
def test_rounding_precision():
    """Test that calculations maintain 2 decimal precision"""
    items = [(1, 10.999, 5.0)]
    total = financial.calculate_sale_total(items)
    # Should round to 2 decimals
    assert total == 11.0
