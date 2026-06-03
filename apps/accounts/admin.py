from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["email", "username", "role", "is_staff", "date_joined"]
    list_filter = ["role", "is_staff", "is_active"]
    search_fields = ["email", "username"]
    ordering = ["-date_joined"]
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("role", "avatar", "bio")}),
    )
