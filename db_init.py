# db_init.py (Professional version)
import sqlite3
from datetime import datetime
import hashlib, os
from pathlib import Path

DB = Path(__file__).resolve().parent / "shop.db"


# ---------------------- Password hashing ----------------------
def hash_password(plain: str) -> str:
    """Generate salted sha256 password hash."""
    salt = os.urandom(8).hex()
    h = hashlib.sha256((salt + plain).encode("utf-8")).hexdigest()
    return f"{salt}${h}"


# ---------------------- Init DB ----------------------
conn = sqlite3.connect(DB)
c = conn.cursor()

now = datetime.now().isoformat()


# ===================== USERS TABLE =====================
c.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    full_name TEXT,
    role TEXT DEFAULT 'Cashier',
    created_at TEXT
);
""")


# ===================== INVENTORY =====================
c.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT UNIQUE,
    name TEXT,
    description TEXT,
    quantity INTEGER DEFAULT 0,
    buy_price REAL DEFAULT 0,
    sell_price REAL DEFAULT 0
);
""")


# ===================== CUSTOMERS TABLE =====================
c.execute("""
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT UNIQUE,
    email TEXT,
    address TEXT,
    customer_type TEXT DEFAULT 'Both',
    created_date TEXT,
    last_purchase_date TEXT,
    last_repair_date TEXT,
    total_purchases INTEGER DEFAULT 0,
    total_repairs INTEGER DEFAULT 0,
    total_spent REAL DEFAULT 0.0,
    notes TEXT
);
""")


# ===================== SALES =====================
c.execute("""
CREATE TABLE IF NOT EXISTS sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_date TEXT,
    customer_id INTEGER,
    customer_name TEXT,
    total_amount REAL,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS sale_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sale_id INTEGER,
    item_id INTEGER,
    quantity INTEGER,
    unit_price REAL,
    cost_price REAL DEFAULT 0,
    FOREIGN KEY(sale_id) REFERENCES sales(sale_id),
    FOREIGN KEY(item_id) REFERENCES inventory(item_id)
);
""")


# ===================== REPAIRS =====================
c.execute("""
CREATE TABLE IF NOT EXISTS repair_orders (
    repair_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_number TEXT UNIQUE,
    customer_id INTEGER,
    customer_name TEXT,
    customer_phone TEXT,
    device_model TEXT,
    imei TEXT,
    reported_problem TEXT,
    received_date TEXT,
    estimated_delivery TEXT,
    status TEXT DEFAULT 'Received',
    technician TEXT,
    total_estimate REAL DEFAULT 0,
    notes TEXT,
    FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);
""")

c.execute("""
CREATE TABLE IF NOT EXISTS repair_parts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER,
    item_id INTEGER,
    part_name TEXT,
    qty INTEGER DEFAULT 1,
    unit_price REAL DEFAULT 0,
    FOREIGN KEY(repair_id) REFERENCES repair_orders(repair_id),
    FOREIGN KEY(item_id) REFERENCES inventory(item_id)
);
""")


# ===================== REPAIR HISTORY =====================
c.execute("""
CREATE TABLE IF NOT EXISTS repair_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT,
    repair_id INTEGER,
    action_date TEXT,
    action_by TEXT,
    status_from TEXT,
    status_to TEXT,
    comment TEXT,
    FOREIGN KEY(repair_id) REFERENCES repair_orders(repair_id)
);
""")


# ===================== Default Admin =====================
try:
    c.execute("SELECT COUNT(*) FROM users WHERE username = ?", ("admin",))
    exists = c.fetchone()[0]

    if exists == 0:
        admin_pw = hash_password("admin123")
        c.execute("""
            INSERT INTO users (username, password, full_name, role, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, ("admin", admin_pw, "Administrator", "Admin", now))
        print("Default admin created -> username: admin  password: admin123")
    else:
        print("Admin user already exists.")
except Exception as e:
    print("Warning while checking/creating admin:", e)


conn.commit()
conn.close()
print("Database initialized:", DB)
