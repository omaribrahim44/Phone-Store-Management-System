# add_barcode_tracking.py
"""
Add barcode tracking system for individual product instances
Allows same product to have multiple unique barcodes (serial numbers)
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "shop.db"

def add_barcode_tracking():
    """Add barcode tracking table and update schema"""
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Adding barcode tracking system...")
    
    # Create product_barcodes table
    c.execute("""
        CREATE TABLE IF NOT EXISTS product_barcodes (
            barcode_id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER NOT NULL,
            barcode TEXT UNIQUE NOT NULL,
            serial_number TEXT,
            status TEXT DEFAULT 'available',
            added_date TEXT,
            sold_date TEXT,
            sale_id INTEGER,
            notes TEXT,
            FOREIGN KEY(item_id) REFERENCES inventory(item_id),
            FOREIGN KEY(sale_id) REFERENCES sales(sale_id)
        )
    """)
    print("✓ Created product_barcodes table")
    
    # Create index for faster barcode lookups
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_barcode 
        ON product_barcodes(barcode)
    """)
    print("✓ Created barcode index")
    
    # Create index for item_id lookups
    c.execute("""
        CREATE INDEX IF NOT EXISTS idx_barcode_item 
        ON product_barcodes(item_id, status)
    """)
    print("✓ Created item status index")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*60)
    print("Barcode Tracking System Added Successfully!")
    print("="*60)
    print("\nFeatures:")
    print("  • Track individual product instances with unique barcodes")
    print("  • Same product can have multiple barcodes/serial numbers")
    print("  • Track which specific item was sold")
    print("  • Prevent selling the same barcode twice")
    print("  • Status tracking: available, sold, reserved, damaged")
    print("\nUsage:")
    print("  1. Add product to inventory (creates base product)")
    print("  2. Scan/add individual barcodes for each physical item")
    print("  3. When selling, scan barcode to sell specific item")
    print("  4. System tracks which exact item was sold")

if __name__ == "__main__":
    add_barcode_tracking()
