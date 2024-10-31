# core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class RoleBasedAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            user_type = request.user.user_type
            # Redirect logic based on user_type here if needed
        response = self.get_response(request)
        return response
