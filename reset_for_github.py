"""
Reset database for GitHub upload - removes all test data
Keeps only the admin user with default password
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "shop.db"
BACKUP_DIR = Path(__file__).resolve().parent / "backups"

def create_backup():
    """Create a backup before cleaning"""
    BACKUP_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = BACKUP_DIR / f"shop_before_github_{timestamp}.db"
    shutil.copy2(DB_PATH, backup_file)
    print(f"✅ Backup created: {backup_file}")
    return backup_file

def reset_database():
    """Reset database to clean state"""
    print("\n" + "="*50)
    print("  Resetting Database for GitHub Upload")
    print("="*50)
    
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        return
    
    # Create backup first
    backup_file = create_backup()
    
    # Connect to database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        print("\n🧹 Cleaning database...")
        
        # Delete in correct order (respecting foreign keys)
        tables_to_clean = [
            ('sale_items', 'sale items'),
            ('sales', 'sales'),
            ('repair_parts', 'repair parts'),
            ('repair_history', 'repair history entries'),
            ('repair_orders', 'repair orders'),
            ('customers', 'customers'),
            ('inventory', 'inventory items'),
        ]
        
        for table, description in tables_to_clean:
            cursor.execute(f"DELETE FROM {table}")
            count = cursor.rowcount
            print(f"   ✅ Deleted {count} {description}")
        
        # Try to delete audit_log if it exists
        try:
            cursor.execute("DELETE FROM audit_log")
            count = cursor.rowcount
            print(f"   ✅ Deleted {count} audit log entries")
        except sqlite3.OperationalError:
            print(f"   ℹ️  No audit_log table (skipped)")
        
        # Delete non-admin users
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
        
        # Show final stats
        print("\n📊 Final Database State")
        print("="*50)
        
        stats = [
            ("Inventory Items", "SELECT COUNT(*) FROM inventory"),
            ("Sales", "SELECT COUNT(*) FROM sales"),
            ("Customers", "SELECT COUNT(*) FROM customers"),
            ("Repair Orders", "SELECT COUNT(*) FROM repair_orders"),
            ("Users", "SELECT COUNT(*) FROM users"),
        ]
        
        for label, query in stats:
            cursor.execute(query)
            count = cursor.fetchone()[0]
            print(f"{label}: {count}")
        
        # Try to show audit logs if table exists
        try:
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            count = cursor.fetchone()[0]
            print(f"Audit Logs: {count}")
        except sqlite3.OperationalError:
            pass
        
        print("="*50)
        print("\n✅ Database is ready for GitHub upload!")
        print("\n⚠️  Default Login Credentials:")
        print("   Username: admin")
        print("   Password: admin123")
        print("\n⚠️  Remember to change password after first login!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        conn.rollback()
        print(f"\n💾 Restoring from backup: {backup_file}")
        conn.close()
        shutil.copy2(backup_file, DB_PATH)
        print("✅ Database restored from backup")
        return
    
    finally:
        conn.close()

def clear_logs():
    """Clear all log files"""
    logs_dir = Path(__file__).resolve().parent / "logs"
    if logs_dir.exists():
        log_files = list(logs_dir.glob("*.log"))
        if log_files:
            print("\n🧹 Clearing log files...")
            for log_file in log_files:
                log_file.unlink()
                print(f"   ✅ Deleted {log_file.name}")
            print(f"✅ Cleared {len(log_files)} log files")
        else:
            print("\n✅ No log files to clear")
    else:
        print("\n✅ Logs directory doesn't exist")

def clear_receipts():
    """Clear generated receipts"""
    receipts_dir = Path(__file__).resolve().parent / "receipts"
    if receipts_dir.exists():
        receipt_files = list(receipts_dir.glob("*.pdf"))
        if receipt_files:
            print("\n🧹 Clearing receipt files...")
            for receipt_file in receipt_files:
                receipt_file.unlink()
                print(f"   ✅ Deleted {receipt_file.name}")
            print(f"✅ Cleared {len(receipt_files)} receipt files")
        else:
            print("\n✅ No receipt files to clear")
    else:
        print("\n✅ Receipts directory doesn't exist")

def clear_reports():
    """Clear generated reports"""
    reports_dir = Path(__file__).resolve().parent / "reports"
    if reports_dir.exists():
        report_files = list(reports_dir.glob("*.pdf"))
        if report_files:
            print("\n🧹 Clearing report files...")
            for report_file in report_files:
                report_file.unlink()
                print(f"   ✅ Deleted {report_file.name}")
            print(f"✅ Cleared {len(report_files)} report files")
        else:
            print("\n✅ No report files to clear")
    else:
        print("\n✅ Reports directory doesn't exist")

def main():
    """Main function"""
    print("\n" + "="*50)
    print("  GitHub Upload Preparation")
    print("="*50)
    print("\nThis will:")
    print("  1. Clean all test data from database")
    print("  2. Clear all log files")
    print("  3. Clear all generated receipts")
    print("  4. Clear all generated reports")
    print("  5. Keep only admin user with default password")
    print("\n⚠️  A backup will be created automatically")
    print("="*50)
    
    response = input("\nProceed? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled")
        return
    
    # Reset database
    reset_database()
    
    # Clear logs
    clear_logs()
    
    # Clear receipts
    clear_receipts()
    
    # Clear reports
    clear_reports()
    
    print("\n" + "="*50)
    print("  ✅ All Done! Repository is ready for GitHub")
    print("="*50)
    print("\nNext steps:")
    print("  1. Review changes: git status")
    print("  2. Stage changes: git add .")
    print("  3. Commit: git commit -m 'chore: Prepare for public release'")
    print("  4. Push: git push origin main")
    print("="*50)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
