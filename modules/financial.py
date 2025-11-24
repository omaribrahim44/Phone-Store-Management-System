# modules/financial.py
"""
Financial calculation utilities for the Phone Management System.

This module provides centralized, validated financial calculations for
sales, repairs, taxes, discounts, and profit calculations.
"""

from typing import List, Tuple
from modules.validators import validate_price, validate_quantity


def calculate_sale_total(items: List[Tuple[int, int, float, float]]) -> float:
    """
    Calculate total for a sale from items.
    
    Args:
        items: List of tuples (item_id, quantity, unit_price, cost_price)
    
    Returns:
        Total amount
    
    Raises:
        ValueError: If validation fails
    """
    if not items:
        raise ValueError("Items list cannot be empty")
    
    total = 0.0
    for item_id, qty, unit_price, cost_price in items:
        # Validate
        qty_result = validate_quantity(qty)
        if not qty_result.valid:
            raise ValueError(f"Invalid quantity for item {item_id}: {qty_result.error_message}")
        
        price_result = validate_price(unit_price)
        if not price_result.valid:
            raise ValueError(f"Invalid price for item {item_id}: {price_result.error_message}")
        
        # Calculate
        total += qty_result.normalized_value * price_result.normalized_value
    
    return round(total, 2)


def calculate_repair_total(parts: List[Tuple[str, int, float, float]]) -> float:
    """
    Calculate total for a repair from parts.
    
    Args:
        parts: List of tuples (part_name, qty, unit_price, cost_price)
    
    Returns:
        Total amount
    
    Raises:
        ValueError: If validation fails
    """
    if not parts:
        return 0.0
    
    total = 0.0
    for part_name, qty, unit_price, cost_price in parts:
        # Validate
        qty_result = validate_quantity(qty)
        if not qty_result.valid:
            raise ValueError(f"Invalid quantity for part {part_name}: {qty_result.error_message}")
        
        price_result = validate_price(unit_price)
        if not price_result.valid:
            raise ValueError(f"Invalid price for part {part_name}: {price_result.error_message}")
        
        # Calculate
        total += qty_result.normalized_value * price_result.normalized_value
    
    return round(total, 2)


def calculate_profit(revenue: float, cost: float) -> float:
    """
    Calculate profit as revenue minus cost.
    
    Args:
        revenue: Total revenue
        cost: Total cost
    
    Returns:
        Profit amount
    
    Raises:
        ValueError: If validation fails
    """
    # Validate
    rev_result = validate_price(revenue)
    if not rev_result.valid:
        raise ValueError(f"Invalid revenue: {rev_result.error_message}")
    
    cost_result = validate_price(cost)
    if not cost_result.valid:
        raise ValueError(f"Invalid cost: {cost_result.error_message}")
    
    # Calculate
    profit = rev_result.normalized_value - cost_result.normalized_value
    return round(profit, 2)


def calculate_tax(amount: float, tax_rate: float) -> float:
    """
    Calculate tax amount.
    
    Args:
        amount: Base amount
        tax_rate: Tax rate as percentage (e.g., 14.0 for 14%)
    
    Returns:
        Tax amount
    
    Raises:
        ValueError: If validation fails
    """
    # Validate amount
    amount_result = validate_price(amount)
    if not amount_result.valid:
        raise ValueError(f"Invalid amount: {amount_result.error_message}")
    
    # Validate tax rate (0-100%)
    if tax_rate < 0 or tax_rate > 100:
        raise ValueError(f"Tax rate must be between 0 and 100, got {tax_rate}")
    
    # Calculate
    tax = amount_result.normalized_value * (tax_rate / 100.0)
    return round(tax, 2)


def apply_discount(amount: float, discount_percent: float) -> float:
    """
    Apply discount to an amount.
    
    Args:
        amount: Original amount
        discount_percent: Discount percentage (e.g., 10.0 for 10% off)
    
    Returns:
        Final amount after discount (non-negative)
    
    Raises:
        ValueError: If validation fails
    """
    # Validate amount
    amount_result = validate_price(amount)
    if not amount_result.valid:
        raise ValueError(f"Invalid amount: {amount_result.error_message}")
    
    # Validate discount (0-100%)
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError(f"Discount must be between 0 and 100, got {discount_percent}")
    
    # Calculate
    discount_amount = amount_result.normalized_value * (discount_percent / 100.0)
    final_amount = amount_result.normalized_value - discount_amount
    
    # Ensure non-negative
    if final_amount < 0:
        final_amount = 0.0
    
    return round(final_amount, 2)


def calculate_total_with_tax(amount: float, tax_rate: float) -> float:
    """
    Calculate total including tax.
    
    Args:
        amount: Base amount
        tax_rate: Tax rate as percentage
    
    Returns:
        Total amount including tax
    """
    tax = calculate_tax(amount, tax_rate)
    return round(amount + tax, 2)


def calculate_total_with_discount_and_tax(amount: float, discount_percent: float, tax_rate: float) -> float:
    """
    Calculate total with discount applied first, then tax.
    
    Args:
        amount: Original amount
        discount_percent: Discount percentage
        tax_rate: Tax rate as percentage
    
    Returns:
        Final total
    """
    # Apply discount first
    discounted = apply_discount(amount, discount_percent)
    
    # Then apply tax
    total = calculate_total_with_tax(discounted, tax_rate)
    
    return round(total, 2)


def calculate_cost_from_items(items: List[Tuple[int, int, float, float]]) -> float:
    """
    Calculate total cost from sale items.
    
    Args:
        items: List of tuples (item_id, quantity, unit_price, cost_price)
    
    Returns:
        Total cost
    """
    if not items:
        return 0.0
    
    total_cost = 0.0
    for item_id, qty, unit_price, cost_price in items:
        # Validate
        qty_result = validate_quantity(qty)
        if not qty_result.valid:
            raise ValueError(f"Invalid quantity for item {item_id}: {qty_result.error_message}")
        
        cost_result = validate_price(cost_price)
        if not cost_result.valid:
            raise ValueError(f"Invalid cost for item {item_id}: {cost_result.error_message}")
        
        # Calculate
        total_cost += qty_result.normalized_value * cost_result.normalized_value
    
    return round(total_cost, 2)


def calculate_margin(revenue: float, cost: float) -> float:
    """
    Calculate profit margin as percentage.
    
    Args:
        revenue: Total revenue
        cost: Total cost
    
    Returns:
        Profit margin as percentage
    """
    if revenue == 0:
        return 0.0
    
    profit = calculate_profit(revenue, cost)
    margin = (profit / revenue) * 100.0
    
    return round(margin, 2)
