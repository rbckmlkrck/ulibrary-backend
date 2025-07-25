"""
ulibrary_api/urls.py

This file is part of the University Library project.
It defines the main URL configuration for the entire project. The `urlpatterns`
list routes URLs to views, including the admin site, the library API,
authentication endpoints, and the API schema documentation.

Author: Raul Berrios
"""
from django.contrib import admin
from django.urls import include, path
from django.views.generic.base import RedirectView
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.authtoken import views

# Main URL patterns for the project.
urlpatterns = [
    # Redirect the root URL ("/") to the Swagger UI for API documentation.
    path("", RedirectView.as_view(url="/api/schema/swagger-ui/", permanent=False)),

    # Django's built-in admin site.
    path("admin/", admin.site.urls),

    # Include the URL patterns from the 'library' application, prefixed with "api/".
    path("api/", include("library.urls")),

    # Endpoint for obtaining an authentication token.
    path("api/token-auth/", views.obtain_auth_token),

    # API schema generation endpoints provided by drf-spectacular.
    # Generates the OpenAPI schema file.
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Serves the interactive Swagger UI for the API.
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # Serves the ReDoc documentation for the API.
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
