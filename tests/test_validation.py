# tests/test_validation.py
"""Property-based and unit tests for validation functions"""

import pytest
from hypothesis import given, assume
import tests.generators as gen
from modules.validators import (
    ValidationResult,
    validate_price,
    validate_quantity,
    validate_phone,
    validate_sku,
    validate_password,
    validate_email,
    validate_required,
    validate_all
)


# ==================== ValidationResult Tests ====================

@pytest.mark.unit
def test_validation_result_success():
    """Test ValidationResult.success factory method"""
    result = ValidationResult.success(42)
    assert result.valid is True
    assert result.normalized_value == 42
    assert result.error_message is None


@pytest.mark.unit
def test_validation_result_failure():
    """Test ValidationResult.failure factory method"""
    result = ValidationResult.failure("Error message", "bad_value")
    assert result.valid is False
    assert result.normalized_value == "bad_value"
    assert result.error_message == "Error message"


# ==================== Price Validation Tests ====================

@pytest.mark.property
@given(price=gen.valid_price)
def test_validate_price_accepts_valid_prices(price):
    """
    **Feature: data-integrity-testing, Property 11: Required field validation**
    **Validates: Requirements 4.3**
    
    For any valid price (non-negative float), validation should succeed.
    """
    result = validate_price(price)
    assert result.valid is True
    assert result.normalized_value >= 0
    assert isinstance(result.normalized_value, float)


@pytest.mark.unit
def test_validate_price_rejects_negative():
    """Test that negative prices are rejected"""
    result = validate_price(-10.50)
    assert result.valid is False
    assert "negative" in result.error_message.lower()


@pytest.mark.unit
def test_validate_price_rejects_invalid_format():
    """Test that invalid price formats are rejected"""
    result = validate_price("not_a_number")
    assert result.valid is False
    assert "invalid" in result.error_message.lower()


@pytest.mark.unit
def test_validate_price_rounds_to_two_decimals():
    """Test that prices are rounded to 2 decimal places"""
    result = validate_price(10.999)
    assert result.valid is True
    assert result.normalized_value == 11.00


# ==================== Quantity Validation Tests ====================

@pytest.mark.property
@given(qty=gen.non_negative_quantity)
def test_validate_quantity_accepts_valid_quantities(qty):
    """For any non-negative integer, quantity validation should succeed"""
    result = validate_quantity(qty)
    assert result.valid is True
    assert result.normalized_value >= 0
    assert isinstance(result.normalized_value, int)


@pytest.mark.unit
def test_validate_quantity_rejects_negative():
    """Test that negative quantities are rejected"""
    result = validate_quantity(-5)
    assert result.valid is False
    assert "negative" in result.error_message.lower()


@pytest.mark.unit
def test_validate_quantity_rejects_invalid_format():
    """Test that invalid quantity formats are rejected"""
    result = validate_quantity("abc")
    assert result.valid is False
    assert "invalid" in result.error_message.lower()


# ==================== Phone Number Validation Tests ====================

@pytest.mark.property
@given(phone=gen.phone_number)
def test_validate_phone_accepts_valid_numbers(phone):
    """
    **Feature: data-integrity-testing, Property 12: Phone number format validation**
    **Validates: Requirements 4.5**
    
    For any valid phone number (10-15 digits), validation should succeed
    and normalize to digits only.
    """
    result = validate_phone(phone)
    assert result.valid is True
    assert result.normalized_value.isdigit()
    assert 10 <= len(result.normalized_value) <= 15


@pytest.mark.unit
def test_validate_phone_normalizes_formats():
    """Test that various phone formats are normalized"""
    test_cases = [
        ("123-456-7890", "1234567890"),
        ("(123) 456-7890", "1234567890"),
        ("+1 123-456-7890", "11234567890"),
        ("123.456.7890", "1234567890"),
    ]
    
    for input_phone, expected in test_cases:
        result = validate_phone(input_phone)
        assert result.valid is True
        assert result.normalized_value == expected


@pytest.mark.unit
def test_validate_phone_rejects_too_short():
    """Test that phone numbers too short are rejected"""
    result = validate_phone("12345")
    assert result.valid is False
    assert "short" in result.error_message.lower()


@pytest.mark.unit
def test_validate_phone_rejects_too_long():
    """Test that phone numbers too long are rejected"""
    result = validate_phone("1234567890123456")
    assert result.valid is False
    assert "long" in result.error_message.lower()


# ==================== SKU Validation Tests ====================

@pytest.mark.property
@given(sku=gen.valid_sku)
def test_validate_sku_accepts_valid_skus(sku):
    """For any valid SKU, validation should succeed"""
    result = validate_sku(sku)
    assert result.valid is True
    assert 3 <= len(result.normalized_value) <= 20


@pytest.mark.unit
def test_validate_sku_rejects_too_short():
    """Test that SKUs too short are rejected"""
    result = validate_sku("AB")
    assert result.valid is False
    assert "short" in result.error_message.lower()


@pytest.mark.unit
def test_validate_sku_rejects_too_long():
    """Test that SKUs too long are rejected"""
    result = validate_sku("A" * 21)
    assert result.valid is False
    assert "long" in result.error_message.lower()


@pytest.mark.unit
def test_validate_sku_rejects_invalid_characters():
    """Test that SKUs with invalid characters are rejected"""
    result = validate_sku("ABC@123")
    assert result.valid is False
    assert "invalid" in result.error_message.lower()


@pytest.mark.unit
def test_validate_sku_rejects_hyphen_at_edges():
    """Test that SKUs starting/ending with hyphen are rejected"""
    result1 = validate_sku("-ABC123")
    result2 = validate_sku("ABC123-")
    assert result1.valid is False
    assert result2.valid is False


@pytest.mark.unit
def test_validate_sku_checks_uniqueness():
    """Test that duplicate SKUs are rejected when check_unique=True"""
    existing = {"SKU-001", "SKU-002"}
    result = validate_sku("SKU-001", check_unique=True, existing_skus=existing)
    assert result.valid is False
    assert "exists" in result.error_message.lower()


# ==================== Password Validation Tests ====================

@pytest.mark.property
@given(pwd=gen.strong_password())
def test_validate_password_accepts_strong_passwords(pwd):
    """
    **Feature: data-integrity-testing, Property 22: Password complexity enforcement**
    **Validates: Requirements 7.3**
    
    For any password meeting complexity requirements, validation should succeed.
    """
    result = validate_password(pwd)
    assert result.valid is True


@pytest.mark.property
@given(pwd=gen.weak_password())
def test_validate_password_rejects_weak_passwords(pwd):
    """For any weak password, validation should fail"""
    result = validate_password(pwd)
    assert result.valid is False


@pytest.mark.unit
def test_validate_password_rejects_too_short():
    """Test that passwords too short are rejected"""
    result = validate_password("Abc1!")
    assert result.valid is False
    assert "at least" in result.error_message.lower()


@pytest.mark.unit
def test_validate_password_rejects_no_uppercase():
    """Test that passwords without uppercase are rejected"""
    result = validate_password("abcdefg1!")
    assert result.valid is False
    assert "uppercase" in result.error_message.lower()


@pytest.mark.unit
def test_validate_password_rejects_no_lowercase():
    """Test that passwords without lowercase are rejected"""
    result = validate_password("ABCDEFG1!")
    assert result.valid is False
    assert "lowercase" in result.error_message.lower()


@pytest.mark.unit
def test_validate_password_rejects_no_digit():
    """Test that passwords without digits are rejected"""
    result = validate_password("Abcdefgh!")
    assert result.valid is False
    assert "digit" in result.error_message.lower()


@pytest.mark.unit
def test_validate_password_rejects_no_special():
    """Test that passwords without special characters are rejected"""
    result = validate_password("Abcdefgh1")
    assert result.valid is False
    assert "special" in result.error_message.lower()


@pytest.mark.unit
def test_validate_password_rejects_common_passwords():
    """Test that common weak passwords are rejected"""
    weak = ["password", "12345678", "qwerty123"]
    for pwd in weak:
        result = validate_password(pwd)
        assert result.valid is False


# ==================== Email Validation Tests ====================

@pytest.mark.unit
def test_validate_email_accepts_valid_emails():
    """Test that valid email formats are accepted"""
    valid_emails = [
        "user@example.com",
        "test.user@example.co.uk",
        "user+tag@example.com",
        "user123@test-domain.com"
    ]
    
    for email in valid_emails:
        result = validate_email(email)
        assert result.valid is True, f"Failed for {email}"
        assert result.normalized_value == email.lower()


@pytest.mark.unit
def test_validate_email_rejects_invalid_formats():
    """Test that invalid email formats are rejected"""
    invalid_emails = [
        "notanemail",
        "@example.com",
        "user@",
        "user @example.com",
        "user@.com"
    ]
    
    for email in invalid_emails:
        result = validate_email(email)
        assert result.valid is False, f"Should reject {email}"


# ==================== Required Field Validation Tests ====================

@pytest.mark.property
@given(value=gen.valid_name)
def test_validate_required_accepts_non_empty(value):
    """
    **Feature: data-integrity-testing, Property 11: Required field validation**
    **Validates: Requirements 4.3**
    
    For any non-empty value, required field validation should succeed.
    """
    result = validate_required(value, "test_field")
    assert result.valid is True


@pytest.mark.unit
def test_validate_required_rejects_none():
    """Test that None values are rejected"""
    result = validate_required(None, "test_field")
    assert result.valid is False
    assert "required" in result.error_message.lower()


@pytest.mark.unit
def test_validate_required_rejects_empty_string():
    """Test that empty strings are rejected"""
    result = validate_required("", "test_field")
    assert result.valid is False
    assert "empty" in result.error_message.lower()


@pytest.mark.unit
def test_validate_required_rejects_whitespace():
    """Test that whitespace-only strings are rejected"""
    result = validate_required("   ", "test_field")
    assert result.valid is False
    assert "empty" in result.error_message.lower()


# ==================== Combined Validation Tests ====================

@pytest.mark.unit
def test_validate_all_returns_first_failure():
    """Test that validate_all returns first failure"""
    result1 = ValidationResult.success(1)
    result2 = ValidationResult.failure("Error 2", None)
    result3 = ValidationResult.failure("Error 3", None)
    
    combined = validate_all(result1, result2, result3)
    assert combined.valid is False
    assert combined.error_message == "Error 2"


@pytest.mark.unit
def test_validate_all_returns_success_if_all_pass():
    """Test that validate_all returns success if all pass"""
    result1 = ValidationResult.success(1)
    result2 = ValidationResult.success(2)
    result3 = ValidationResult.success(3)
    
    combined = validate_all(result1, result2, result3)
    assert combined.valid is True
