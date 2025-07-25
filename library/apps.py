"""
library/apps.py

This file is part of the University Library project.
It contains the application configuration for the 'library' app.

Author: Raul Berrios

"""
from django.apps import AppConfig


class LibraryConfig(AppConfig):
    """
    Application configuration for the 'library' app.

    This class defines the configuration for the Django application,
    including the default auto field for models and the application name.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "library"
