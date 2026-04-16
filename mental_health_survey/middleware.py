from django.shortcuts import redirect
from django.urls import reverse

class LoginRequiredMiddleware:
    """Redirect anonymous users to the auth landing page for protected URLs.

    Allows a safe whitelist of URL prefixes that are accessible without login:
    - static files, media, admin, the auth landing, login, signup, logout, and open APIs.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        # Define allowed path prefixes that do not require authentication
        self.allowed_prefixes = (
            '/static/',
            '/media/',
            '/favicon.ico',
            '/robots.txt',
            '/admin/',
            '/auth',
            '/login',
            '/signup',
            '/logout',
            '/doctor-login',
            '/doctor-signup',
            '/api/',
        )

    def __call__(self, request):
        path = request.path
        # If user is authenticated or path is allowed, continue
        if request.user.is_authenticated:
            return self.get_response(request)

        for pfx in self.allowed_prefixes:
            if path.startswith(pfx):
                return self.get_response(request)

        # Otherwise redirect to the auth landing page
        return redirect('wellness:auth')
