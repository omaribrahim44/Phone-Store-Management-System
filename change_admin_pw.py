# change_admin_pw.py
"""
A safe admin-password reset script.

Features:
- Checks if DB exists
- Checks if admin user exists
- Prompts for new password twice (confirmation)
- Hashing identical to modules.models
- Safe error handling + timestamp update
"""

import sqlite3
import hashlib
import os
import getpass
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parent / "shop.db"


def hash_password(plain: str) -> str:
    salt = os.urandom(8).hex()
    h = hashlib.sha256((salt + plain).encode("utf-8")).hexdigest()
    return f"{salt}${h}"


def admin_exists(conn) -> bool:
    c = conn.cursor()
    c.execute("SELECT user_id FROM users WHERE username = 'admin'")
    return c.fetchone() is not None


def main():
    print("=== Admin Password Reset Tool ===")

    if not DB.exists():
        print(f"[ERROR] Database not found: {DB}")
        return

    conn = sqlite3.connect(DB)
    if not admin_exists(conn):
        print("[ERROR] Admin user not found in database.")
        conn.close()
        return

    # ask for password twice
    pw1 = getpass.getpass("Enter NEW admin password: ").strip()
    pw2 = getpass.getpass("Re-enter password: ").strip()

    if not pw1:
        print("[ERROR] Password cannot be empty.")
        conn.close()
        return

    if pw1 != pw2:
        print("[ERROR] Passwords do not match.")
        conn.close()
        return

    hashed = hash_password(pw1)

    try:
        c = conn.cursor()
        c.execute(
            "UPDATE users SET password = ?, created_at = ? WHERE username = ?",
            (hashed, datetime.now().isoformat(), "admin")
        )
        conn.commit()
        print("[OK] Admin password updated successfully.")
    except Exception as e:
        print(f"[ERROR] Failed to update password: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
