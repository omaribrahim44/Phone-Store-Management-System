# modules/db.py
from pathlib import Path
import sqlite3

# DB file is at project root: E:\PHONE MANAGEMENT SYSTEM\shop.db
DB_PATH = Path(__file__).resolve().parents[1] / "shop.db"

def get_conn():
    """Return a sqlite3.Connection to the project DB with UTF-8 support for Arabic text."""
    conn = sqlite3.connect(str(DB_PATH))
    # Ensure UTF-8 encoding for Arabic and international characters
    conn.text_factory = str
    return conn

def init_db():
    """Initialize the database with necessary tables."""
    with get_conn() as conn:
        c = conn.cursor()
        
        # Audit logs table (Phase 3)
        c.execute('''CREATE TABLE IF NOT EXISTS audit_logs (
                        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        user TEXT,
                        action_type TEXT NOT NULL,
                        entity_type TEXT NOT NULL,
                        entity_id INTEGER,
                        old_value TEXT,
                        new_value TEXT,
                        description TEXT
                    )''')
        
        # Repair history table
        c.execute('''CREATE TABLE IF NOT EXISTS repair_history (
                        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repair_id INTEGER,
                        action_date TEXT,
                        action_by TEXT,
                        status_from TEXT,
                        status_to TEXT,
                        comment TEXT,
                        FOREIGN KEY(repair_id) REFERENCES repair_orders(repair_id)
                    )''')
        
        # Scan log table (for barcode scanning tracking)
        c.execute('''CREATE TABLE IF NOT EXISTS scan_log (
                        scan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        scan_date TEXT NOT NULL,
                        barcode TEXT NOT NULL,
                        scan_type TEXT,
                        user TEXT,
                        module TEXT
                    )''')
        
        # Check if barcode column exists in inventory, add if not
        c.execute("PRAGMA table_info(inventory)")
        columns = [col[1] for col in c.fetchall()]
        if 'barcode' not in columns:
            c.execute("ALTER TABLE inventory ADD COLUMN barcode TEXT")
            c.execute("CREATE INDEX IF NOT EXISTS idx_inventory_barcode ON inventory(barcode)")
        
        conn.commit()

# Call init_db() when the module is imported to ensure tables exist
init_db()
