# modules/enhance_sales_schema.py
"""
Enhance sales tables to capture comprehensive transaction details for reporting.
This adds fields for: seller, payment method, discount, timestamps, etc.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "shop.db"

def enhance_sales_schema():
    """Add missing columns to sales tables for comprehensive tracking"""
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    try:
        # Check existing columns in sales table
        c.execute("PRAGMA table_info(sales)")
        existing_columns = [col[1] for col in c.fetchall()]
        
        # Add missing columns to sales table
        columns_to_add = {
            'seller_name': 'TEXT',  # Who made the sale
            'customer_phone': 'TEXT',  # Customer phone
            'customer_email': 'TEXT',  # Customer email
            'customer_address': 'TEXT',  # Customer address
            'subtotal': 'REAL DEFAULT 0',  # Before discount
            'discount_percent': 'REAL DEFAULT 0',  # Discount percentage
            'discount_amount': 'REAL DEFAULT 0',  # Discount amount
            'payment_method': 'TEXT DEFAULT "Cash"',  # Cash, Card, etc.
            'sale_time': 'TEXT',  # Exact time of sale (HH:MM:SS)
            'notes': 'TEXT',  # Additional notes
        }
        
        for col_name, col_type in columns_to_add.items():
            if col_name not in existing_columns:
                c.execute(f"ALTER TABLE sales ADD COLUMN {col_name} {col_type}")
                print(f"Added column: {col_name} to sales table")
        
        # Check existing columns in sale_items table
        c.execute("PRAGMA table_info(sale_items)")
        existing_item_columns = [col[1] for col in c.fetchall()]
        
        # Add missing columns to sale_items table
        item_columns_to_add = {
            'item_name': 'TEXT',  # Product name (for historical record)
            'item_sku': 'TEXT',  # Product SKU (for historical record)
            'item_category': 'TEXT',  # Product category
            'line_total': 'REAL DEFAULT 0',  # quantity * unit_price
            'profit': 'REAL DEFAULT 0',  # (unit_price - cost_price) * quantity
        }
        
        for col_name, col_type in item_columns_to_add.items():
            if col_name not in existing_item_columns:
                c.execute(f"ALTER TABLE sale_items ADD COLUMN {col_name} {col_type}")
                print(f"Added column: {col_name} to sale_items table")
        
        # Create indexes for faster reporting queries
        c.execute("CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(sale_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sales_seller ON sales(seller_name)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_name)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_sale_items_sale_id ON sale_items(sale_id)")
        
        conn.commit()
        print("✅ Sales schema enhanced successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error enhancing sales schema: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    enhance_sales_schema()
