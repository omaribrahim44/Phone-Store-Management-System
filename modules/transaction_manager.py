# modules/transaction_manager.py
"""
Transaction management utilities for ensuring atomic database operations.

This module provides context managers and decorators for wrapping database
operations in transactions with automatic commit/rollback.
"""

from contextlib import contextmanager
from functools import wraps
from typing import Callable, Any
import sqlite3
from modules.db import get_conn
from modules.logger import log


@contextmanager
def transaction():
    """
    Context manager for database transactions with automatic commit/rollback.
    
    Usage:
        with transaction() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO ...")
            cursor.execute("UPDATE ...")
            # Automatically commits on success, rolls back on exception
    
    Yields:
        sqlite3.Connection: Database connection
    
    Raises:
        Exception: Re-raises any exception after rollback
    """
    conn = get_conn()
    try:
        yield conn
        conn.commit()
        log.debug("Transaction committed successfully")
    except Exception as e:
        conn.rollback()
        log.error(f"Transaction rolled back due to error: {e}")
        raise
    finally:
        conn.close()


def transactional(func: Callable) -> Callable:
    """
    Decorator to wrap a function in a database transaction.
    
    The decorated function will receive a 'conn' parameter with the database
    connection. All database operations should use this connection.
    
    Usage:
        @transactional
        def create_sale(conn, customer_name, items):
            cursor = conn.cursor()
            cursor.execute("INSERT INTO sales ...")
            for item in items:
                cursor.execute("INSERT INTO sale_items ...")
    
    Args:
        func: Function to wrap in transaction
    
    Returns:
        Wrapped function with transaction management
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        with transaction() as conn:
            # Inject connection as first argument
            return func(conn, *args, **kwargs)
    
    return wrapper


def execute_in_transaction(func: Callable, *args, **kwargs) -> Any:
    """
    Execute a function within a transaction context.
    
    This is useful when you can't use the decorator (e.g., lambda functions,
    or when you need more control over the transaction).
    
    Args:
        func: Function to execute (should accept conn as first parameter)
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func
    
    Returns:
        Result of func execution
    
    Raises:
        Exception: Re-raises any exception after rollback
    """
    with transaction() as conn:
        return func(conn, *args, **kwargs)


@contextmanager
def rollback_on_error(conn: sqlite3.Connection):
    """
    Context manager for explicit rollback handling.
    
    Use this when you already have a connection and want to ensure
    rollback on error without committing.
    
    Usage:
        conn = get_conn()
        try:
            with rollback_on_error(conn):
                cursor = conn.cursor()
                cursor.execute("INSERT ...")
                # Will rollback on exception
            conn.commit()  # Explicit commit
        finally:
            conn.close()
    
    Args:
        conn: Existing database connection
    
    Yields:
        The same connection
    """
    try:
        yield conn
    except Exception as e:
        conn.rollback()
        log.error(f"Rolled back due to error: {e}")
        raise


class TransactionContext:
    """
    Class-based transaction context for more complex scenarios.
    
    Provides explicit control over transaction lifecycle with
    savepoints for nested transactions.
    """
    
    def __init__(self):
        self.conn = None
        self.savepoint_counter = 0
    
    def __enter__(self):
        self.conn = get_conn()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
            log.error(f"Transaction rolled back: {exc_val}")
        else:
            self.conn.commit()
            log.debug("Transaction committed")
        
        self.conn.close()
        return False  # Don't suppress exceptions
    
    def cursor(self):
        """Get a cursor for the transaction connection"""
        if self.conn is None:
            raise RuntimeError("Transaction not started. Use 'with' statement.")
        return self.conn.cursor()
    
    def savepoint(self, name: str = None):
        """
        Create a savepoint for nested transaction support.
        
        Args:
            name: Optional savepoint name (auto-generated if not provided)
        
        Returns:
            Savepoint name
        """
        if name is None:
            self.savepoint_counter += 1
            name = f"sp_{self.savepoint_counter}"
        
        cursor = self.cursor()
        cursor.execute(f"SAVEPOINT {name}")
        log.debug(f"Created savepoint: {name}")
        return name
    
    def rollback_to_savepoint(self, name: str):
        """
        Rollback to a specific savepoint.
        
        Args:
            name: Savepoint name to rollback to
        """
        cursor = self.cursor()
        cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")
        log.debug(f"Rolled back to savepoint: {name}")
    
    def release_savepoint(self, name: str):
        """
        Release a savepoint (commit nested transaction).
        
        Args:
            name: Savepoint name to release
        """
        cursor = self.cursor()
        cursor.execute(f"RELEASE SAVEPOINT {name}")
        log.debug(f"Released savepoint: {name}")


# ==================== Helper Functions ====================

def verify_transaction_state(conn: sqlite3.Connection) -> bool:
    """
    Verify that a connection is in a valid transaction state.
    
    Args:
        conn: Database connection to check
    
    Returns:
        True if in transaction, False otherwise
    """
    try:
        # Check if we're in a transaction by trying to get autocommit status
        return conn.in_transaction
    except AttributeError:
        # Fallback for older sqlite3 versions
        return True


def get_transaction_isolation_level(conn: sqlite3.Connection) -> str:
    """
    Get the current transaction isolation level.
    
    Args:
        conn: Database connection
    
    Returns:
        Isolation level string
    """
    return conn.isolation_level or "DEFERRED"


def set_transaction_isolation_level(conn: sqlite3.Connection, level: str):
    """
    Set the transaction isolation level.
    
    SQLite supports: DEFERRED, IMMEDIATE, EXCLUSIVE
    
    Args:
        conn: Database connection
        level: Isolation level ('DEFERRED', 'IMMEDIATE', or 'EXCLUSIVE')
    """
    valid_levels = ['DEFERRED', 'IMMEDIATE', 'EXCLUSIVE']
    if level.upper() not in valid_levels:
        raise ValueError(f"Invalid isolation level: {level}. Must be one of {valid_levels}")
    
    conn.isolation_level = level
    log.debug(f"Set transaction isolation level to: {level}")
