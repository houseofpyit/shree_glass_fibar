"""Schema validation tests."""

import pytest
from pydantic import ValidationError
from app.schemas.user import UserCreate


def test_valid_user_create():
    """Test valid user creation schema."""
    user = UserCreate(
        personal_name="Rahul Sharma",
        mobile="9876543210",
        email="rahul@example.com",
        password="SecurePass@123",
        business_name="Test Corp",
        gst_number="22AAAAA0000A1Z5",
    )
    assert user.personal_name == "Rahul Sharma"
    assert user.mobile == "9876543210"


def test_invalid_mobile():
    """Test invalid mobile number validation."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            personal_name="Test User",
            mobile="1234567890",  # Invalid: starts with 1
            email="test@example.com",
            password="SecurePass@123",
        )
    assert "Invalid Indian mobile number" in str(exc_info.value)


def test_invalid_gst():
    """Test invalid GST number validation."""
    with pytest.raises(ValidationError) as exc_info:
        UserCreate(
            personal_name="Test User",
            mobile="9876543210",
            email="test@example.com",
            password="SecurePass@123",
            gst_number="INVALID_GST",
        )
    assert "Invalid GST number" in str(exc_info.value)


def test_valid_gst_format():
    """Test valid GST number passes validation."""
    user = UserCreate(
        personal_name="Test User",
        mobile="9876543210",
        email="test@example.com",
        password="SecurePass@123",
        gst_number="22AAAAA0000A1Z5",
    )
    assert user.gst_number == "22AAAAA0000A1Z5"


def test_mobile_with_country_code():
    """Test mobile number with +91 prefix."""
    user = UserCreate(
        personal_name="Test User",
        mobile="+919876543210",
        email="test@example.com",
        password="SecurePass@123",
    )
    assert user.mobile == "9876543210"


def test_password_too_short():
    """Test password minimum length validation."""
    with pytest.raises(ValidationError):
        UserCreate(
            personal_name="Test User",
            mobile="9876543210",
            email="test@example.com",
            password="short",
        )
