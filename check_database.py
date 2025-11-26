#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Quick script to check database contents"""

import sqlite3

conn = sqlite3.connect('shop.db')
cursor = conn.cursor()

print("\n" + "="*50)
print("📊 Current Database Contents")
print("="*50)

tables = [
    ('inventory', 'Products/Inventory'),
    ('sales', 'Sales Records'),
    ('customers', 'Customers'),
    ('repair_orders', 'Repair Orders'),
    ('users', 'Users')
]

for table, name in tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{name}: {count} records")
    except:
        print(f"{name}: Table not found")

print("="*50)

# Check if there's any data
cursor.execute("SELECT COUNT(*) FROM inventory")
inv_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM sales")
sales_count = cursor.fetchone()[0]

if inv_count > 0 or sales_count > 0:
    print("\n💡 You have data in your database.")
    print("   Use RESET_DATABASE.bat or CLEAN_DATABASE.bat to clean it.")
else:
    print("\n✅ Database is empty and ready for data entry!")

conn.close()
