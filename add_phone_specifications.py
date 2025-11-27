# add_phone_specifications.py
"""
Add phone specifications tracking to inventory
Adds Storage, RAM, Color, Condition, and other specs for mobile phones
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "shop.db"

def add_phone_specifications():
    """Add phone specifications columns to inventory table"""
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    print("Adding phone specifications to inventory...")
    
    # Check existing columns
    c.execute("PRAGMA table_info(inventory)")
    existing_columns = [col[1] for col in c.fetchall()]
    
    # Add new columns if they don't exist
    new_columns = {
        'storage': 'TEXT',           # e.g., "128GB", "256GB", "512GB"
        'ram': 'TEXT',               # e.g., "4GB", "6GB", "8GB", "12GB"
        'color': 'TEXT',             # e.g., "Black", "White", "Blue"
        'condition': 'TEXT',         # e.g., "New", "Used", "Refurbished"
        'brand': 'TEXT',             # e.g., "Apple", "Samsung", "Xiaomi"
        'model': 'TEXT',             # e.g., "iPhone 15 Pro", "Galaxy S24"
        'processor': 'TEXT',         # e.g., "A17 Pro", "Snapdragon 8 Gen 3"
        'battery': 'TEXT',           # e.g., "4500mAh", "5000mAh"
        'screen_size': 'TEXT',       # e.g., "6.1 inch", "6.7 inch"
        'camera': 'TEXT',            # e.g., "48MP", "108MP Triple"
        'warranty_months': 'INTEGER' # e.g., 12, 24
    }
    
    added = []
    skipped = []
    
    for column, data_type in new_columns.items():
        if column not in existing_columns:
            try:
                c.execute(f"ALTER TABLE inventory ADD COLUMN {column} {data_type}")
                added.append(column)
                print(f"  ✓ Added column: {column}")
            except Exception as e:
                print(f"  ❌ Error adding {column}: {e}")
        else:
            skipped.append(column)
            print(f"  ⊘ Column already exists: {column}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*70)
    print("PHONE SPECIFICATIONS ADDED SUCCESSFULLY!")
    print("="*70)
    print(f"\n✓ Added {len(added)} new columns")
    print(f"⊘ Skipped {len(skipped)} existing columns")
    
    print("\n📱 New Specifications Available:")
    print("  • Storage (128GB, 256GB, 512GB, 1TB)")
    print("  • RAM (4GB, 6GB, 8GB, 12GB, 16GB)")
    print("  • Color (Black, White, Blue, etc.)")
    print("  • Condition (New, Used, Refurbished)")
    print("  • Brand (Apple, Samsung, Xiaomi, etc.)")
    print("  • Model (iPhone 15 Pro, Galaxy S24, etc.)")
    print("  • Processor (A17 Pro, Snapdragon, etc.)")
    print("  • Battery (4500mAh, 5000mAh, etc.)")
    print("  • Screen Size (6.1 inch, 6.7 inch, etc.)")
    print("  • Camera (48MP, 108MP Triple, etc.)")
    print("  • Warranty (12, 24 months)")
    
    print("\n💡 Usage Example:")
    print("  Product: iPhone 15 Pro")
    print("  Storage: 256GB")
    print("  RAM: 8GB")
    print("  Color: Deep Purple")
    print("  Condition: New")
    print("  Warranty: 12 months")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    add_phone_specifications()
