from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Profile  # Import Profile model


def register_user(username, email, password, confirm_password):
    """
    Validates input and creates a new user & profile.
    Does NOT handle authentication or token generation.

    Returns a dictionary:
    - On success: { "success": True, "user": user }
    - On failure: { "success": False, "message": "Error message" }
    """

    # 1. Ensure all fields are provided
    if not username or not email or not password or not confirm_password:
        return {"success": False, "message": "All fields are required."}

    # 2. Check if passwords match
    if password != confirm_password:
        return {"success": False, "message": "Passwords do not match."}

    # 3. Validate password strength
    try:
        validate_password(password)
    except ValidationError as e:
        return {"success": False, "message": e.messages[0]}  # Return first validation error

    # 4. Check if username or email already exists
    if User.objects.filter(username=username).exists():
        return {"success": False, "message": "This username is already taken."}

    if User.objects.filter(email=email).exists():
        return {"success": False, "message": "This email is already taken."}

    # 5. Create user and profile
    user = User.objects.create_user(username=username, email=email, password=password)
    Profile.objects.create(user=user)

    return {"success": True, "user": user}
