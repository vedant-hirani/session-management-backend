"""
Custom User model with role support.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.common.constants import ROLE_USER, ROLE_CHOICES


class User(AbstractUser):
    """
    Extended User model.
    - role: 'user' or 'creator'
    - avatar: URL or path to profile picture
    - bio: short description
    """

    class Role(models.TextChoices):
        USER = "user", "User"
        CREATOR = "creator", "Creator"

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )
    avatar = models.URLField(blank=True, null=True)
    bio = models.TextField(blank=True, default="")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.email} ({self.role})"

    @property
    def is_creator(self):
        return self.role == self.Role.CREATOR

    @property
    def is_regular_user(self):
        return self.role == self.Role.USER
