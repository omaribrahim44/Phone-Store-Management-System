# modules/validators.py
"""
Validation utilities for all input data in the Phone Management System
"""

from dataclasses import dataclass
from typing import Any, Optional
import re
import string

def validate_imei(imei: str) -> bool:
    """
    Validate IMEI number using Luhn algorithm (checksum validation)
    IMEI should be 15 digits
    """
    if not imei:
        return False
    
    # Remove any spaces or dashes
    imei = imei.replace(" ", "").replace("-", "")
    
    # Check if it's 15 digits
    if not imei.isdigit() or len(imei) != 15:
        return False
    
    # Luhn algorithm for checksum validation
    def luhn_checksum(number):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(number)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    return luhn_checksum(imei) == 0

def validate_barcode(barcode: str, barcode_type: str = "any") -> bool:
    """
    Validate barcode based on type
    Supports: EAN-13, UPC-A, Code-128, or any
    """
    if not barcode:
        return False
    
    barcode = barcode.strip()
    
    if barcode_type == "EAN-13":
        return barcode.isdigit() and len(barcode) == 13
    elif barcode_type == "UPC-A":
        return barcode.isdigit() and len(barcode) == 12
    elif barcode_type == "Code-128":
        # Code-128 can be alphanumeric
        return len(barcode) > 0 and len(barcode) <= 128
    else:  # any
        # Accept any non-empty barcode
        return len(barcode) > 0 and len(barcode) <= 50

def format_imei(imei: str) -> str:
    """Format IMEI with spaces for readability: XXX XXX XXX XXX XXX"""
    if not imei:
        return ""
    
    imei = imei.replace(" ", "").replace("-", "")
    if len(imei) == 15:
        return f"{imei[0:3]} {imei[3:6]} {imei[6:9]} {imei[9:12]} {imei[12:15]}"
    return imei

def clean_barcode(barcode: str) -> str:
    """Clean barcode by removing whitespace and special characters"""
    if not barcode:
        return ""
    return barcode.strip().upper()


# ==================== Validation Result ====================

@dataclass
class ValidationResult:
    """Result of a validation operation"""
    valid: bool
    normalized_value: Any
    error_message: Optional[str] = None
    
    @staticmethod
    def success(normalized_value: Any) -> 'ValidationResult':
        """Create a successful validation result"""
        return ValidationResult(valid=True, normalized_value=normalized_value, error_message=None)
    
    @staticmethod
    def failure(error_message: str, original_value: Any = None) -> 'ValidationResult':
        """Create a failed validation result"""
        return ValidationResult(valid=False, normalized_value=original_value, error_message=error_message)


# ==================== Price Validation ====================

def validate_price(value: Any) -> ValidationResult:
    """
    Validate that a price is non-negative and reasonable.
    
    Args:
        value: The price value to validate (can be float, int, or string)
    
    Returns:
        ValidationResult with normalized float value or error
    """
    try:
        price = float(value)
    except (ValueError, TypeError):
        return ValidationResult.failure(f"Invalid price format: {value}", value)
    
    if price < 0:
        return ValidationResult.failure(f"Price cannot be negative: {price}", value)
    
    if price > 10_000_000:  # Reasonable upper limit
        return ValidationResult.failure(f"Price exceeds reasonable limit: {price}", value)
    
    # Round to 2 decimal places
    normalized = round(price, 2)
    return ValidationResult.success(normalized)


# ==================== Quantity Validation ====================

def validate_quantity(value: Any) -> ValidationResult:
    """
    Validate that a quantity is a non-negative integer.
    
    Args:
        value: The quantity value to validate
    
    Returns:
        ValidationResult with normalized int value or error
    """
    try:
        quantity = int(value)
    except (ValueError, TypeError):
        return ValidationResult.failure(f"Invalid quantity format: {value}", value)
    
    if quantity < 0:
        return ValidationResult.failure(f"Quantity cannot be negative: {quantity}", value)
    
    if quantity > 1_000_000:  # Reasonable upper limit
        return ValidationResult.failure(f"Quantity exceeds reasonable limit: {quantity}", value)
    
    return ValidationResult.success(quantity)


# ==================== Phone Number Validation ====================

def validate_phone(phone: str) -> ValidationResult:
    """
    Validate and normalize phone number.
    Accepts various formats and normalizes to digits only.
    
    Valid formats:
    - 1234567890 (10 digits)
    - 12345678901 (11 digits)
    - 123-456-7890
    - (123) 456-7890
    - +1 123-456-7890
    
    Args:
        phone: Phone number string
    
    Returns:
        ValidationResult with normalized phone (digits only) or error
    """
    if not phone or not isinstance(phone, str):
        return ValidationResult.failure("Phone number is required", phone)
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check length (10-15 digits is reasonable)
    if len(digits_only) < 10:
        return ValidationResult.failure(f"Phone number too short: {phone}", phone)
    
    if len(digits_only) > 15:
        return ValidationResult.failure(f"Phone number too long: {phone}", phone)
    
    # Normalize to digits only
    return ValidationResult.success(digits_only)


# ==================== SKU Validation ====================

def validate_sku(sku: str, check_unique: bool = False, existing_skus: set = None) -> ValidationResult:
    """
    Validate SKU (Stock Keeping Unit).
    
    Rules:
    - Must be non-empty
    - 3-20 characters
    - Alphanumeric with hyphens allowed
    - Cannot start or end with hyphen
    - Optionally check uniqueness
    
    Args:
        sku: SKU string
        check_unique: Whether to check if SKU already exists
        existing_skus: Set of existing SKUs (required if check_unique=True)
    
    Returns:
        ValidationResult with normalized SKU or error
    """
    if not sku or not isinstance(sku, str):
        return ValidationResult.failure("SKU is required", sku)
    
    sku = sku.strip().upper()
    
    if len(sku) < 3:
        return ValidationResult.failure(f"SKU too short (minimum 3 characters): {sku}", sku)
    
    if len(sku) > 20:
        return ValidationResult.failure(f"SKU too long (maximum 20 characters): {sku}", sku)
    
    # Check valid characters (alphanumeric + hyphen)
    if not re.match(r'^[A-Z0-9-]+$', sku):
        return ValidationResult.failure(f"SKU contains invalid characters: {sku}", sku)
    
    # Cannot start or end with hyphen
    if sku.startswith('-') or sku.endswith('-'):
        return ValidationResult.failure(f"SKU cannot start or end with hyphen: {sku}", sku)
    
    # Check uniqueness if requested
    if check_unique and existing_skus is not None:
        if sku in existing_skus:
            return ValidationResult.failure(f"SKU already exists: {sku}", sku)
    
    return ValidationResult.success(sku)


# ==================== Password Validation ====================

def validate_password(password: str, min_length: int = 8) -> ValidationResult:
    """
    Validate password complexity.
    
    Requirements:
    - Minimum length (default 8)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (!@#$%^&*)
    
    Args:
        password: Password string
        min_length: Minimum password length
    
    Returns:
        ValidationResult with password or error
    """
    if not password or not isinstance(password, str):
        return ValidationResult.failure("Password is required", password)
    
    if len(password) < min_length:
        return ValidationResult.failure(
            f"Password must be at least {min_length} characters long",
            password
        )
    
    if len(password) > 128:
        return ValidationResult.failure("Password too long (maximum 128 characters)", password)
    
    # Check for uppercase
    if not any(c.isupper() for c in password):
        return ValidationResult.failure("Password must contain at least one uppercase letter", password)
    
    # Check for lowercase
    if not any(c.islower() for c in password):
        return ValidationResult.failure("Password must contain at least one lowercase letter", password)
    
    # Check for digit
    if not any(c.isdigit() for c in password):
        return ValidationResult.failure("Password must contain at least one digit", password)
    
    # Check for special character
    special_chars = '!@#$%^&*'
    if not any(c in special_chars for c in password):
        return ValidationResult.failure(
            f"Password must contain at least one special character ({special_chars})",
            password
        )
    
    # Check for common weak passwords
    weak_passwords = ['password', '12345678', 'qwerty123', 'admin123']
    if password.lower() in weak_passwords:
        return ValidationResult.failure("Password is too common", password)
    
    return ValidationResult.success(password)


# ==================== Email Validation ====================

def validate_email(email: str) -> ValidationResult:
    """
    Validate email address format.
    
    Args:
        email: Email address string
    
    Returns:
        ValidationResult with normalized email (lowercase) or error
    """
    if not email or not isinstance(email, str):
        return ValidationResult.failure("Email is required", email)
    
    email = email.strip().lower()
    
    # Basic email regex pattern
    pattern = r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$'
    
    if not re.match(pattern, email):
        return ValidationResult.failure(f"Invalid email format: {email}", email)
    
    if len(email) > 254:  # RFC 5321
        return ValidationResult.failure("Email too long", email)
    
    return ValidationResult.success(email)


# ==================== Required Field Validation ====================

def validate_required(value: Any, field_name: str) -> ValidationResult:
    """
    Validate that a required field is not empty.
    
    Args:
        value: The value to check
        field_name: Name of the field (for error messages)
    
    Returns:
        ValidationResult with value or error
    """
    if value is None:
        return ValidationResult.failure(f"{field_name} is required", value)
    
    if isinstance(value, str) and not value.strip():
        return ValidationResult.failure(f"{field_name} cannot be empty", value)
    
    return ValidationResult.success(value)


# ==================== Helper Functions ====================

def validate_all(*results: ValidationResult) -> ValidationResult:
    """
    Combine multiple validation results.
    Returns first failure or success if all pass.
    
    Args:
        *results: Variable number of ValidationResult objects
    
    Returns:
        First failed ValidationResult or success
    """
    for result in results:
        if not result.valid:
            return result
    
    return ValidationResult.success(True)
