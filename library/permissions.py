"""
library/permissions.py

This file is part of the University Library project.
It contains custom permission classes for the Django REST Framework to control
access to different API endpoints based on user roles.

Author: Raul Berrios
"""
from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsLibrarian(BasePermission):
    """
    Custom permission to only allow access to users with the 'librarian' role.

    This permission class checks if the request is made by an authenticated user
    and if that user's `role` attribute is set to 'librarian'. It is used
    to protect views that should only be accessible by library staff.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "librarian"
        )


class IsStudent(BasePermission):
    """
    Custom permission to only allow access to users with the 'student' role.

    This permission class checks if the request is made by an authenticated user
    and if that user's `role` attribute is set to 'student'. It is used
    to protect views or actions that are specific to students, such as
    viewing their own checkouts.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "student"
        )
