# modules/audit_logger.py
import sqlite3
from datetime import datetime
from modules.logger import log
import config

def get_conn():
    return sqlite3.connect(config.DB_PATH)

def log_action(user, action_type, entity_type, entity_id=None, description="", old_value=None, new_value=None):
    """
    Log an audit event to the database.
    
    Args:
        user: Username performing the action
        action_type: Type of action (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, STATUS_CHANGE, PRINT, EXPORT)
        entity_type: Type of entity (repair, sale, inventory, user, customer)
        entity_id: ID of the entity being acted upon
        description: Human-readable description of the action
        old_value: Previous value (for updates)
        new_value: New value (for updates)
    """
    conn = get_conn()
    c = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    try:
        c.execute('''
            INSERT INTO audit_logs (timestamp, user, action_type, entity_type, entity_id, old_value, new_value, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, user, action_type, entity_type, entity_id, old_value, new_value, description))
        
        conn.commit()
        log.info(f"Audit: {user} - {action_type} {entity_type} #{entity_id}: {description}")
    except Exception as e:
        log.error(f"Failed to log audit event: {e}")
    finally:
        conn.close()

def get_logs(limit=100, user=None, action_type=None, entity_type=None, start_date=None, end_date=None):
    """
    Retrieve audit logs with optional filtering.
    
    Returns: List of tuples (log_id, timestamp, user, action_type, entity_type, entity_id, old_value, new_value, description)
    """
    conn = get_conn()
    c = conn.cursor()
    
    query = "SELECT * FROM audit_logs WHERE 1=1"
    params = []
    
    if user:
        query += " AND user = ?"
        params.append(user)
    
    if action_type:
        query += " AND action_type = ?"
        params.append(action_type)
    
    if entity_type:
        query += " AND entity_type = ?"
        params.append(entity_type)
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    
    query += f" ORDER BY timestamp DESC LIMIT {limit}"
    
    c.execute(query, params)
    rows = c.fetchall()
    conn.close()
    
    return rows

def get_entity_history(entity_type, entity_id):
    """
    Get all audit logs for a specific entity.
    
    Returns: List of tuples (log_id, timestamp, user, action_type, entity_type, entity_id, old_value, new_value, description)
    """
    conn = get_conn()
    c = conn.cursor()
    
    c.execute('''
        SELECT * FROM audit_logs 
        WHERE entity_type = ? AND entity_id = ?
        ORDER BY timestamp DESC
    ''', (entity_type, entity_id))
    
    rows = c.fetchall()
    conn.close()
    
    return rows

def clear_old_logs(days=90):
    """
    Delete audit logs older than specified days.
    """
    conn = get_conn()
    c = conn.cursor()
    
    cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_date = cutoff_date.replace(day=cutoff_date.day - days).isoformat()
    
    try:
        c.execute("DELETE FROM audit_logs WHERE timestamp < ?", (cutoff_date,))
        deleted = c.rowcount
        conn.commit()
        log.info(f"Cleared {deleted} old audit logs (older than {days} days)")
        return deleted
    except Exception as e:
        log.error(f"Failed to clear old logs: {e}")
        return 0
    finally:
        conn.close()
