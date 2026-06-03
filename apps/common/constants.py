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

# ── API Response Messages ───────────────────────────────────────────────
# Sessions
MSG_SESSION_NOT_FOUND = "Session not found."
MSG_SESSION_UNAVAILABLE = "This session is not available for booking."
MSG_SESSION_FULLY_BOOKED = "This session is fully booked. No spots remaining."
MSG_SESSION_ALREADY_CANCELLED = "Session is already cancelled."
MSG_SESSION_ALREADY_DELETED = "Session is already deleted."
MSG_SESSION_NOT_DELETED = "Session is not deleted."
MSG_CANNOT_UPDATE_DELETED = "Cannot update a deleted session."
MSG_CANNOT_UPDATE_CANCELLED = "Cannot update a cancelled session."
MSG_CANNOT_CANCEL_DELETED = "Cannot cancel a deleted session."
MSG_CANNOT_CANCEL_DELETED_SESSION = "Cannot cancel booking for a cancelled or deleted session."
MSG_ONLY_CREATORS = "Only creators can create sessions."
MSG_OWN_SESSIONS_ONLY = "You can only edit your own sessions."
MSG_OWN_CANCEL_ONLY = "You can only cancel your own sessions."
MSG_OWN_DELETE_ONLY = "You can only delete your own sessions."
MSG_OWN_RESTORE_ONLY = "You can only restore your own sessions."

# Bookings
MSG_BOOKING_NOT_FOUND = "Booking not found."
MSG_BOOKING_ALREADY_CANCELLED = "Booking is already cancelled."
MSG_ALREADY_BOOKED = "You have already booked this session."
MSG_OWN_BOOKINGS_ONLY = "You can only cancel your own bookings."
MSG_SESSION_ID_REQUIRED = "session_id is required."

# Auth / General
MSG_NOT_AUTHORIZED = "Not authorized."
MSG_SERVER_ERROR = "An unexpected server error occurred."
MSG_PROFILE_UPDATE_SUCCESS = "Profile updated successfully."
MSG_REFUND_ISSUED = "Booking cancelled and refund issued to wallet."
MSG_REFRESH_TOKEN_REQUIRED = "Refresh token is required."
MSG_INVALID_TOKEN = "Invalid or expired token."
MSG_LOGGED_OUT = "Successfully logged out."

