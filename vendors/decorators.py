from django.shortcuts import redirect
from django.contrib.auth import authenticate, login

def user_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            # Check if the current user matches the specified credentials
            if request.user.username == 'gouthamn2024' and request.user.check_password('murdeshwartender'):
                return view_func(request, *args, **kwargs)
        # Redirect to login page with a message if user is not allowed
        return redirect('login')  # Replace 'login' with your actual login URL name
    return _wrapped_view
