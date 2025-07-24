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
    API endpoint that allows users to be viewed or edited.
    Only Librarians can create new users.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser | IsLibrarian] # Superusers or Librarians


class BookViewSet(viewsets.ModelViewSet):
    """
    API endpoint for books.
    - All authenticated users can list/search books.
    - Only Librarians can create, update, or delete books.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'author', 'genre']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            self.permission_classes = [IsLibrarian]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()


class CheckoutViewSet(viewsets.ModelViewSet):
    """
    API endpoint for checkouts.
    - Students can create checkouts (request a book) and view their own checkouts.
    - Librarians can view all checkouts and mark them as returned.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__username', 'student__first_name', 'student__last_name', 'book__title']

    def get_queryset(self):
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
        if self.action == 'create':
            return CreateCheckoutSerializer

        user = self.request.user
        if user.is_authenticated and user.role == 'librarian':
            return CheckoutLibrarianSerializer

        return CheckoutStudentSerializer

    def create(self, request, *args, **kwargs):
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
        # This method is called when a student requests a book.
        book = serializer.validated_data['book']
        with transaction.atomic():
            # Decrease book stock
            Book.objects.filter(id=book.id).update(stock=F('stock') - 1)
            # Save the checkout record
            serializer.save(student=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsLibrarian])
    def return_book(self, request, pk=None):
        """
        Action for a librarian to mark a book as returned.
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
