# modules/barcode_handler.py
"""
Barcode scanning handler and utilities
"""
from datetime import datetime
from modules.db import get_conn
from modules.logger import log
from modules.validators import validate_imei, validate_barcode, clean_barcode

def log_scan(barcode: str, scan_type: str, user: str, module: str):
    """Log a barcode scan to the database"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("""
            INSERT INTO scan_log (scan_date, barcode, scan_type, user, module)
            VALUES (?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), barcode, scan_type, user, module))
        conn.commit()
        conn.close()
        log.info(f"Scan logged: {scan_type} - {barcode} in {module}")
    except Exception as e:
        log.error(f"Error logging scan: {e}")

def get_item_by_barcode(barcode: str):
    """Look up inventory item by barcode"""
    try:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT * FROM inventory WHERE barcode = ?", (barcode,))
        result = c.fetchone()
        conn.close()
        return result
    except Exception as e:
        log.error(f"Error looking up barcode: {e}")
        return None

def check_duplicate_imei(imei: str, exclude_repair_id: int = None):
    """Check if IMEI already exists in repair orders"""
    try:
        conn = get_conn()
        c = conn.cursor()
        if exclude_repair_id:
            c.execute("SELECT repair_id, order_number, customer_name FROM repair_orders WHERE imei = ? AND repair_id != ?", 
                     (imei, exclude_repair_id))
        else:
            c.execute("SELECT repair_id, order_number, customer_name FROM repair_orders WHERE imei = ?", (imei,))
        result = c.fetchone()
        conn.close()
        return result
    except Exception as e:
        log.error(f"Error checking duplicate IMEI: {e}")
        return None

def process_scan(scan_data: str, scan_context: str = "general"):
    """
    Process scanned data and determine type
    Returns: (scan_type, cleaned_data, is_valid)
    """
    cleaned = clean_barcode(scan_data)
    
    # Try to determine scan type
    if len(cleaned) == 15 and cleaned.isdigit():
        # Likely IMEI
        is_valid = validate_imei(cleaned)
        return ("IMEI", cleaned, is_valid)
    elif len(cleaned) == 13 and cleaned.isdigit():
        # Likely EAN-13
        is_valid = validate_barcode(cleaned, "EAN-13")
        return ("EAN-13", cleaned, is_valid)
    elif len(cleaned) == 12 and cleaned.isdigit():
        # Likely UPC-A
        is_valid = validate_barcode(cleaned, "UPC-A")
        return ("UPC-A", cleaned, is_valid)
    else:
        # Generic barcode
        is_valid = validate_barcode(cleaned, "any")
        return ("BARCODE", cleaned, is_valid)
