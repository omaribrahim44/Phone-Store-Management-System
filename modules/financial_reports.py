# -*- coding: utf-8 -*-
# modules/financial_reports.py
"""
Advanced financial reporting and analytics for the Phone Management System.

Provides profit/loss analysis, expense tracking, cash flow management,
and comprehensive financial dashboards.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from modules.db import get_conn


def get_profit_loss_report(start_date: str, end_date: str) -> Dict:
    """
    Generate comprehensive profit/loss report for date range.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        Dictionary with revenue, costs, profit breakdown
    """
    conn = get_conn()
    c = conn.cursor()
    
    report = {
        'period': {'start': start_date, 'end': end_date},
        'sales': {},
        'repairs': {},
        'summary': {}
    }
    
    # Sales Revenue and Profit
    c.execute("""
        SELECT 
            COUNT(*) as transaction_count,
            SUM(total_amount) as total_revenue,
            SUM(si.quantity * (si.unit_price - si.cost_price)) as total_profit
        FROM sales s
        LEFT JOIN sale_items si ON s.sale_id = si.sale_id
        WHERE DATE(s.sale_date) BETWEEN ? AND ?
    """, (start_date, end_date))
    
    sales_data = c.fetchone()
    report['sales'] = {
        'transaction_count': sales_data[0] or 0,
        'revenue': float(sales_data[1] or 0.0),
        'profit': float(sales_data[2] or 0.0)
    }
    
    # Repair Revenue and Profit
    c.execute("""
        SELECT 
            COUNT(*) as repair_count,
            SUM(total_estimate) as total_revenue,
            SUM(rp.qty * (rp.unit_price - rp.cost_price)) as total_profit
        FROM repair_orders ro
        LEFT JOIN repair_parts rp ON ro.repair_id = rp.repair_id
        WHERE DATE(ro.received_date) BETWEEN ? AND ?
        AND ro.status IN ('Completed', 'Delivered')
    """, (start_date, end_date))
    
    repair_data = c.fetchone()
    report['repairs'] = {
        'order_count': repair_data[0] or 0,
        'revenue': float(repair_data[1] or 0.0),
        'profit': float(repair_data[2] or 0.0)
    }
    
    # Summary
    total_revenue = report['sales']['revenue'] + report['repairs']['revenue']
    total_profit = report['sales']['profit'] + report['repairs']['profit']
    total_cost = total_revenue - total_profit
    
    report['summary'] = {
        'total_revenue': round(total_revenue, 2),
        'total_cost': round(total_cost, 2),
        'total_profit': round(total_profit, 2),
        'profit_margin': round((total_profit / total_revenue * 100) if total_revenue > 0 else 0, 2)
    }
    
    conn.close()
    return report


def get_daily_profit_loss(date: str = None) -> Dict:
    """Get profit/loss for a specific day (defaults to today)."""
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    return get_profit_loss_report(date, date)


def get_weekly_profit_loss() -> Dict:
    """Get profit/loss for current week."""
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    start_date = start_of_week.strftime('%Y-%m-%d')
    end_date = today.strftime('%Y-%m-%d')
    return get_profit_loss_report(start_date, end_date)


def get_monthly_profit_loss(year: int = None, month: int = None) -> Dict:
    """Get profit/loss for a specific month (defaults to current month)."""
    if year is None or month is None:
        today = datetime.now()
        year = today.year
        month = today.month
    
    start_date = f"{year}-{month:02d}-01"
    
    # Calculate last day of month
    if month == 12:
        next_month = f"{year + 1}-01-01"
    else:
        next_month = f"{year}-{month + 1:02d}-01"
    
    last_day = (datetime.strptime(next_month, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    
    return get_profit_loss_report(start_date, last_day)


def get_sales_trends(days: int = 30) -> List[Dict]:
    """
    Get sales trends for the last N days.
    
    Args:
        days: Number of days to analyze
    
    Returns:
        List of daily sales data
    """
    conn = get_conn()
    c = conn.cursor()
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    c.execute("""
        SELECT 
            DATE(sale_date) as date,
            COUNT(*) as transaction_count,
            SUM(total_amount) as revenue,
            SUM(si.quantity * (si.unit_price - si.cost_price)) as profit
        FROM sales s
        LEFT JOIN sale_items si ON s.sale_id = si.sale_id
        WHERE DATE(sale_date) >= ?
        GROUP BY DATE(sale_date)
        ORDER BY date
    """, (start_date.strftime('%Y-%m-%d'),))
    
    trends = []
    for row in c.fetchall():
        trends.append({
            'date': row[0],
            'transactions': row[1],
            'revenue': float(row[2] or 0.0),
            'profit': float(row[3] or 0.0)
        })
    
    conn.close()
    return trends


def get_top_selling_products(limit: int = 10, days: int = 30) -> List[Dict]:
    """
    Get top selling products by revenue.
    
    Args:
        limit: Number of products to return
        days: Number of days to analyze
    
    Returns:
        List of top products with sales data
    """
    conn = get_conn()
    c = conn.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    c.execute("""
        SELECT 
            i.name,
            i.sku,
            SUM(si.quantity) as units_sold,
            SUM(si.quantity * si.unit_price) as revenue,
            SUM(si.quantity * (si.unit_price - si.cost_price)) as profit
        FROM sale_items si
        JOIN inventory i ON si.item_id = i.item_id
        JOIN sales s ON si.sale_id = s.sale_id
        WHERE DATE(s.sale_date) >= ?
        GROUP BY si.item_id
        ORDER BY revenue DESC
        LIMIT ?
    """, (start_date, limit))
    
    products = []
    for row in c.fetchall():
        products.append({
            'name': row[0],
            'sku': row[1],
            'units_sold': row[2],
            'revenue': float(row[3]),
            'profit': float(row[4])
        })
    
    conn.close()
    return products


def get_top_customers(limit: int = 10, days: int = 30) -> List[Dict]:
    """
    Get top customers by total spending.
    
    Args:
        limit: Number of customers to return
        days: Number of days to analyze
    
    Returns:
        List of top customers with spending data
    """
    conn = get_conn()
    c = conn.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    c.execute("""
        SELECT 
            customer_name,
            COUNT(*) as transaction_count,
            SUM(total_amount) as total_spent
        FROM sales
        WHERE DATE(sale_date) >= ?
        GROUP BY customer_name
        ORDER BY total_spent DESC
        LIMIT ?
    """, (start_date, limit))
    
    customers = []
    for row in c.fetchall():
        customers.append({
            'name': row[0],
            'transactions': row[1],
            'total_spent': float(row[2])
        })
    
    conn.close()
    return customers


def get_inventory_valuation() -> Dict:
    """
    Calculate current inventory valuation.
    
    Returns:
        Dictionary with cost value, retail value, and potential profit
    """
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("""
        SELECT 
            SUM(quantity * buy_price) as cost_value,
            SUM(quantity * sell_price) as retail_value,
            COUNT(*) as item_count,
            SUM(quantity) as total_units
        FROM inventory
    """)
    
    row = c.fetchone()
    cost_value = float(row[0] or 0.0)
    retail_value = float(row[1] or 0.0)
    potential_profit = retail_value - cost_value
    
    valuation = {
        'cost_value': round(cost_value, 2),
        'retail_value': round(retail_value, 2),
        'potential_profit': round(potential_profit, 2),
        'item_count': row[2] or 0,
        'total_units': row[3] or 0
    }
    
    conn.close()
    return valuation


def get_low_stock_items(threshold: int = 5) -> List[Dict]:
    """
    Get items with stock below threshold.
    
    Args:
        threshold: Minimum quantity threshold
    
    Returns:
        List of low stock items
    """
    conn = get_conn()
    c = conn.cursor()
    
    c.execute("""
        SELECT 
            item_id,
            sku,
            name,
            category,
            quantity,
            sell_price
        FROM inventory
        WHERE quantity < ?
        ORDER BY quantity ASC
    """, (threshold,))
    
    items = []
    for row in c.fetchall():
        items.append({
            'item_id': row[0],
            'sku': row[1],
            'name': row[2],
            'category': row[3],
            'quantity': row[4],
            'sell_price': float(row[5])
        })
    
    conn.close()
    return items


def get_repair_analytics(days: int = 30) -> Dict:
    """
    Get repair analytics for the specified period.
    
    Args:
        days: Number of days to analyze
    
    Returns:
        Dictionary with repair statistics
    """
    conn = get_conn()
    c = conn.cursor()
    
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    # Overall stats
    c.execute("""
        SELECT 
            COUNT(*) as total_repairs,
            AVG(total_estimate) as avg_value,
            SUM(total_estimate) as total_revenue
        FROM repair_orders
        WHERE DATE(received_date) >= ?
    """, (start_date,))
    
    overall = c.fetchone()
    
    # By status
    c.execute("""
        SELECT 
            status,
            COUNT(*) as count
        FROM repair_orders
        WHERE DATE(received_date) >= ?
        GROUP BY status
    """, (start_date,))
    
    by_status = {row[0]: row[1] for row in c.fetchall()}
    
    # Most common device models
    c.execute("""
        SELECT 
            device_model,
            COUNT(*) as count
        FROM repair_orders
        WHERE DATE(received_date) >= ?
        GROUP BY device_model
        ORDER BY count DESC
        LIMIT 5
    """, (start_date,))
    
    top_devices = [{'model': row[0], 'count': row[1]} for row in c.fetchall()]
    
    analytics = {
        'total_repairs': overall[0] or 0,
        'average_value': round(float(overall[1] or 0.0), 2),
        'total_revenue': round(float(overall[2] or 0.0), 2),
        'by_status': by_status,
        'top_devices': top_devices
    }
    
    conn.close()
    return analytics


def get_financial_dashboard() -> Dict:
    """
    Get comprehensive financial dashboard data.
    
    Returns:
        Dictionary with all key financial metrics
    """
    today = datetime.now().strftime('%Y-%m-%d')
    
    dashboard = {
        'today': get_daily_profit_loss(today),
        'this_week': get_weekly_profit_loss(),
        'this_month': get_monthly_profit_loss(),
        'inventory_valuation': get_inventory_valuation(),
        'low_stock_items': get_low_stock_items(5),
        'top_products': get_top_selling_products(5, 30),
        'top_customers': get_top_customers(5, 30),
        'repair_analytics': get_repair_analytics(30),
        'sales_trends': get_sales_trends(7)  # Last 7 days
    }
    
    return dashboard
