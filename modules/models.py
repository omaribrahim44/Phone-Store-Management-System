# -*- coding: utf-8 -*-
# modules/models.py
from .db import get_conn
from datetime import datetime
import hashlib, os

# ---------------- password helpers ----------------
def hash_password(plain: str) -> str:
    salt = os.urandom(8).hex()
    h = hashlib.sha256((salt + plain).encode("utf-8")).hexdigest()
    return f"{salt}${h}"

def verify_password(stored: str, plaintext: str) -> bool:
    try:
        salt, h = stored.split("$", 1)
        return hashlib.sha256((salt + plaintext).encode("utf-8")).hexdigest() == h
    except Exception:
        return False

# ---------------- users ----------------
def get_user(username: str):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT user_id, username, password, full_name, role, created_at FROM users WHERE username = ?", (username,))
    row = c.fetchone(); conn.close()
    return row

def add_user(username: str, plain_password: str, full_name: str = "", role: str = "Cashier"):
    hashed = hash_password(plain_password)
    conn = get_conn(); c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password, full_name, role, created_at) VALUES (?, ?, ?, ?, ?)",
                  (username, hashed, full_name, role, datetime.now().isoformat()))
        conn.commit()
        return True
    except Exception as e:
        print("add_user error:", e)
        return False
    finally:
        conn.close()

def get_all_users():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT user_id, username, full_name, role, created_at FROM users ORDER BY user_id")
    rows = c.fetchall(); conn.close()
    return rows

def delete_user_by_id(user_id: int) -> bool:
    conn = get_conn(); c = conn.cursor()
    try:
        c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
        return True
    except Exception as e:
        print("delete_user_by_id error:", e)
        return False
    finally:
        conn.close()

def update_user_password(user_id: int, new_plain: str) -> bool:
    hashed = hash_password(new_plain)
    conn = get_conn(); c = conn.cursor()
    try:
        c.execute("UPDATE users SET password = ? WHERE user_id = ?", (hashed, user_id))
        conn.commit()
        return True
    except Exception as e:
        print("update_user_password error:", e)
        return False
    finally:
        conn.close()

# ---------------- inventory ----------------
def add_inventory_item(sku: str, name: str, qty: int, buy: float, sell: float, category: str, desc: str = "") -> bool:
    """
    Add an inventory item with validation and transaction support.
    
    Args:
        sku: Stock keeping unit (unique identifier)
        name: Item name
        qty: Quantity (non-negative)
        buy: Buy price (non-negative)
        sell: Sell price (non-negative)
        category: Item category
        desc: Optional description
    
    Returns:
        True if successful, False otherwise
    """
    from modules.validators import validate_sku, validate_required, validate_quantity, validate_price
    from modules.transaction_manager import transaction
    
    # Validate inputs
    sku_result = validate_sku(sku)
    if not sku_result.valid:
        print(f"add_inventory_item validation error: {sku_result.error_message}")
        return False
    
    name_result = validate_required(name, "name")
    if not name_result.valid:
        print(f"add_inventory_item validation error: {name_result.error_message}")
        return False
    
    qty_result = validate_quantity(qty)
    if not qty_result.valid:
        print(f"add_inventory_item validation error: {qty_result.error_message}")
        return False
    
    buy_result = validate_price(buy)
    if not buy_result.valid:
        print(f"add_inventory_item validation error: {buy_result.error_message}")
        return False
    
    sell_result = validate_price(sell)
    if not sell_result.valid:
        print(f"add_inventory_item validation error: {sell_result.error_message}")
        return False
    
    # Use validated/normalized values
    sku = sku_result.normalized_value
    qty = qty_result.normalized_value
    buy = buy_result.normalized_value
    sell = sell_result.normalized_value
    
    # Execute in transaction
    try:
        with transaction() as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO inventory (sku, name, category, description, quantity, buy_price, sell_price) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (sku, name, category, desc, qty, buy, sell)
            )
        return True
    except Exception as e:
        print("add_inventory_item error:", e)
        return False


def update_inventory_item(item_id: int, sku: str, name: str, category: str, qty: int, buy_price: float, sell_price: float, description: str = None) -> bool:
    """
    Update an inventory item.
    
    Args:
        item_id: Item ID to update
        sku: Stock keeping unit
        name: Item name
        category: Item category
        qty: Quantity
        buy_price: Buy price
        sell_price: Sell price
        description: Optional description
    
    Returns:
        True if successful, False otherwise
    """
    from modules.validators import validate_quantity, validate_price
    from modules.transaction_manager import transaction
    
    # Validate inputs
    qty_result = validate_quantity(qty)
    if not qty_result.valid:
        print(f"update_inventory_item validation error: {qty_result.error_message}")
        return False
    
    buy_result = validate_price(buy_price)
    if not buy_result.valid:
        print(f"update_inventory_item validation error: {buy_result.error_message}")
        return False
    
    sell_result = validate_price(sell_price)
    if not sell_result.valid:
        print(f"update_inventory_item validation error: {sell_result.error_message}")
        return False
    
    # Use validated values
    qty = qty_result.normalized_value
    buy_price = buy_result.normalized_value
    sell_price = sell_result.normalized_value
    
    # Execute in transaction
    try:
        with transaction() as conn:
            c = conn.cursor()
            if description is not None:
                c.execute(
                    "UPDATE inventory SET sku=?, name=?, category=?, quantity=?, buy_price=?, sell_price=?, description=? WHERE item_id=?",
                    (sku, name, category, qty, buy_price, sell_price, description, item_id)
                )
            else:
                c.execute(
                    "UPDATE inventory SET sku=?, name=?, category=?, quantity=?, buy_price=?, sell_price=? WHERE item_id=?",
                    (sku, name, category, qty, buy_price, sell_price, item_id)
                )
        return True
    except Exception as e:
        print("update_inventory_item error:", e)
        return False


def get_inventory():
    """
    Get all inventory items.
    
    Returns:
        List of tuples: (item_id, sku, name, category, quantity, buy_price, sell_price)
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id, sku, name, category, quantity, buy_price, sell_price FROM inventory")
    rows = c.fetchall()
    conn.close()
    return rows


def get_inventory_item_by_id(item_id: int):
    """
    Get a specific inventory item by ID.
    
    Args:
        item_id: Item ID
    
    Returns:
        Tuple with item data or None if not found
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id, sku, name, category, description, quantity, buy_price, sell_price FROM inventory WHERE item_id = ?", (item_id,))
    row = c.fetchone()
    conn.close()
    return row


def get_inventory_item_by_sku(sku: str):
    """
    Get a specific inventory item by SKU.
    
    Args:
        sku: Stock keeping unit
    
    Returns:
        Tuple with item data or None if not found
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT item_id, sku, name, category, description, quantity, buy_price, sell_price FROM inventory WHERE sku = ?", (sku,))
    row = c.fetchone()
    conn.close()
    return row


def update_inventory_quantity(item_id: int, new_quantity: int) -> bool:
    """
    Update inventory quantity with validation and transaction support.
    
    Args:
        item_id: Item ID
        new_quantity: New quantity (non-negative)
    
    Returns:
        True if successful, False otherwise
    """
    from modules.validators import validate_quantity
    from modules.transaction_manager import transaction
    
    # Validate quantity
    qty_result = validate_quantity(new_quantity)
    if not qty_result.valid:
        print(f"update_inventory_quantity validation error: {qty_result.error_message}")
        return False
    
    new_quantity = qty_result.normalized_value
    
    try:
        with transaction() as conn:
            c = conn.cursor()
            c.execute("UPDATE inventory SET quantity = ? WHERE item_id = ?", (new_quantity, item_id))
            if c.rowcount == 0:
                raise ValueError(f"Item with ID {item_id} not found")
        return True
    except Exception as e:
        print(f"update_inventory_quantity error: {e}")
        return False


def decrease_inventory_quantity(item_id: int, amount: int) -> bool:
    """
    Decrease inventory quantity by a specific amount with validation.
    
    Args:
        item_id: Item ID
        amount: Amount to decrease (positive integer)
    
    Returns:
        True if successful, False otherwise
    """
    from modules.validators import validate_quantity
    from modules.transaction_manager import transaction
    
    # Validate amount
    amount_result = validate_quantity(amount)
    if not amount_result.valid:
        print(f"decrease_inventory_quantity validation error: {amount_result.error_message}")
        return False
    
    amount = amount_result.normalized_value
    
    try:
        with transaction() as conn:
            c = conn.cursor()
            
            # Get current quantity
            c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
            row = c.fetchone()
            if not row:
                raise ValueError(f"Item with ID {item_id} not found")
            
            current_qty = row[0]
            new_qty = current_qty - amount
            
            if new_qty < 0:
                raise ValueError(f"Insufficient inventory: current={current_qty}, requested={amount}")
            
            # Update quantity
            c.execute("UPDATE inventory SET quantity = ? WHERE item_id = ?", (new_qty, item_id))
        
        return True
    except Exception as e:
        print(f"decrease_inventory_quantity error: {e}")
        return False


def delete_inventory_item(item_id: int) -> bool:
    """
    Delete an inventory item from the database.
    
    Args:
        item_id: Item ID to delete
    
    Returns:
        True if successful, False otherwise
    """
    from modules.transaction_manager import transaction
    
    try:
        with transaction() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
            if c.rowcount == 0:
                raise ValueError(f"Item with ID {item_id} not found")
        return True
    except Exception as e:
        print(f"delete_inventory_item error: {e}")
        return False


def check_inventory_availability(item_id: int, required_quantity: int) -> bool:
    """
    Check if sufficient inventory is available.
    
    Args:
        item_id: Item ID
        required_quantity: Required quantity
    
    Returns:
        True if available, False otherwise
    """
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return False
    
    return row[0] >= required_quantity

# ---------------- repairs ----------------
def create_repair_order(order_number: str, customer_name: str, phone: str, model: str, imei: str,
                        problem: str, est_date: str, tech: str, note: str, total_est: float, customer_id: int = None):
    """
    Create a repair order with validation and atomic transaction support.
    
    The repair order and initial history entry are created atomically.
    
    Args:
        order_number: Unique order number
        customer_name: Customer name
        phone: Customer phone number
        model: Device model
        imei: Device IMEI number
        problem: Reported problem description
        est_date: Estimated delivery date
        tech: Technician name
        note: Additional notes
        total_est: Total estimate
        customer_id: Optional customer ID to link repair
    
    Returns:
        repair_id if successful, raises exception otherwise
    """
    from modules.validators import validate_required, validate_phone, validate_price
    from modules.transaction_manager import transaction
    
    # Validate inputs
    order_result = validate_required(order_number, "order_number")
    if not order_result.valid:
        raise ValueError(f"Validation error: {order_result.error_message}")
    
    name_result = validate_required(customer_name, "customer_name")
    if not name_result.valid:
        raise ValueError(f"Validation error: {name_result.error_message}")
    
    phone_result = validate_phone(phone)
    if not phone_result.valid:
        raise ValueError(f"Validation error: {phone_result.error_message}")
    
    model_result = validate_required(model, "device_model")
    if not model_result.valid:
        raise ValueError(f"Validation error: {model_result.error_message}")
    
    problem_result = validate_required(problem, "reported_problem")
    if not problem_result.valid:
        raise ValueError(f"Validation error: {problem_result.error_message}")
    
    tech_result = validate_required(tech, "technician")
    if not tech_result.valid:
        raise ValueError(f"Validation error: {tech_result.error_message}")
    
    est_result = validate_price(total_est)
    if not est_result.valid:
        raise ValueError(f"Validation error: {est_result.error_message}")
    
    # Use normalized values
    phone = phone_result.normalized_value
    total_est = est_result.normalized_value
    
    received = datetime.now().isoformat()
    
    try:
        with transaction() as conn:
            c = conn.cursor()
            
            # Create repair order with customer_id
            c.execute('''INSERT INTO repair_orders
                         (order_number, customer_id, customer_name, customer_phone, device_model, imei, reported_problem, received_date, estimated_delivery, status, technician, total_estimate, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (order_number, customer_id, customer_name, phone, model, imei, problem, received, est_date, 'Received', tech, total_est, note))
            
            rid = c.lastrowid
            
            # Create initial history entry atomically
            action_date = datetime.now().isoformat()
            c.execute('''INSERT INTO repair_history (repair_id, action_date, action_by, status_from, status_to, comment)
                         VALUES (?, ?, ?, ?, ?, ?)''', (rid, action_date, customer_name, None, 'Received', 'Order created'))
        
        return rid
    except Exception as e:
        print(f"create_repair_order error: {e}")
        raise

def get_repairs():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT repair_id, order_number, customer_name, customer_phone, device_model, imei, status, received_date, estimated_delivery FROM repair_orders ORDER BY repair_id DESC")
    rows = c.fetchall(); conn.close()
    return rows

def get_repair_details(repair_id: int):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT * FROM repair_orders WHERE repair_id = ?", (repair_id,))
    order = c.fetchone()
    # Updated to fetch cost_price
    c.execute("SELECT id, part_name, qty, unit_price, cost_price FROM repair_parts WHERE repair_id = ?", (repair_id,))
    parts = c.fetchall()
    c.execute("SELECT history_id, action_date, action_by, status_from, status_to, comment FROM repair_history WHERE repair_id = ? ORDER BY history_id DESC", (repair_id,))
    history = c.fetchall()
    conn.close()
    return order, parts, history

def add_repair_part(repair_id: int, part_name: str, qty: int, unit_price: float, cost_price: float = 0.0) -> bool:
    """
    Add a part to a repair order with validation and automatic total recalculation.
    
    Args:
        repair_id: Repair order ID
        part_name: Part name
        qty: Quantity
        unit_price: Unit price
        cost_price: Cost price
    
    Returns:
        True if successful, False otherwise
    """
    from modules.validators import validate_required, validate_quantity, validate_price
    from modules.transaction_manager import transaction
    
    # Validate inputs
    name_result = validate_required(part_name, "part_name")
    if not name_result.valid:
        print(f"add_repair_part validation error: {name_result.error_message}")
        return False
    
    qty_result = validate_quantity(qty)
    if not qty_result.valid:
        print(f"add_repair_part validation error: {qty_result.error_message}")
        return False
    
    price_result = validate_price(unit_price)
    if not price_result.valid:
        print(f"add_repair_part validation error: {price_result.error_message}")
        return False
    
    cost_result = validate_price(cost_price)
    if not cost_result.valid:
        print(f"add_repair_part validation error: {cost_result.error_message}")
        return False
    
    # Use normalized values
    qty = qty_result.normalized_value
    unit_price = price_result.normalized_value
    cost_price = cost_result.normalized_value
    
    try:
        with transaction() as conn:
            c = conn.cursor()
            
            # Add the part
            c.execute("INSERT INTO repair_parts (repair_id, part_name, qty, unit_price, cost_price) VALUES (?, ?, ?, ?, ?)",
                      (repair_id, part_name, qty, unit_price, cost_price))
            
            # Recalculate and update total_estimate
            c.execute("SELECT SUM(qty * unit_price) FROM repair_parts WHERE repair_id = ?", (repair_id,))
            new_total = c.fetchone()[0] or 0.0
            
            c.execute("UPDATE repair_orders SET total_estimate = ? WHERE repair_id = ?", (new_total, repair_id))
        
        return True
    except Exception as e:
        print(f"add_repair_part error: {e}")
        return False

def add_repair_history(repair_id: int, action_by: str, status_from: str, status_to: str, comment: str = None):
    conn = get_conn(); c = conn.cursor()
    action_date = datetime.now().isoformat()
    try:
        # ensure table exists (db_init normally creates it)
        c.execute('''CREATE TABLE IF NOT EXISTS repair_history (
                        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        repair_id INTEGER,
                        action_date TEXT,
                        action_by TEXT,
                        status_from TEXT,
                        status_to TEXT,
                        comment TEXT
                    )''')
        c.execute('''INSERT INTO repair_history (repair_id, action_date, action_by, status_from, status_to, comment)
                     VALUES (?, ?, ?, ?, ?, ?)''', (repair_id, action_date, action_by, status_from, status_to, comment))
        conn.commit()
    except Exception as e:
        print("add_repair_history error:", e)
    finally:
        conn.close()

def update_repair_status(repair_id: int, new_status: str, action_by: str, comment: str = "") -> bool:
    """
    Update repair status with validation and atomic history logging.
    
    The status update and history entry are created atomically.
    
    Args:
        repair_id: Repair order ID
        new_status: New status
        action_by: User performing the action
        comment: Optional comment
    
    Returns:
        True if successful, False otherwise
    """
    from modules.validators import validate_required
    from modules.transaction_manager import transaction
    
    # Validate inputs
    status_result = validate_required(new_status, "status")
    if not status_result.valid:
        print(f"update_repair_status validation error: {status_result.error_message}")
        return False
    
    user_result = validate_required(action_by, "action_by")
    if not user_result.valid:
        print(f"update_repair_status validation error: {user_result.error_message}")
        return False
    
    try:
        with transaction() as conn:
            c = conn.cursor()
            
            # Get current status
            c.execute("SELECT status FROM repair_orders WHERE repair_id = ?", (repair_id,))
            r = c.fetchone()
            if not r:
                raise ValueError(f"Repair order {repair_id} not found")
            
            old_status = r[0]
            
            # Update status
            c.execute("UPDATE repair_orders SET status = ? WHERE repair_id = ?", (new_status, repair_id))
            
            # Add history entry atomically
            action_date = datetime.now().isoformat()
            c.execute('''INSERT INTO repair_history (repair_id, action_date, action_by, status_from, status_to, comment)
                         VALUES (?, ?, ?, ?, ?, ?)''', (repair_id, action_date, action_by, old_status, new_status, comment))
        
        return True
    except Exception as e:
        print(f"update_repair_status error: {e}")
        return False

def get_repair_parts_total(repair_id: int) -> float:
    conn = get_conn(); c = conn.cursor()
    try:
        c.execute("SELECT SUM(qty * unit_price) FROM repair_parts WHERE repair_id = ?", (repair_id,))
        r = c.fetchone()
        return float(r[0] or 0.0)
    except Exception as e:
        print("get_repair_parts_total error:", e)
        return 0.0
    finally:
        conn.close()

# ---------------- analytics ----------------
def get_dashboard_stats():
    conn = get_conn(); c = conn.cursor()
    stats = {}
    try:
        # 1. Total Repairs
        c.execute("SELECT COUNT(*) FROM repair_orders")
        stats['total_repairs'] = c.fetchone()[0]

        # 2. Pending Repairs (not Completed/Delivered/Cancelled)
        c.execute("SELECT COUNT(*) FROM repair_orders WHERE status NOT IN ('Completed', 'Delivered', 'Cancelled')")
        stats['pending_repairs'] = c.fetchone()[0]

        # 3. Total Revenue from Repairs (Completed/Delivered)
        c.execute("SELECT SUM(total_estimate) FROM repair_orders WHERE status IN ('Completed', 'Delivered')")
        repair_revenue = c.fetchone()[0]
        
        # 4. Total Revenue from Sales
        c.execute("SELECT SUM(total_amount) FROM sales")
        sales_revenue = c.fetchone()[0]
        
        # Combined revenue
        stats['total_revenue'] = float(repair_revenue or 0.0) + float(sales_revenue or 0.0)
        stats['repair_revenue'] = float(repair_revenue or 0.0)
        stats['sales_revenue'] = float(sales_revenue or 0.0)

        # 5. Total Profit from Sales (revenue - cost)
        c.execute("""
            SELECT SUM(si.quantity * (si.unit_price - si.cost_price))
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.sale_id
        """)
        sales_profit = c.fetchone()[0]
        stats['sales_profit'] = float(sales_profit or 0.0)

        # 6. Low Stock Items (qty < 5)
        c.execute("SELECT COUNT(*) FROM inventory WHERE quantity < 5")
        stats['low_stock'] = c.fetchone()[0]

        # 7. Overdue Repairs
        today = datetime.now().isoformat()[:10]
        c.execute("SELECT COUNT(*) FROM repair_orders WHERE status NOT IN ('Completed','Delivered','Cancelled') AND estimated_delivery < ?", (today,))
        stats['overdue_count'] = c.fetchone()[0]

        # 8. Recent Repairs (last 10 with full details)
        c.execute("""
            SELECT order_number, customer_name, device_model, status, received_date, total_estimate
            FROM repair_orders 
            ORDER BY repair_id DESC 
            LIMIT 10
        """)
        stats['recent_repairs'] = c.fetchall()

    except Exception as e:
        print("get_dashboard_stats error:", e)
        import traceback
        traceback.print_exc()
        stats = {
            'total_repairs': 0, 
            'pending_repairs': 0, 
            'total_revenue': 0.0,
            'repair_revenue': 0.0,
            'sales_revenue': 0.0,
            'sales_profit': 0.0,
            'low_stock': 0, 
            'overdue_count': 0,
            'recent_repairs': []
        }
    finally:
        conn.close()
    return stats

def get_daily_sales_total():
    """Get total sales for today."""
    conn = get_conn(); c = conn.cursor()
    today = datetime.now().isoformat()[:10]
    try:
        c.execute("SELECT SUM(total_amount) FROM sales WHERE sale_date LIKE ?", (f"{today}%",))
        result = c.fetchone()[0]
        return float(result or 0.0)
    except Exception as e:
        print("get_daily_sales_total error:", e)
        return 0.0
    finally:
        conn.close()

def get_repair_distribution():
    """Get top 5 device models for repair distribution pie chart."""
    conn = get_conn(); c = conn.cursor()
    try:
        c.execute("""
            SELECT device_model, COUNT(*) as count 
            FROM repair_orders 
            GROUP BY device_model 
            ORDER BY count DESC 
            LIMIT 5
        """)
        return c.fetchall()
    except Exception as e:
        print("get_repair_distribution error:", e)
        return []
    finally:
        conn.close()

def get_top_selling_items():
    """Get top 5 selling items with quantity, revenue, and profit."""
    conn = get_conn(); c = conn.cursor()
    try:
        c.execute("""
            SELECT 
                i.name, 
                SUM(si.quantity) as total_sold,
                SUM(si.quantity * si.unit_price) as revenue,
                SUM(si.quantity * (si.unit_price - si.cost_price)) as profit
            FROM sale_items si
            JOIN inventory i ON si.item_id = i.item_id
            GROUP BY si.item_id
            ORDER BY total_sold DESC
            LIMIT 5
        """)
        return c.fetchall()
    except Exception as e:
        print("get_top_selling_items error:", e)
        return []
    finally:
        conn.close()

# ---------------- CRM & Advanced ----------------
def get_customer_history(phone: str):
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT repair_id, order_number, device_model, status, received_date, total_estimate
                 FROM repair_orders WHERE customer_phone LIKE ? ORDER BY received_date DESC""", (f"%{phone}%",))
    rows = c.fetchall(); conn.close()
    return rows

# ===================== CUSTOMER MANAGEMENT =====================

def get_or_create_customer(name, phone, email=None, address=None, customer_type='Both'):
    """Get existing customer or create new one. Returns customer_id."""
    conn = get_conn(); c = conn.cursor()
    
    # Try to find by phone first (most reliable)
    if phone:
        c.execute("SELECT customer_id FROM customers WHERE phone = ?", (phone,))
        result = c.fetchone()
        if result:
            customer_id = result[0]
            # Update customer info
            c.execute("""UPDATE customers 
                        SET name = ?, email = ?, address = ?, customer_type = ?
                        WHERE customer_id = ?""",
                     (name, email, address, customer_type, customer_id))
            conn.commit(); conn.close()
            return customer_id
    
    # Create new customer
    from datetime import datetime
    now = datetime.now().isoformat()
    c.execute("""INSERT INTO customers 
                (name, phone, email, address, customer_type, created_date)
                VALUES (?, ?, ?, ?, ?, ?)""",
             (name, phone, email, address, customer_type, now))
    customer_id = c.lastrowid
    conn.commit(); conn.close()
    return customer_id


def update_customer_purchase(customer_id, amount):
    """Update customer purchase statistics"""
    conn = get_conn(); c = conn.cursor()
    from datetime import datetime
    now = datetime.now().isoformat()
    c.execute("""UPDATE customers 
                SET total_purchases = total_purchases + 1,
                    total_spent = total_spent + ?,
                    last_purchase_date = ?
                WHERE customer_id = ?""",
             (amount, now, customer_id))
    conn.commit(); conn.close()


def update_customer_repair(customer_id):
    """Update customer repair statistics"""
    conn = get_conn(); c = conn.cursor()
    from datetime import datetime
    now = datetime.now().isoformat()
    c.execute("""UPDATE customers 
                SET total_repairs = total_repairs + 1,
                    last_repair_date = ?
                WHERE customer_id = ?""",
             (now, customer_id))
    conn.commit(); conn.close()


def get_all_customers():
    """Get list of all customers from customers table"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT customer_id, name, phone, email, address, customer_type,
                 total_purchases, total_repairs, total_spent,
                 last_purchase_date, last_repair_date, created_date
                 FROM customers 
                 ORDER BY created_date DESC""")
    rows = c.fetchall(); conn.close()
    return rows


def search_customer_by_phone(phone):
    """Search for customer by phone number"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT customer_id, name, phone, email, address, customer_type,
                 total_purchases, total_repairs, total_spent
                 FROM customers 
                 WHERE phone LIKE ?""", (f"%{phone}%",))
    result = c.fetchone(); conn.close()
    return result


def get_customer_details(customer_id):
    """Get detailed customer information"""
    conn = get_conn(); c = conn.cursor()
    c.execute("""SELECT * FROM customers WHERE customer_id = ?""", (customer_id,))
    result = c.fetchone(); conn.close()
    return result

def get_item_cost(name_or_sku: str) -> float:
    """Try to find cost price from inventory based on name or SKU."""
    conn = get_conn(); c = conn.cursor()
    # Try exact match on SKU first
    c.execute("SELECT buy_price FROM inventory WHERE sku = ?", (name_or_sku,))
    r = c.fetchone()
    if not r:
        # Try exact match on Name
        c.execute("SELECT buy_price FROM inventory WHERE name = ?", (name_or_sku,))
        r = c.fetchone()
    conn.close()
    return float(r[0]) if r else 0.0

def get_profit_stats():
    conn = get_conn(); c = conn.cursor()
    stats = {'revenue': 0.0, 'cost': 0.0, 'profit': 0.0}
    try:
        # Revenue from Completed/Delivered
        c.execute("SELECT SUM(total_estimate) FROM repair_orders WHERE status IN ('Completed', 'Delivered')")
        rev = c.fetchone()[0]
        stats['revenue'] = float(rev or 0.0)

        # Cost from parts used in those repairs
        # We need to join repair_parts with repair_orders
        c.execute('''
            SELECT SUM(p.qty * p.cost_price)
            FROM repair_parts p
            JOIN repair_orders o ON p.repair_id = o.repair_id
            WHERE o.status IN ('Completed', 'Delivered')
        ''')
        cost = c.fetchone()[0]
        stats['cost'] = float(cost or 0.0)
        stats['profit'] = stats['revenue'] - stats['cost']
    except Exception as e:
        print("get_profit_stats error:", e)
    finally:
        conn.close()
    return stats

# ---------------- Sales (POS) ----------------
def create_sale(customer_name: str, items: list, customer_id: int = None) -> int:
    """
    Create a sale with validation and atomic transaction support.
    
    All operations (sale creation, item insertion, inventory updates) are
    performed atomically - either all succeed or all are rolled back.
    
    Args:
        customer_name: Customer name
        items: List of tuples (item_id, qty, unit_price, cost_price)
        customer_id: Optional customer ID to link sale
    
    Returns:
        sale_id if successful, None otherwise
    """
    from modules.validators import validate_required, validate_quantity, validate_price
    from modules.transaction_manager import transaction
    
    # Validate customer name
    name_result = validate_required(customer_name, "customer_name")
    if not name_result.valid:
        print(f"create_sale validation error: {name_result.error_message}")
        return None
    
    # Validate items list
    if not items or len(items) == 0:
        print("create_sale validation error: items list cannot be empty")
        return None
    
    # Validate each item
    for item_id, qty, unit_price, cost_price in items:
        qty_result = validate_quantity(qty)
        if not qty_result.valid:
            print(f"create_sale validation error for item {item_id}: {qty_result.error_message}")
            return None
        
        price_result = validate_price(unit_price)
        if not price_result.valid:
            print(f"create_sale validation error for item {item_id}: {price_result.error_message}")
            return None
        
        cost_result = validate_price(cost_price)
        if not cost_result.valid:
            print(f"create_sale validation error for item {item_id}: {cost_result.error_message}")
            return None
    
    # Calculate total
    total_amount = sum([i[1] * i[2] for i in items])
    date_str = datetime.now().isoformat()
    
    try:
        with transaction() as conn:
            c = conn.cursor()
            
            # Check inventory availability for all items BEFORE making any changes
            for item_id, qty, unit_price, cost_price in items:
                c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
                row = c.fetchone()
                if not row:
                    raise ValueError(f"Item with ID {item_id} not found")
                
                available_qty = row[0]
                if available_qty < qty:
                    raise ValueError(f"Insufficient inventory for item {item_id}: available={available_qty}, requested={qty}")
            
            # All checks passed, now perform the sale
            # Create sale record with customer_id
            c.execute("INSERT INTO sales (sale_date, customer_id, customer_name, total_amount) VALUES (?, ?, ?, ?)",
                      (date_str, customer_id, customer_name, total_amount))
            sale_id = c.lastrowid
            
            # Add items and update inventory
            for item_id, qty, unit_price, cost_price in items:
                c.execute("INSERT INTO sale_items (sale_id, item_id, quantity, unit_price, cost_price) VALUES (?, ?, ?, ?, ?)",
                          (sale_id, item_id, qty, unit_price, cost_price))
                c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?",
                          (qty, item_id))
        
        return sale_id
    except ValueError as ve:
        print(f"create_sale validation error: {ve}")
        return None
    except Exception as e:
        print(f"create_sale error: {e}")
        return None


def create_sale_detailed(customer_name: str, customer_id: int, customer_phone: str, customer_email: str,
                        customer_address: str, items: list, subtotal: float, discount_percent: float,
                        discount_amount: float, total_amount: float, seller_name: str = "System",
                        payment_method: str = "Cash", notes: str = None) -> int:
    """
    Create a comprehensive sale record with all details for reporting.
    
    Args:
        customer_name: Customer name
        customer_id: Customer ID (can be None)
        customer_phone: Customer phone
        customer_email: Customer email
        customer_address: Customer address
        items: List of dicts with keys: id, sku, name, category, qty, price, cost
        subtotal: Subtotal before discount
        discount_percent: Discount percentage
        discount_amount: Discount amount in currency
        total_amount: Final total after discount
        seller_name: Name of seller
        payment_method: Payment method
        notes: Additional notes
    
    Returns:
        sale_id if successful, None otherwise
    """
    from modules.transaction_manager import transaction
    from datetime import datetime
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    time_str = datetime.now().strftime("%H:%M:%S")
    
    try:
        with transaction() as conn:
            c = conn.cursor()
            
            # Check inventory availability for all items BEFORE making any changes
            for item in items:
                item_id = item['id']
                qty = item['qty']
                
                c.execute("SELECT quantity FROM inventory WHERE item_id = ?", (item_id,))
                row = c.fetchone()
                if not row:
                    raise ValueError(f"Item with ID {item_id} not found")
                
                available_qty = row[0]
                if available_qty < qty:
                    raise ValueError(f"Insufficient inventory for item {item_id}: available={available_qty}, requested={qty}")
            
            # Create comprehensive sale record
            c.execute("""
                INSERT INTO sales (
                    sale_date, sale_time, customer_id, customer_name, customer_phone,
                    customer_email, customer_address, subtotal, discount_percent,
                    discount_amount, total_amount, seller_name, payment_method, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (date_str, time_str, customer_id, customer_name, customer_phone,
                  customer_email, customer_address, subtotal, discount_percent,
                  discount_amount, total_amount, seller_name, payment_method, notes))
            
            sale_id = c.lastrowid
            
            # Add detailed sale items and update inventory
            for item in items:
                item_id = item['id']
                sku = item['sku']
                name = item['name']
                category = item.get('category', 'Unknown')
                qty = item['qty']
                unit_price = item['price']
                cost_price = item['cost']
                line_total = qty * unit_price
                profit = (unit_price - cost_price) * qty
                
                c.execute("""
                    INSERT INTO sale_items (
                        sale_id, item_id, item_sku, item_name, item_category,
                        quantity, unit_price, cost_price, line_total, profit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (sale_id, item_id, sku, name, category, qty, unit_price, cost_price, line_total, profit))
                
                # Update inventory
                c.execute("UPDATE inventory SET quantity = quantity - ? WHERE item_id = ?", (qty, item_id))
        
        return sale_id
    
    except ValueError as ve:
        print(f"create_sale_detailed validation error: {ve}")
        return None
    except Exception as e:
        print(f"create_sale_detailed error: {e}")
        return None
    except Exception as e:
        print(f"create_sale error: {e}")
        return None

def get_sales_history():
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT sale_id, sale_date, customer_name, total_amount FROM sales ORDER BY sale_date DESC")
    rows = c.fetchall(); conn.close()
    return rows

def get_sale_details(sale_id: int):
    conn = get_conn(); c = conn.cursor()
    c.execute("SELECT sale_id, sale_date, customer_name, total_amount FROM sales WHERE sale_id = ?", (sale_id,))
    sale_info = c.fetchone()
    c.execute('''SELECT si.item_id, i.sku, i.name, si.quantity, si.unit_price, si.cost_price 
                 FROM sale_items si JOIN inventory i ON si.item_id = i.item_id 
                 WHERE si.sale_id = ?''', (sale_id,))
    sale_items = c.fetchall()
    conn.close()
    return sale_info, sale_items

# --- Schema Check ---
def check_schema():
    conn = get_conn(); c = conn.cursor()
    try:
        def get_columns(table_name: str):
            c.execute(f"PRAGMA table_info({table_name})")
            return [col[1] for col in c.fetchall()]

        def rename_column(table_name: str, old: str, new: str):
            try:
                c.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old} TO {new}")
            except Exception as err:
                print(f"rename_column {table_name}.{old}->{new} failed:", err)

        # Check for 'cost_price' in repair_parts
        cols = get_columns("repair_parts")
        if 'cost_price' not in cols:
            print("Migrating: Adding cost_price to repair_parts")
            c.execute("ALTER TABLE repair_parts ADD COLUMN cost_price REAL DEFAULT 0.0")
        
        # Check for 'cost_price' in sale_items
        sale_item_cols = get_columns("sale_items")
        if 'cost_price' not in sale_item_cols:
            print("Migrating: Adding cost_price to sale_items")
            c.execute("ALTER TABLE sale_items ADD COLUMN cost_price REAL DEFAULT 0.0")

        # Ensure quantity/unit_price column names align with code
        sale_item_cols = get_columns("sale_items")
        if 'quantity' not in sale_item_cols:
            if 'qty' in sale_item_cols:
                print("Migrating: Renaming sale_items.qty -> quantity")
                rename_column("sale_items", "qty", "quantity")
            else:
                print("Migrating: Adding quantity to sale_items")
                c.execute("ALTER TABLE sale_items ADD COLUMN quantity INTEGER DEFAULT 0")

        sale_item_cols = get_columns("sale_items")
        if 'unit_price' not in sale_item_cols:
            if 'price' in sale_item_cols:
                print("Migrating: Renaming sale_items.price -> unit_price")
                rename_column("sale_items", "price", "unit_price")
            else:
                print("Migrating: Adding unit_price to sale_items")
                c.execute("ALTER TABLE sale_items ADD COLUMN unit_price REAL DEFAULT 0.0")

        # Ensure sales table includes customer_name & total_amount
        sales_cols = get_columns("sales")
        if 'customer_name' not in sales_cols:
            print("Migrating: Adding customer_name to sales")
            c.execute("ALTER TABLE sales ADD COLUMN customer_name TEXT")

        sales_cols = get_columns("sales")
        if 'total_amount' not in sales_cols:
            if 'total' in sales_cols:
                print("Migrating: Renaming sales.total -> total_amount")
                rename_column("sales", "total", "total_amount")
            else:
                print("Migrating: Adding total_amount to sales")
                c.execute("ALTER TABLE sales ADD COLUMN total_amount REAL DEFAULT 0.0")

        # Check for 'category' in inventory
        inv_cols = get_columns("inventory")
        if 'category' not in inv_cols:
            print("Migrating: Adding category to inventory")
            c.execute("ALTER TABLE inventory ADD COLUMN category TEXT DEFAULT 'General'")
        
        conn.commit()
    except Exception as e:
        print("Schema check error:", e)
    finally:
        conn.close()

# Run schema check on import
check_schema()
