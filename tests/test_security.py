# tests/test_security.py
"""Property-based and unit tests for security functions"""

import pytest
from hypothesis import given, settings
import tests.generators as gen
from modules.security import (
    hash_password_secure,
    verify_password_secure,
    check_password_strength
)


@pytest.mark.property
@given(pwd=gen.strong_password())
@settings(deadline=1000)  # bcrypt is intentionally slow for security
def test_password_hashing(pwd):
    """
    **Feature: data-integrity-testing, Property 21: Password hashing**
    **Validates: Requirements 7.1**
    
    For any password, the stored value must be a hash (not plaintext)
    and must be different from the original password.
    """
    hashed = hash_password_secure(pwd)
    
    # Hash should be different from original
    assert hashed != pwd
    
    # Hash should be bcrypt format (starts with $2b$)
    assert hashed.startswith('$2b$') or hashed.startswith('$2a$')
    
    # Should be able to verify
    assert verify_password_secure(hashed, pwd) is True


@pytest.mark.property
@given(pwd1=gen.strong_password(), pwd2=gen.strong_password())
@settings(deadline=2000)  # bcrypt is intentionally slow for security
def test_unique_password_salts(pwd1, pwd2):
    """
    **Feature: data-integrity-testing, Property 23: Unique password salts**
    **Validates: Requirements 7.4**
    
    For any two users, their password hashes must use different salts
    even if they have the same password.
    """
    # Hash same password twice
    hash1 = hash_password_secure(pwd1)
    hash2 = hash_password_secure(pwd1)
    
    # Hashes should be different (different salts)
    assert hash1 != hash2
    
    # Both should verify correctly
    assert verify_password_secure(hash1, pwd1) is True
    assert verify_password_secure(hash2, pwd1) is True


@pytest.mark.unit
def test_hash_password_secure_creates_valid_hash():
    """Test that hashing creates valid bcrypt hash"""
    password = "TestPass123!"
    hashed = hash_password_secure(password)
    
    assert isinstance(hashed, str)
    assert len(hashed) == 60  # bcrypt hashes are 60 chars
    assert hashed.startswith('$2')


@pytest.mark.unit
def test_verify_password_secure_correct_password():
    """Test verifying correct password"""
    password = "TestPass123!"
    hashed = hash_password_secure(password)
    
    assert verify_password_secure(hashed, password) is True


@pytest.mark.unit
def test_verify_password_secure_wrong_password():
    """Test verifying wrong password"""
    password = "TestPass123!"
    hashed = hash_password_secure(password)
    
    assert verify_password_secure(hashed, "WrongPass456!") is False


@pytest.mark.unit
def test_hash_password_rejects_weak():
    """Test that weak passwords are rejected"""
    with pytest.raises(ValueError):
        hash_password_secure("weak")


@pytest.mark.unit
def test_check_password_strength_strong():
    """Test password strength checker for strong password"""
    is_strong, message, score = check_password_strength("VeryStrong123!Pass")
    assert is_strong is True
    assert score >= 60


@pytest.mark.unit
def test_check_password_strength_weak():
    """Test password strength checker for weak password"""
    is_strong, message, score = check_password_strength("weak")
    assert is_strong is False
    assert score == 0
