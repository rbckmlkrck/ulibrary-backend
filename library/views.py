"""
library/views.py

This file is part of the University Library project.
It contains the ViewSets that define the API endpoints for the library app,
handling the logic for user, book, and checkout management.

Author: Raul Berrios
"""
from django.db import transaction, IntegrityError
from django.utils import timezone
from django.db.models import F
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from drf_spectacular.utils import extend_schema

from .models import User, Book, Checkout
from .permissions import IsLibrarian, IsStudent
from .serializers import (
    UserSerializer,
    BookSerializer,
    CheckoutStudentSerializer,
    CheckoutLibrarianSerializer,
    CreateCheckoutSerializer,
)

@extend_schema(
    responses={200: UserSerializer},
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_api(request):
    """
    Returns the current authenticated user's details.
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    """
    Provides the API endpoints for viewing and editing users.

    Permissions:
    - Superusers and Librarians can perform any action (list, create, retrieve,
      update, delete).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser | IsLibrarian] # Superusers or Librarians


class BookViewSet(viewsets.ModelViewSet):
    """
    Provides API endpoints for managing books in the library.

    Allows for listing, searching, creating, updating, and deleting books.
    Access is controlled based on the user's role.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author', 'genre']

    def get_permissions(self):
        """
        Dynamically sets permissions based on the action.

        - Write actions (create, update, etc.) are restricted to Librarians.
        - Read actions (list, retrieve) are allowed for any authenticated user.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsLibrarian]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class CheckoutViewSet(viewsets.ModelViewSet):
    """
    Provides API endpoints for managing book checkouts.

    - **Students**: Can create new checkouts (i.e., check out a book) and
      view their own active checkouts.
    - **Librarians**: Can view all active checkouts across all students and
      mark books as returned.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'book__title', 'book__author']

    def get_queryset(self):
        """
        Dynamically filters the queryset based on the user's role.

        - Librarians can see all active checkouts.
        - Students can only see their own active checkouts.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.role == 'librarian':
                # Librarians can see all checkouts
                return Checkout.objects.filter(return_date__isnull=True)
            elif user.role == 'student':
                # Students see only their own active checkouts
                return Checkout.objects.filter(student=user, return_date__isnull=True)
        return Checkout.objects.none()

    def get_serializer_class(self):
        """
        Returns the appropriate serializer class based on the action and user role.

        - `CreateCheckoutSerializer` for the 'create' action.
        - `CheckoutLibrarianSerializer` for Librarians on other actions.
        - `CheckoutStudentSerializer` for Students on other actions.
        """
        if self.action == 'create':
            return CreateCheckoutSerializer

        user = self.request.user
        if user.is_authenticated and user.role == 'librarian':
            return CheckoutLibrarianSerializer

        return CheckoutStudentSerializer

    def filter_queryset(self, queryset):
        """
        Dynamically sets the search_fields based on the user's role.
        Students can only search their checkouts by book title or author.
        """
        user = self.request.user
        if user.is_authenticated and user.role == 'student':
            self.search_fields = ['book__title', 'book__author']
        # For librarians, the default search_fields will be used.
        return super().filter_queryset(queryset)

    def create(self, request, *args, **kwargs):
        """
        Handles the creation of a new checkout record.

        This method validates the request and wraps the creation logic in a
        transaction to ensure atomicity. It also provides a user-friendly
        error message if a student tries to check out a book they already have.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer)
        except IntegrityError:
            # This catches the UniqueConstraint violation from the model.
            # Explicitly raise with a 'detail' key for a consistent error format.
            raise ValidationError({"detail": "You have already checked out this book."})

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        Performs the creation of a checkout and updates the book's stock.

        This is called by `create` and executes within a database transaction.
        It decrements the book's stock and saves the new checkout record.
        """
        book = serializer.validated_data['book']
        with transaction.atomic():
            # Decrease book stock
            Book.objects.filter(id=book.id).update(stock=F('stock') - 1)
            # Save the checkout record
            serializer.save(student=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsLibrarian])
    def return_book(self, request, pk=None):
        """
        Marks a checkout as returned. Only accessible by Librarians.

        This action sets the `return_date` to the current time and increments
        the corresponding book's stock count.
        """
        checkout = self.get_object()
        if checkout.return_date:
            return Response({'status': 'Book already returned'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            # Increase book stock
            Book.objects.filter(id=checkout.book.id).update(stock=F('stock') + 1)
            # Mark as returned
            checkout.return_date = timezone.now()
            checkout.save()

        return Response({'status': 'Book returned successfully'})
