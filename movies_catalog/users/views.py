from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.contrib import messages


from django.contrib.auth import authenticate, login, logout


# Create your views here.
def signup(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        additional_info = request.POST.get('additional_info')

        if not username or not email or not password or not confirm_password:
            messages.error(request, 'Please fill all fields')
            return redirect('users/signup.html')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return render(request, 'users/signup.html')

        # Validate the password strength
        try:
            validate_password(password)
        except ValidationError as e:
            # If validation fails, add error messages and return to the form
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'users/signup.html')

        # Check for duplicate username
        if User.objects.filter(username=username).exists():
            messages.error(request, f"The username '{username}' is already taken. Please choose another.")
            return render(request, 'users/signup.html')

        #Check for duplicate email
        if User.objects.filter(email=email).exists():
            messages.error(request, f"The email '{email}' is already taken. Please choose another.")
            return render(request, 'users/signup.html')

        #Proceed with user creation
        user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password)
        Profile.objects.create(user=user)

        # Authenticate and log in the user
        user = authenticate(username=username, password=password)  # Verifies credentials
        if user is not None:
            login(request, user)  # Logs the user in
            return redirect('movies-list')  # Redirect to movies list after login
        else:
            messages.error(request, "Something went wrong. Please try logging in manually.")
            return redirect('user-login')

    else:
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


