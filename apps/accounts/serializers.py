"""
Serializers for the accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class UserPublicSerializer(serializers.ModelSerializer):
    """Read-only public profile (safe to expose in session/booking responses)."""

    class Meta:
        model = User
        fields = ["id", "username", "avatar", "role"]
        read_only_fields = fields


class UserProfileSerializer(serializers.ModelSerializer):
    """Full profile — used by the authenticated user to view/update their own data."""

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "role",
            "avatar",
            "bio",
            "wallet_balance",
            "date_joined",
        ]
        read_only_fields = ["id", "email", "role", "wallet_balance", "date_joined"]

    def validate_username(self, value):
        user = self.context["request"].user
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value


class RegisterSerializer(serializers.ModelSerializer):
    """Register a new user with email, username, password, and role (fixed at sign-up)."""

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")
    role = serializers.ChoiceField(choices=["user", "creator"], default="user", required=False)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password2", "role", "first_name", "last_name"]
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop("password2")
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class OAuthSetupSerializer(serializers.ModelSerializer):
    """
    Used after Google OAuth for brand-new users.
    Lets them confirm/set their username and choose a role.
    Role is fixed permanently after this step.
    """
    role = serializers.ChoiceField(choices=["user", "creator"])
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ["username", "role"]

    def validate_username(self, value):
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def update(self, instance, validated_data):
        instance.username = validated_data["username"]
        instance.role = validated_data["role"]
        instance.save(update_fields=["username", "role"])
        return instance
