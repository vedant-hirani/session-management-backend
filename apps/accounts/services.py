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
