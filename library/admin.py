"""
library/admin.py

This file is part of the University Library project.
It configures the Django admin interface for the library application's models,
making them accessible and manageable through the admin panel.

Author: Raul Berrios
"""
from django.contrib import admin
from django.contrib import messages
from django.utils import timezone
from django.utils.translation import ngettext
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Book, Checkout, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Customizes the admin interface for the User model.

    Extends the base UserAdmin to include the 'role' field in the list
    display and fieldsets for better visibility and management of user roles.
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role', {'fields': ('role',)}),
    )


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Book model.

    Provides a detailed view in the admin panel, including list display,
    search functionality, and filters for managing the library's book collection.
    """
    list_display = ('title', 'author', 'published_year', 'genre', 'stock')
    search_fields = ('title', 'author', 'genre')
    list_filter = ('genre', 'published_year')


@admin.register(Checkout)
class CheckoutAdmin(admin.ModelAdmin):
    """
    Admin interface configuration for the Checkout model.

    Displays checkout records and provides an action to mark books as returned,
    which updates the book's stock accordingly.
    """
    list_display = ('student', 'book', 'checkout_date', 'return_date')
    search_fields = ('student__username', 'book__title')
    list_filter = ('return_date',)
    actions = ['mark_as_returned']

    @admin.action(description='Mark selected checkouts as returned')
    def mark_as_returned(self, request, queryset):
        """
        Admin action to mark one or more checkout records as returned.

        This action sets the `return_date` to the current time and increments
        the stock for the associated book. It only processes active checkouts
        (those without a `return_date`).
        """
        active_checkouts = queryset.filter(return_date__isnull=True)
        updated_count = 0
        for checkout in active_checkouts:
            checkout.return_date = timezone.now()
            checkout.book.stock += 1
            checkout.book.save()
            checkout.save()
            updated_count += 1

        if updated_count > 0:
            self.message_user(request, ngettext(
                '%d checkout was successfully marked as returned.',
                '%d checkouts were successfully marked as returned.',
                updated_count,
            ) % updated_count, messages.SUCCESS)
        else:
            self.message_user(request, 'No active checkouts were selected to be returned.', messages.WARNING)
