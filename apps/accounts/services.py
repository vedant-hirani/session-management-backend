"""
Business logic for the accounts app.
"""
from django.contrib.auth import get_user_model

User = get_user_model()


def update_user_profile(user, validated_data: dict) -> User:
    """Update allowed profile fields and save."""
    for field, value in validated_data.items():
        setattr(user, field, value)
    user.save()
    return user


def switch_user_role(user, new_role: str) -> User:
    """
    Switch the user's role.
    In a real system you might add eligibility checks here
    (e.g. require email verification before becoming a creator).
    """
    allowed_roles = [User.Role.USER, User.Role.CREATOR]
    if new_role not in allowed_roles:
        raise ValueError(f"Invalid role: {new_role}")
    user.role = new_role
    user.save(update_fields=["role"])
    return user
