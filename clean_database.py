#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Database Cleaning Utility
Removes test/sample data while preserving structure
"""

import sqlite3
import os
from datetime import datetime
import shutil

def create_backup():
    """Create backup before cleaning"""
    if not os.path.exists('backups'):
        os.makedirs('backups')
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'backups/before_clean_{timestamp}.db'
    
    shutil.copy('shop.db', backup_file)
    print(f"✅ Backup created: {backup_file}")
    return backup_file

def clean_all_data():
    """Remove all data but keep admin user"""
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    try:
        print("\n🧹 Cleaning database...")
        
        # Delete in correct order (respecting foreign keys)
        tables_to_clean = [
            ('sale_items', 'sale items'),
            ('sales', 'sales'),
            ('repair_parts', 'repair parts'),
            ('repair_history', 'repair history'),
            ('repair_orders', 'repair orders'),
            ('customers', 'customers'),
            ('inventory', 'inventory items'),
            ('audit_log', 'audit logs'),
        ]
        
        for table, description in tables_to_clean:
            cursor.execute(f"DELETE FROM {table}")
            count = cursor.rowcount
            print(f"   ✅ Deleted {count} {description}")
        
        # Keep only admin user, delete others
        cursor.execute("DELETE FROM users WHERE username != 'admin'")
        count = cursor.rowcount
        if count > 0:
            print(f"   ✅ Deleted {count} non-admin users")
        
        # Reset admin password to default
        cursor.execute("""
            UPDATE users 
            SET password = 'admin123' 
            WHERE username = 'admin'
        """)
        print("   ✅ Reset admin password to 'admin123'")
        
        conn.commit()
        print("\n✅ Database cleaned successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Error cleaning database: {e}")
        raise
    finally:
        conn.close()

def clean_specific_data():
    """Interactive cleaning - choose what to delete"""
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    print("\n📋 What would you like to delete?")
    print("=" * 50)
    
    # Get counts
    counts = {}
    tables = {
        'inventory': 'Products/Inventory',
        'sales': 'Sales Records',
        'customers': 'Customers',
        'repair_orders': 'Repair Orders',
        'users': 'Users (except admin)',
        'audit_log': 'Audit Logs'
    }
    
    for table, name in tables.items():
        if table == 'users':
            cursor.execute("SELECT COUNT(*) FROM users WHERE username != 'admin'")
        else:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        counts[table] = count
        print(f"{name}: {count} records")
    
    print("=" * 50)
    print("\nOptions:")
    print("1. Delete ALL data (keep admin user)")
    print("2. Delete specific categories")
    print("3. Cancel")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == '1':
        confirm = input("\n⚠️  Delete ALL data? (yes/no): ").strip().lower()
        if confirm == 'yes':
            clean_all_data()
        else:
            print("Cancelled.")
    
    elif choice == '2':
        print("\nSelect what to delete (y/n for each):")
        
        to_delete = []
        
        if counts['inventory'] > 0:
            if input(f"Delete {counts['inventory']} inventory items? (y/n): ").lower() == 'y':
                to_delete.append(('inventory', 'inventory items'))
        
        if counts['sales'] > 0:
            if input(f"Delete {counts['sales']} sales records? (y/n): ").lower() == 'y':
                to_delete.append(('sale_items', 'sale items'))
                to_delete.append(('sales', 'sales'))
        
        if counts['customers'] > 0:
            if input(f"Delete {counts['customers']} customers? (y/n): ").lower() == 'y':
                to_delete.append(('customers', 'customers'))
        
        if counts['repair_orders'] > 0:
            if input(f"Delete {counts['repair_orders']} repair orders? (y/n): ").lower() == 'y':
                to_delete.append(('repair_parts', 'repair parts'))
                to_delete.append(('repair_history', 'repair history'))
                to_delete.append(('repair_orders', 'repair orders'))
        
        if counts['users'] > 0:
            if input(f"Delete {counts['users']} non-admin users? (y/n): ").lower() == 'y':
                to_delete.append(('users_non_admin', 'non-admin users'))
        
        if counts['audit_log'] > 0:
            if input(f"Delete {counts['audit_log']} audit logs? (y/n): ").lower() == 'y':
                to_delete.append(('audit_log', 'audit logs'))
        
        if to_delete:
            confirm = input(f"\n⚠️  Confirm deletion of {len(to_delete)} categories? (yes/no): ").lower()
            if confirm == 'yes':
                try:
                    for table, description in to_delete:
                        if table == 'users_non_admin':
                            cursor.execute("DELETE FROM users WHERE username != 'admin'")
                        else:
                            cursor.execute(f"DELETE FROM {table}")
                        count = cursor.rowcount
                        print(f"✅ Deleted {count} {description}")
                    
                    conn.commit()
                    print("\n✅ Selected data deleted successfully!")
                except Exception as e:
                    conn.rollback()
                    print(f"\n❌ Error: {e}")
            else:
                print("Cancelled.")
        else:
            print("Nothing selected for deletion.")
    
    else:
        print("Cancelled.")
    
    conn.close()

def show_database_stats():
    """Show current database statistics"""
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    print("\n📊 Current Database Statistics")
    print("=" * 50)
    
    # Inventory
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantity), 0) FROM inventory")
    inv_count, inv_qty = cursor.fetchone()
    print(f"Inventory Items: {inv_count} products, {inv_qty} total quantity")
    
    # Sales
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total), 0) FROM sales")
    sales_count, sales_total = cursor.fetchone()
    print(f"Sales: {sales_count} transactions, ${sales_total:,.2f} total")
    
    # Customers
    cursor.execute("SELECT COUNT(*) FROM customers")
    cust_count = cursor.fetchone()[0]
    print(f"Customers: {cust_count} records")
    
    # Repairs
    cursor.execute("SELECT COUNT(*), COALESCE(SUM(total_estimate), 0) FROM repair_orders")
    repair_count, repair_total = cursor.fetchone()
    print(f"Repair Orders: {repair_count} orders, ${repair_total:,.2f} total")
    
    # Users
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"Users: {user_count} accounts")
    
    # Audit logs
    cursor.execute("SELECT COUNT(*) FROM audit_log")
    log_count = cursor.fetchone()[0]
    print(f"Audit Logs: {log_count} entries")
    
    print("=" * 50)
    
    conn.close()

def main():
    """Main function"""
    print("=" * 50)
    print("  Database Cleaning Utility")
    print("=" * 50)
    
    if not os.path.exists('shop.db'):
        print("\n❌ Error: shop.db not found!")
        print("Run db_init.py first to create the database.")
        return
    
    # Show current stats
    show_database_stats()
    
    print("\n⚠️  WARNING: This will delete data from your database!")
    print("A backup will be created automatically.")
    
    proceed = input("\nDo you want to proceed? (yes/no): ").strip().lower()
    
    if proceed != 'yes':
        print("\nOperation cancelled.")
        return
    
    # Create backup
    backup_file = create_backup()
    
    # Clean data
    clean_specific_data()
    
    # Show final stats
    print("\n" + "=" * 50)
    show_database_stats()
    
    print(f"\n💾 Backup saved to: {backup_file}")
    print("\n✅ Done! Your database is ready for data entry.")
    print("\n⚠️  Remember to change admin password after login!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        input("\nPress Enter to exit...")
