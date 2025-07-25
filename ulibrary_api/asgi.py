"""
ulibrary_api/asgi.py

This file is part of the University Library project.
It configures the ASGI entry-point for the application, allowing it to be
served by ASGI-compliant web servers. It exposes the ASGI callable as a
module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/

Author: Raul Berrios
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ulibrary_api.settings")

application = get_asgi_application()
