# -*- coding: utf-8 -*-
# modules/financial.py
"""
Financial calculation utilities for the Phone Management System.

This module provides validated financial calculations for sales, repairs,
taxes, discounts, and profit/loss analysis.
"""

from typing import List, Tuple
from modules.validators import validate_price, validate_quantity


def calculate_sale_total(items: List[Tuple[int, float, float]]) -> float:
    """
    Calculate total for a sale from list of items.
    
    Args:
        items: List of tuples (quantity, unit_price, cost_price)
    
    Returns:
        Total amount (sum of quantity * unit_price)
    
    Raises:
        ValueError: If validation fails
    """
    total = 0.0
    
    for qty, unit_price, cost_price in items:
        # Validate inputs
        qty_result = validate_quantity(qty)
        if not qty_result.valid:
            raise ValueError(f"Invalid quantity: {qty_result.error_message}")
        
        price_result = validate_price(unit_price)
        if not price_result.valid:
            raise ValueError(f"Invalid unit price: {price_result.error_message}")
        
        # Use validated values
        qty = qty_result.normalized_value
        unit_price = price_result.normalized_value
        
        total += qty * unit_price
    
    return round(total, 2)


def calculate_repair_total(parts: List[Tuple[int, float]]) -> float:
    """
    Calculate total for a repair from list of parts.
    
    Args:
        parts: List of tuples (quantity, unit_price)
    
    Returns:
        Total amount (sum of quantity * unit_price)
    
    Raises:
        ValueError: If validation fails
    """
    total = 0.0
    
    for qty, unit_price in parts:
        # Validate inputs
        qty_result = validate_quantity(qty)
        if not qty_result.valid:
            raise ValueError(f"Invalid quantity: {qty_result.error_message}")
        
        price_result = validate_price(unit_price)
        if not price_result.valid:
            raise ValueError(f"Invalid unit price: {price_result.error_message}")
        
        # Use validated values
        qty = qty_result.normalized_value
        unit_price = price_result.normalized_value
        
        total += qty * unit_price
    
    return round(total, 2)


def calculate_profit(revenue: float, cost: float) -> float:
    """
    Calculate profit as revenue minus cost.
    
    Args:
        revenue: Total revenue
        cost: Total cost
    
    Returns:
        Profit amount (revenue - cost)
    
    Raises:
        ValueError: If validation fails
    """
    # Validate inputs
    revenue_result = validate_price(revenue)
    if not revenue_result.valid:
        raise ValueError(f"Invalid revenue: {revenue_result.error_message}")
    
    cost_result = validate_price(cost)
    if not cost_result.valid:
        raise ValueError(f"Invalid cost: {cost_result.error_message}")
    
    # Use validated values
    revenue = revenue_result.normalized_value
    cost = cost_result.normalized_value
    
    profit = revenue - cost
    return round(profit, 2)


def calculate_tax(amount: float, tax_rate: float) -> float:
    """
    Calculate tax amount using configured tax rate.
    
    Args:
        amount: Amount to calculate tax on
        tax_rate: Tax rate as percentage (e.g., 15 for 15%)
    
    Returns:
        Tax amount (amount * tax_rate / 100)
    
    Raises:
        ValueError: If validation fails
    """
    # Validate amount
    amount_result = validate_price(amount)
    if not amount_result.valid:
        raise ValueError(f"Invalid amount: {amount_result.error_message}")
    
    # Validate tax rate (0-100%)
    if not isinstance(tax_rate, (int, float)):
        raise ValueError(f"Invalid tax rate format: {tax_rate}")
    
    if tax_rate < 0 or tax_rate > 100:
        raise ValueError(f"Tax rate must be between 0 and 100: {tax_rate}")
    
    # Use validated values
    amount = amount_result.normalized_value
    
    tax = amount * (tax_rate / 100.0)
    return round(tax, 2)


def apply_discount(amount: float, discount_percent: float) -> float:
    """
    Apply discount to amount and ensure result is non-negative.
    
    Args:
        amount: Original amount
        discount_percent: Discount as percentage (e.g., 10 for 10%)
    
    Returns:
        Final amount after discount (never negative)
    
    Raises:
        ValueError: If validation fails
    """
    # Validate amount
    amount_result = validate_price(amount)
    if not amount_result.valid:
        raise ValueError(f"Invalid amount: {amount_result.error_message}")
    
    # Validate discount (0-100%)
    if not isinstance(discount_percent, (int, float)):
        raise ValueError(f"Invalid discount format: {discount_percent}")
    
    if discount_percent < 0 or discount_percent > 100:
        raise ValueError(f"Discount must be between 0 and 100: {discount_percent}")
    
    # Use validated values
    amount = amount_result.normalized_value
    
    # Calculate discount
    discount_amount = amount * (discount_percent / 100.0)
    final_amount = amount - discount_amount
    
    # Ensure non-negative
    if final_amount < 0:
        final_amount = 0.0
    
    return round(final_amount, 2)


def calculate_sale_profit(items: List[Tuple[int, float, float]]) -> float:
    """
    Calculate profit for a sale (revenue - cost).
    
    Args:
        items: List of tuples (quantity, unit_price, cost_price)
    
    Returns:
        Total profit
    
    Raises:
        ValueError: If validation fails
    """
    total_revenue = 0.0
    total_cost = 0.0
    
    for qty, unit_price, cost_price in items:
        # Validate inputs
        qty_result = validate_quantity(qty)
        if not qty_result.valid:
            raise ValueError(f"Invalid quantity: {qty_result.error_message}")
        
        price_result = validate_price(unit_price)
        if not price_result.valid:
            raise ValueError(f"Invalid unit price: {price_result.error_message}")
        
        cost_result = validate_price(cost_price)
        if not cost_result.valid:
            raise ValueError(f"Invalid cost price: {cost_result.error_message}")
        
        # Use validated values
        qty = qty_result.normalized_value
        unit_price = price_result.normalized_value
        cost_price = cost_result.normalized_value
        
        total_revenue += qty * unit_price
        total_cost += qty * cost_price
    
    profit = total_revenue - total_cost
    return round(profit, 2)


def calculate_repair_profit(parts: List[Tuple[int, float, float]]) -> float:
    """
    Calculate profit for a repair (revenue - cost).
    
    Args:
        parts: List of tuples (quantity, unit_price, cost_price)
    
    Returns:
        Total profit
    
    Raises:
        ValueError: If validation fails
    """
    total_revenue = 0.0
    total_cost = 0.0
    
    for qty, unit_price, cost_price in parts:
        # Validate inputs
        qty_result = validate_quantity(qty)
        if not qty_result.valid:
            raise ValueError(f"Invalid quantity: {qty_result.error_message}")
        
        price_result = validate_price(unit_price)
        if not price_result.valid:
            raise ValueError(f"Invalid unit price: {price_result.error_message}")
        
        cost_result = validate_price(cost_price)
        if not cost_result.valid:
            raise ValueError(f"Invalid cost price: {cost_result.error_message}")
        
        # Use validated values
        qty = qty_result.normalized_value
        unit_price = price_result.normalized_value
        cost_price = cost_result.normalized_value
        
        total_revenue += qty * unit_price
        total_cost += qty * cost_price
    
    profit = total_revenue - total_cost
    return round(profit, 2)
