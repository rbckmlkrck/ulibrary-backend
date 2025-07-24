from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Book, Checkout
# Models registration for the admin interface
admin.site.register(User, UserAdmin)
admin.site.register(Book)
admin.site.register(Checkout)

