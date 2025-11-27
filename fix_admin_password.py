# fix_admin_password.py
"""
Fix admin password to 'admin' for easy login
"""

import sqlite3
from pathlib import Path
import hashlib
import os

DB_PATH = Path(__file__).resolve().parent / "shop.db"

def hash_password(plain: str) -> str:
    """Generate salted sha256 password hash."""
    salt = os.urandom(8).hex()
    h = hashlib.sha256((salt + plain).encode("utf-8")).hexdigest()
    return f"{salt}${h}"

def fix_admin_password():
    """Set admin password to 'admin'"""
    if not DB_PATH.exists():
        print(f"❌ Database not found: {DB_PATH}")
        print("Run db_init.py first to create the database")
        return
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Check if admin exists
    c.execute("SELECT user_id, username FROM users WHERE username = ?", ("admin",))
    admin = c.fetchone()
    
    if not admin:
        print("❌ Admin user not found!")
        print("Creating admin user...")
        
        # Create admin user
        admin_pw = hash_password("admin")
        from datetime import datetime
        c.execute("""
            INSERT INTO users (username, password, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", admin_pw, "Administrator", "Admin", datetime.now().isoformat()))
        conn.commit()
        print("✅ Admin user created with password: admin")
    else:
        print(f"✅ Found admin user (ID: {admin[0]})")
        print("Updating password to 'admin'...")
        
        # Update password
        new_password = hash_password("admin")
        c.execute("UPDATE users SET password = ? WHERE username = ?", (new_password, "admin"))
        conn.commit()
        print("✅ Admin password updated to: admin")
    
    conn.close()
    
    print("\n" + "="*50)
    print("Login Credentials:")
    print("  Username: admin")
    print("  Password: admin")
    print("="*50)
    print("\n⚠️  IMPORTANT: Change this password after first login!")

if __name__ == "__main__":
    fix_admin_password()
