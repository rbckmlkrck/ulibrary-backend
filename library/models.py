"""
library/models.py

This file is part of the University Library project.
It contains the Django data models for the 'library' application, defining
the structure of the User, Book, and Checkout tables in the database.

Author: Raul Berrios
"""
from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class CustomUserManager(UserManager):
    """
    Custom user manager for the User model.

    This manager overrides the default `create_superuser` method to ensure
    that any superuser created has their role automatically set to 'librarian'.
    This resolves an issue where superusers were defaulting to the 'student' role.
    """
    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """
        Create and save a SuperUser with the given email and password,
        and ensure their role is 'librarian'.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", "librarian")  # Ensure role is librarian

        if extra_fields.get("role") != "librarian":
            raise ValueError("Superuser must have role of Librarian.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom User model for the application.

    Extends Django's AbstractUser to include a `role` field, which can be
    either 'student' or 'librarian'. This model is the central point for
    user authentication and role-based permissions. It uses the
    CustomUserManager to handle user creation.
    """

    ROLE_CHOICES = (
        ("student", "Student"),
        ("librarian", "Librarian"),
    )
    # Add role field with default 'student'
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    objects = CustomUserManager()


class Book(models.Model):
    """
    Represents a single book in the library's collection.

    Stores details about the book, including its title, author, publication
    year, genre, and the current number of copies available in stock.
    """

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    published_year = models.IntegerField()
    genre = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Checkout(models.Model):
    """
    Represents a checkout record for a book by a student.

    This model links a student (User) to a book they have checked out.
    It includes the checkout date and an optional return date. A database
    constraint (`unique_active_checkout`) prevents a student from checking
    out the same book more than once if it hasn't been returned yet.
    """

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="checkouts",
        limit_choices_to={"role": "student"},
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    checkout_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "book"],
                condition=Q(return_date__isnull=True),
                name="unique_active_checkout",
            )
        ]

    def __str__(self):
        return f"{self.student.username} - {self.book.title}"
