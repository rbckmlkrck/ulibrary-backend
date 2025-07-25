"""
library/urls.py

This file is part of the University Library project.
It defines the URL patterns for the 'library' application, mapping API
endpoints to their corresponding ViewSets.

Author: Raul Berrios
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BookViewSet, CheckoutViewSet, current_user_api

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'books', BookViewSet)
# The `basename` is provided for the CheckoutViewSet because its `get_queryset`
# method is dynamic, preventing DRF from automatically inferring the model name.
router.register(r'checkouts', CheckoutViewSet, basename='checkout')


# The API URLs are now determined automatically by the router.
# Additionally, we include a custom endpoint for the current user.
urlpatterns = [
    path('', include(router.urls)),
    path('me/', current_user_api, name='current-user'),
]
