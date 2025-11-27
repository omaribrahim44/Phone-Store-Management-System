# modules/barcode_manager.py
"""
Barcode Management System
Handles individual product instances with unique barcodes
"""

from modules.db import get_conn
from datetime import datetime
from typing import Optional, List, Tuple


class BarcodeStatus:
    """Barcode status constants"""
    AVAILABLE = 'available'
    SOLD = 'sold'
    RESERVED = 'reserved'
    DAMAGED = 'damaged'
    RETURNED = 'returned'


def add_barcode(item_id: int, barcode: str, serial_number: str = None, notes: str = None) -> bool:
    """
    Add a unique barcode for a product.
    
    Args:
        item_id: Product ID from inventory
        barcode: Unique barcode/IMEI/serial
        serial_number: Optional additional serial number
        notes: Optional notes
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        
        # Check if barcode already exists
        c.execute("SELECT barcode_id FROM product_barcodes WHERE barcode = ?", (barcode,))
        if c.fetchone():
            conn.close()
            raise ValueError(f"Barcode {barcode} already exists")
        
        # Check if item exists
        c.execute("SELECT item_id FROM inventory WHERE item_id = ?", (item_id,))
        if not c.fetchone():
            conn.close()
            raise ValueError(f"Product ID {item_id} not found")
        
        # Add barcode
        c.execute("""
            INSERT INTO product_barcodes 
            (item_id, barcode, serial_number, status, added_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_id, barcode, serial_number, BarcodeStatus.AVAILABLE, 
              datetime.now().isoformat(), notes))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error adding barcode: {e}")
        return False


def get_barcode_info(barcode: str) -> Optional[Tuple]:
    """
    Get information about a barcode.
    
    Args:
        barcode: Barcode to lookup
    
    Returns:
        Tuple with barcode info or None if not found
        (barcode_id, item_id, barcode, serial_number, status, added_date, 
         sold_date, sale_id, notes, item_name, sell_price)
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                pb.barcode_id, pb.item_id, pb.barcode, pb.serial_number, 
                pb.status, pb.added_date, pb.sold_date, pb.sale_id, pb.notes,
                i.name, i.sell_price, i.sku
            FROM product_barcodes pb
            JOIN inventory i ON pb.item_id = i.item_id
            WHERE pb.barcode = ?
        """, (barcode,))
        
        result = c.fetchone()
        conn.close()
        return result
        
    except Exception as e:
        print(f"Error getting barcode info: {e}")
        return None


def get_available_barcodes(item_id: int) -> List[Tuple]:
    """
    Get all available barcodes for a product.
    
    Args:
        item_id: Product ID
    
    Returns:
        List of tuples with barcode info
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        
        c.execute("""
            SELECT barcode_id, barcode, serial_number, added_date, notes
            FROM product_barcodes
            WHERE item_id = ? AND status = ?
            ORDER BY added_date DESC
        """, (item_id, BarcodeStatus.AVAILABLE))
        
        results = c.fetchall()
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error getting available barcodes: {e}")
        return []


def mark_barcode_sold(barcode: str, sale_id: int) -> bool:
    """
    Mark a barcode as sold.
    
    Args:
        barcode: Barcode that was sold
        sale_id: Sale ID
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        
        # Check if barcode exists and is available
        c.execute("""
            SELECT barcode_id, status 
            FROM product_barcodes 
            WHERE barcode = ?
        """, (barcode,))
        
        result = c.fetchone()
        if not result:
            conn.close()
            raise ValueError(f"Barcode {barcode} not found")
        
        if result[1] != BarcodeStatus.AVAILABLE:
            conn.close()
            raise ValueError(f"Barcode {barcode} is not available (status: {result[1]})")
        
        # Mark as sold
        c.execute("""
            UPDATE product_barcodes
            SET status = ?, sold_date = ?, sale_id = ?
            WHERE barcode = ?
        """, (BarcodeStatus.SOLD, datetime.now().isoformat(), sale_id, barcode))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error marking barcode as sold: {e}")
        return False


def get_product_stock_count(item_id: int) -> int:
    """
    Get count of available barcodes for a product.
    
    Args:
        item_id: Product ID
    
    Returns:
        Count of available items
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        
        c.execute("""
            SELECT COUNT(*) 
            FROM product_barcodes
            WHERE item_id = ? AND status = ?
        """, (item_id, BarcodeStatus.AVAILABLE))
        
        count = c.fetchone()[0]
        conn.close()
        return count
        
    except Exception as e:
        print(f"Error getting stock count: {e}")
        return 0


def update_barcode_status(barcode: str, new_status: str, notes: str = None) -> bool:
    """
    Update barcode status.
    
    Args:
        barcode: Barcode to update
        new_status: New status
        notes: Optional notes
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        
        if notes:
            c.execute("""
                UPDATE product_barcodes
                SET status = ?, notes = ?
                WHERE barcode = ?
            """, (new_status, notes, barcode))
        else:
            c.execute("""
                UPDATE product_barcodes
                SET status = ?
                WHERE barcode = ?
            """, (new_status, barcode))
        
        if c.rowcount == 0:
            conn.close()
            raise ValueError(f"Barcode {barcode} not found")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error updating barcode status: {e}")
        return False


def delete_barcode(barcode: str) -> bool:
    """
    Delete a barcode (only if not sold).
    
    Args:
        barcode: Barcode to delete
    
    Returns:
        True if successful, False otherwise
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        
        # Check status
        c.execute("SELECT status FROM product_barcodes WHERE barcode = ?", (barcode,))
        result = c.fetchone()
        
        if not result:
            conn.close()
            raise ValueError(f"Barcode {barcode} not found")
        
        if result[0] == BarcodeStatus.SOLD:
            conn.close()
            raise ValueError(f"Cannot delete sold barcode {barcode}")
        
        # Delete
        c.execute("DELETE FROM product_barcodes WHERE barcode = ?", (barcode,))
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error deleting barcode: {e}")
        return False


def get_all_barcodes_for_item(item_id: int) -> List[Tuple]:
    """
    Get all barcodes for a product (all statuses).
    
    Args:
        item_id: Product ID
    
    Returns:
        List of tuples with barcode info
    """
    try:
        conn = get_conn()
        c = conn.cursor()
        
        c.execute("""
            SELECT 
                barcode_id, barcode, serial_number, status, 
                added_date, sold_date, sale_id, notes
            FROM product_barcodes
            WHERE item_id = ?
            ORDER BY added_date DESC
        """, (item_id,))
        
        results = c.fetchall()
        conn.close()
        return results
        
    except Exception as e:
        print(f"Error getting all barcodes: {e}")
        return []


def bulk_add_barcodes(item_id: int, barcodes: List[str]) -> Tuple[int, int]:
    """
    Add multiple barcodes at once.
    
    Args:
        item_id: Product ID
        barcodes: List of barcode strings
    
    Returns:
        Tuple of (success_count, failure_count)
    """
    success = 0
    failure = 0
    
    for barcode in barcodes:
        if add_barcode(item_id, barcode.strip()):
            success += 1
        else:
            failure += 1
    
    return success, failure
