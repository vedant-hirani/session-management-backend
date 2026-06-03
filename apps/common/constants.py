"""
Application-wide constants.
"""

# User roles
ROLE_USER = "user"
ROLE_CREATOR = "creator"

ROLE_CHOICES = [
    (ROLE_USER, "User"),
    (ROLE_CREATOR, "Creator"),
]

# Booking statuses
BOOKING_PENDING = "pending"
BOOKING_CONFIRMED = "confirmed"
BOOKING_CANCELLED = "cancelled"
BOOKING_COMPLETED = "completed"

BOOKING_STATUS_CHOICES = [
    (BOOKING_PENDING, "Pending"),
    (BOOKING_CONFIRMED, "Confirmed"),
    (BOOKING_CANCELLED, "Cancelled"),
    (BOOKING_COMPLETED, "Completed"),
]

# Session statuses
SESSION_DRAFT = "draft"
SESSION_PUBLISHED = "published"
SESSION_CANCELLED = "cancelled"

SESSION_STATUS_CHOICES = [
    (SESSION_DRAFT, "Draft"),
    (SESSION_PUBLISHED, "Published"),
    (SESSION_CANCELLED, "Cancelled"),
]
