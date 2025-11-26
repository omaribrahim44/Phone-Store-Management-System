# -*- coding: utf-8 -*-
# modules/security.py
"""
Security utilities for the Phone Management System.

Provides secure password hashing using bcrypt, password strength validation,
and secure password verification with constant-time comparison.
"""

import bcrypt
from typing import Tuple
from modules.validators import validate_password, ValidationResult


def hash_password_secure(plain: str) -> str:
    """
    Hash a password securely using bcrypt.
    
    Bcrypt automatically:
    - Generates a unique salt per password
    - Uses adaptive hashing (computationally expensive)
    - Provides protection against rainbow tables
    
    Args:
        plain: Plain text password
    
    Returns:
        Bcrypt hash string (includes salt)
    
    Raises:
        ValueError: If password is invalid
    """
    # Validate password first
    result = validate_password(plain)
    if not result.valid:
        raise ValueError(f"Password validation failed: {result.error_message}")
    
    # Generate salt and hash
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds = good security/performance balance
    hashed = bcrypt.hashpw(plain.encode('utf-8'), salt)
    
    return hashed.decode('utf-8')


def verify_password_secure(stored_hash: str, plain: str) -> bool:
    """
    Verify a password against stored bcrypt hash.
    
    Uses constant-time comparison to prevent timing attacks.
    
    Args:
        stored_hash: Stored bcrypt hash
        plain: Plain text password to verify
    
    Returns:
        True if password matches, False otherwise
    """
    try:
        return bcrypt.checkpw(plain.encode('utf-8'), stored_hash.encode('utf-8'))
    except Exception:
        return False


def check_password_strength(password: str) -> Tuple[bool, str, int]:
    """
    Check password strength and provide feedback.
    
    Args:
        password: Password to check
    
    Returns:
        Tuple of (is_strong, feedback_message, strength_score)
        strength_score: 0-100
    """
    result = validate_password(password)
    
    if not result.valid:
        return (False, result.error_message, 0)
    
    # Calculate strength score
    score = 0
    
    # Length bonus
    if len(password) >= 8:
        score += 20
    if len(password) >= 12:
        score += 10
    if len(password) >= 16:
        score += 10
    
    # Character variety
    if any(c.isupper() for c in password):
        score += 15
    if any(c.islower() for c in password):
        score += 15
    if any(c.isdigit() for c in password):
        score += 15
    if any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
        score += 15
    
    # Determine strength
    if score >= 80:
        return (True, "Strong password", score)
    elif score >= 60:
        return (True, "Good password", score)
    else:
        return (True, "Acceptable password", score)


def migrate_password_to_bcrypt(user_id: int, old_hash: str, new_plain: str = None) -> bool:
    """
    Migrate a user's password from old hashing to bcrypt.
    
    This is a utility function for one-time migration.
    If new_plain is provided, it will be hashed with bcrypt.
    Otherwise, user must reset their password.
    
    Args:
        user_id: User ID to migrate
        old_hash: Old password hash
        new_plain: Optional new plain password
    
    Returns:
        True if migration successful
    """
    from modules.db import get_conn
    from modules.transaction_manager import transaction
    
    if new_plain is None:
        # Mark user as needing password reset
        try:
            with transaction() as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET password = ?, needs_reset = 1 WHERE user_id = ?",
                         ("RESET_REQUIRED", user_id))
            return True
        except Exception as e:
            print(f"migrate_password_to_bcrypt error: {e}")
            return False
    else:
        # Hash new password with bcrypt
        try:
            new_hash = hash_password_secure(new_plain)
            with transaction() as conn:
                c = conn.cursor()
                c.execute("UPDATE users SET password = ? WHERE user_id = ?",
                         (new_hash, user_id))
            return True
        except Exception as e:
            print(f"migrate_password_to_bcrypt error: {e}")
            return False
