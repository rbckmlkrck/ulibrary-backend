from rest_framework import serializers
from .models import User, Book, Checkout
from django.contrib.auth.hashers import make_password

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Hash the password before saving the user
        validated_data['password'] = make_password(validated_data.get('password'))
        return super().create(validated_data)

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'published_year', 'genre', 'stock']


class CheckoutStudentSerializer(serializers.ModelSerializer):
    """Serializer for students to view their checkouts."""
    book = BookSerializer(read_only=True)

    class Meta:
        model = Checkout
        fields = ['id', 'book', 'checkout_date', 'return_date']


class CheckoutLibrarianSerializer(serializers.ModelSerializer):
    """Serializer for librarians to view all checkouts."""
    student = UserSerializer(read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Checkout
        fields = ['id', 'student', 'book', 'checkout_date', 'return_date']


class CreateCheckoutSerializer(serializers.ModelSerializer):
    """Serializer for a student to create a checkout."""
    student = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Checkout
        fields = ['id', 'book', 'student']

    def validate_book(self, book):
        if book.stock <= 0:
            raise serializers.ValidationError("This book is out of stock.")
        return book

