import pytest
from pydantic import ValidationError
from datetime import datetime, timedelta
from app.models.learner import Learner, LearnerCreate


def test_learner_create_empty_name() -> None:
    """Test that creating a learner with an empty name raises a validation error."""
    with pytest.raises(ValidationError) as exc_info:
        LearnerCreate(name="", email="john@example.com")
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("name",)
    assert errors[0]["type"] == "string_too_short"
    assert "String should have at least 1 character" in errors[0]["msg"]


def test_learner_create_whitespace_name() -> None:
    """Test that creating a learner with only whitespace in name raises a validation error."""
    with pytest.raises(ValidationError) as exc_info:
        LearnerCreate(name="   ", email="john@example.com")
    
    errors = exc_info.value.errors()
    assert len(errors) == 1
    assert errors[0]["loc"] == ("name",)
    assert errors[0]["type"] == "string_too_short"
    assert "String should have at least 1 character" in errors[0]["msg"]


def test_learner_create_invalid_emails() -> None:
    """Test that creating a learner with various invalid email formats raises validation errors."""
    invalid_emails = [
        "john@",                    # missing domain
        "@example.com",             # missing username
        "john.example.com",          # missing @
        "john@example",              # missing top-level domain
        "john@.com",                 # empty domain label
        "john@example.",             # empty top-level domain
        "john@example..com",         # double dot in domain
        "john space@example.com",    # space in email
        "john@exam ple.com",         # space in domain
    ]
    
    for invalid_email in invalid_emails:
        with pytest.raises(ValidationError) as exc_info:
            LearnerCreate(name="John Doe", email=invalid_email)
        
        errors = exc_info.value.errors()
        assert len(errors) == 1
        assert errors[0]["loc"] == ("email",)
        assert errors[0]["type"] == "value_error.email"
        assert "value is not a valid email address" in errors[0]["msg"].lower()


def test_learner_create_valid_email_boundaries() -> None:
    """Test valid email addresses at boundary conditions."""
    valid_emails = [
        "a@b.co",                    # Very short local part and domain
        "very.long.local.part.with.dots@example.com",  # Long local part with dots
        "user+filter@example.com",    # Plus addressing
        "user.name@subdomain.example.com",  # Multiple subdomains
        "user@example.co.uk",         # Multi-part TLD
        "1234567890@example.com",     # Numeric local part
        "user@example.com",            # Standard email
    ]
    
    for valid_email in valid_emails:
        learner = LearnerCreate(name="John Doe", email=valid_email)
        assert learner.email == valid_email
        assert learner.name == "John Doe"


def test_learner_table_model_defaults() -> None:
    """Test that the Learner table model has correct default values."""
    learner = Learner(name="John Doe", email="john@example.com")
    
    assert learner.id is None
    assert learner.enrolled_at is None
    assert learner.name == "John Doe"
    assert learner.email == "john@example.com"


def test_learner_create_to_learner_conversion() -> None:
    """Test that a LearnerCreate schema can be properly converted to a Learner model."""
    learner_create = LearnerCreate(name="Jane Smith", email="jane@example.com")
    
    # Simulate what happens in the API when creating a new learner
    learner = Learner(
        name=learner_create.name,
        email=learner_create.email,
        enrolled_at=datetime.now()  # This would typically be set by the system
    )
    
    assert learner.name == "Jane Smith"
    assert learner.email == "jane@example.com"
    assert learner.id is None
    assert isinstance(learner.enrolled_at, datetime)


def test_learner_with_special_characters_in_name() -> None:
    """Test that learner names can contain special characters."""
    special_names = [
        "José García",              # Accented characters
        "John O'Connor",             # Apostrophe
        "Mary-Jane Smith",           # Hyphen
        "Dr. John Doe",              # Dot
        "Иван Петров",                # Cyrillic
        "张伟",                        # Chinese characters
        "أحمد محمد",                  # Arabic characters
    ]
    
    for name in special_names:
        learner = LearnerCreate(name=name, email="john@example.com")
        assert learner.name == name


def test_learner_email_max_length() -> None:
    """Test email addresses at different length boundaries."""
    # Create emails of varying lengths
    local_part = "a" * 64  # Max local part length is typically 64
    domain = "example.com"
    long_email = f"{local_part}@{domain}"
    
    learner = LearnerCreate(name="John Doe", email=long_email)
    assert learner.email == long_email
    
    # Test with very long but valid email
    very_long_local = "a" * 63
    very_long_email = f"{very_long_local}@very-long-subdomain.very-long-domain-name.com"
    learner2 = LearnerCreate(name="John Doe", email=very_long_email)
    assert learner2.email == very_long_email


def test_learner_update_without_changing_email() -> None:
    """Test that a learner can be updated without changing the email."""
    # This test simulates a partial update scenario
    original_learner = Learner(
        id=1,
        name="John Doe",
        email="john@example.com",
        enrolled_at=datetime.now() - timedelta(days=30)
    )
    
    # Simulate updating only the name
    updated_learner = Learner(
        id=original_learner.id,
        name="John Smith",
        email=original_learner.email,
        enrolled_at=original_learner.enrolled_at
    )
    
    assert updated_learner.id == original_learner.id
    assert updated_learner.name == "John Smith"
    assert updated_learner.name != original_learner.name
    assert updated_learner.email == original_learner.email
    assert updated_learner.enrolled_at == original_learner.enrolled_at