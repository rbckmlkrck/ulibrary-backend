"""
library/serializers.py

This file is part of the University Library project.
It contains the serializers for the Django REST Framework, which define how
the User, Book, and Checkout models are converted to and from JSON.

Author: Raul Berrios
"""
from rest_framework import serializers
from .models import User, Book, Checkout
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    """
    Serializes User model data.

    This serializer handles the conversion of User objects to and from JSON.
    It ensures the `password` field is write-only for security and automatically
    hashes the password when creating a new user.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Hashes the user's password upon creation."""
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

class BookSerializer(serializers.ModelSerializer):
    """
    Serializes Book model data.

    Provides a standard representation of Book objects, including all
    relevant fields for listing and management.
    """
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'published_year', 'genre', 'stock']


class CheckoutStudentSerializer(serializers.ModelSerializer):
    """
    Serializer for students to view their own checkouts.

    This serializer provides a read-only view of a checkout record from a
    student's perspective. It includes nested details of the checked-out book.
    The student's own information is not included as it is implicit.
    """
    book = BookSerializer(read_only=True)

    class Meta:
        model = Checkout
        fields = ['id', 'book', 'checkout_date', 'return_date']


class CheckoutLibrarianSerializer(serializers.ModelSerializer):
    """
    Serializer for librarians to view all checkouts.

    This serializer provides a comprehensive, read-only view of a checkout
    record, including nested details for both the student and the book.
    It is intended for use by users with librarian privileges.
    """
    student = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Checkout
        fields = ['id', 'student', 'book', 'checkout_date', 'return_date']


class CreateCheckoutSerializer(serializers.ModelSerializer):
    """
    Serializer for a student to create a new checkout record.

    This serializer is used when a student checks out a book. It automatically
    assigns the currently authenticated user as the student. It also includes
    validation logic to ensure that a book is in stock before allowing a checkout.
    """
    student = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Checkout
        fields = ['id', 'book', 'student']

    def validate_book(self, book):
        """Ensures the book is in stock before allowing a checkout."""
        if book.stock <= 0:
            raise serializers.ValidationError("This book is out of stock.")
        return book
