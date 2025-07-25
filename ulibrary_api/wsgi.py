"""
ulibrary_api/wsgi.py

This file is part of the University Library project.
It configures the WSGI entry-point for the application, allowing it to be
served by WSGI-compliant web servers. It exposes the WSGI callable as a
module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/

Author: Raul Berrios
"""

import os
from dotenv import load_dotenv

from django.core.wsgi import get_wsgi_application

# Load environment variables from .env file
load_dotenv()

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ulibrary_api.settings')

application = get_wsgi_application()
