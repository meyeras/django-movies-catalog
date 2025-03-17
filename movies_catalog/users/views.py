from django.conf import settings
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.utils.http import url_has_allowed_host_and_scheme
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Profile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages


from django.contrib.auth import authenticate, login, logout
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny


# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from .utils import register_user  # Import the utility function

from .serializers import UserRegistrationSerializer

from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        result = register_user(username, email, password, confirm_password)

        if result["success"]:
            user = result["user"]

            # Authenticate and log in user after registration
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

            return redirect('movies-list')  # Redirect to movie list after signup
        else:
            messages.error(request, result["message"])
            return render(request, 'users/signup.html')

    return render(request, 'users/signup.html')

def all_users(request):
    users = Profile.objects.all()
    return render(request, 'users/users_list.html', {'users': users})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('movies-list')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid username or password.'})
    return render(request, 'users/login.html')


def user_logout(request):
    logout(request)
    return redirect('movies-list')

class ValidateTokenView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Validate a JWT token and return user details if valid.",
        manual_parameters=[
            openapi.Parameter(
                name="Authorization",
                in_=openapi.IN_HEADER,
                description="JWT token in format: Bearer <token>",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Token is valid",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "valid": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        "user_id": openapi.Schema(type=openapi.TYPE_INTEGER, example=123),
                        "username": openapi.Schema(type=openapi.TYPE_STRING, example="john_doe"),
                    }
                )
            ),
            401: openapi.Response(
                description="Invalid token",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "valid": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                    }
                )
            )
        }
    )
    def get(self, request, *args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return Response({"valid": False}, status=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]

        try:
            jwt_auth = JWTAuthentication()
            validated_token = jwt_auth.get_validated_token(token)  # This validates the token
            user = jwt_auth.get_user(validated_token)  # This retrieves the user

            return Response({"valid": True, "user_id": user.id, "username": user.username})
        except Exception as e:
            return Response({"valid": False}, status=status.HTTP_401_UNAUTHORIZED)



class UserRegistrationView(APIView):
    permission_classes = [AllowAny]  # Anyone can register

    @swagger_auto_schema(
        security=[],
        request_body=UserRegistrationSerializer,
        type=openapi.TYPE_OBJECT,
        required=["username", "email", "password", "confirm_password"],
        properties={
            "username": openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
            "email": openapi.Schema(type=openapi.TYPE_STRING, description="User's email address"),
            "password": openapi.Schema(type=openapi.TYPE_STRING, format="password", description="User's password"),
            "confirm_password": openapi.Schema(type=openapi.TYPE_STRING, format="password",
                                               description="Confirm password (must match password)"),
        },
        responses = {201:  "User registered successfully",
                     400:  "Bad request - Validation failed"},
        operation_description="Register a new user by providing username, email, password, and confirm_password.",
    )

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            print("Error in user registration", serializer.errors)
            return Response({"error": "Username or email already taken"}, status=status.HTTP_400_BAD_REQUEST)

        result = register_user(
            username=serializer.validated_data['username'],
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            confirm_password=serializer.validated_data['confirm_password']
        )

        if result["success"]:
            user = result["user"]

            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response(
                {
                    "message": "User registered successfully!",
                    "access": access_token,
                    "refresh": str(refresh),
                },
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response({"error": result["message"]}, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(TokenObtainPairView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description="User's username"),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description="User's password"),
            },
            required=['username', 'password'],
            security=[]
        ),
        responses={
            200: openapi.Response(
                "Successful login, returns access and refresh tokens",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description="JWT access token"),
                        'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
                    }
                )
            ),
            401: openapi.Response("Unauthorized - Invalid credentials"),
        },
        operation_description="Login using username and password to obtain JWT tokens."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenAPIView(TokenRefreshView):
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT refresh token"),
            },
            required=['refresh'],
            security=[]
        ),
        responses={
            200: openapi.Response(
                "Token refreshed successfully",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'access': openapi.Schema(type=openapi.TYPE_STRING, description="New JWT access token"),
                    }
                )
            ),
            401: openapi.Response("Unauthorized - Invalid refresh token"),
        },
        operation_description="Use the refresh token to get a new access token."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)