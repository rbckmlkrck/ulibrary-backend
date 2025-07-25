from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, Book, Checkout

class LibraryAPITests(APITestCase):
    """
    Test suite for the University Library API endpoints.
    """

    def setUp(self):
        """
        Set up initial data for all tests. This method runs before every test.
        """
        # Create users with different roles
        self.librarian_user = User.objects.create_user(
            username='librarian',
            password='password123',
            first_name='Lib',
            last_name='Rarian',
            role='librarian',
            is_staff=True
        )
        self.student_user = User.objects.create_user(
            username='student',
            password='password123',
            first_name='Stu',
            last_name='Dent',
            role='student'
        )

        # Create some books for testing
        self.book1 = Book.objects.create(title='The Way of Kings', author='Brandon Sanderson', published_year=2010, genre='Fantasy', stock=3)
        self.book2 = Book.objects.create(title='Dune', author='Frank Herbert', published_year=1965, genre='Science Fiction', stock=1)
        self.book3 = Book.objects.create(title='Zero Stock Book', author='Author', published_year=2000, genre='Test', stock=0)

    # --- Authentication and User Endpoint Tests ---

    def test_get_auth_token(self):
        """
        Ensure a user can get an authentication token with valid credentials.
        """
        url = '/api/token-auth/'
        data = {'username': 'student', 'password': 'password123'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_current_user_api(self):
        """
        Ensure the /api/me/ endpoint returns the correct user data for an authenticated user.
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('current-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.student_user.username)

    def test_librarian_can_create_user(self):
        """
        Ensure a librarian can create a new user.
        """
        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('user-list')
        data = {'username': 'newstudent', 'password': 'newpassword', 'first_name': 'New', 'last_name': 'Student', 'email': 'new@test.com', 'role': 'student'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)

    def test_student_cannot_create_user(self):
        """
        Ensure a student receives a 403 Forbidden error when trying to create a user.
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('user-list')
        data = {'username': 'anotherstudent', 'password': 'password', 'role': 'student'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Book Endpoint Tests ---

    def test_any_authenticated_user_can_list_books(self):
        """
        Ensure any authenticated user (e.g., a student) can list books.
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('book-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_librarian_can_create_book(self):
        """
        Ensure a librarian can create a new book.
        """
        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('book-list')
        data = {'title': 'New Book', 'author': 'New Author', 'published_year': 2024, 'genre': 'Fiction', 'stock': 5}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 4)

    def test_student_cannot_create_book(self):
        """
        Ensure a student receives a 403 Forbidden error when trying to create a book.
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('book-list')
        data = {'title': 'Student Book', 'author': 'Student Author', 'published_year': 2024, 'genre': 'Fiction', 'stock': 1}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- Checkout and Return Endpoint Tests ---

    def test_student_can_checkout_book(self):
        """
        Ensure a student can check out an available book, and the stock decreases.
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('checkout-list')
        data = {'book': self.book1.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.stock, 2)
        self.assertTrue(Checkout.objects.filter(student=self.student_user, book=self.book1, return_date__isnull=True).exists())

    def test_student_cannot_checkout_out_of_stock_book(self):
        """
        Ensure a student gets a validation error when checking out a book with zero stock.
        """
        self.client.force_authenticate(user=self.student_user)
        url = reverse('checkout-list')
        data = {'book': self.book3.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('out of stock', response.data['book'][0].lower())

    def test_student_cannot_checkout_same_book_twice(self):
        """
        Ensure a student gets a validation error for violating the unique checkout constraint.
        """
        Checkout.objects.create(student=self.student_user, book=self.book2)
        self.client.force_authenticate(user=self.student_user)
        url = reverse('checkout-list')
        data = {'book': self.book2.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('already checked out', response.data['detail'].lower())

    def test_librarian_can_return_book(self):
        """
        Ensure a librarian can mark a book as returned, and the stock increases.
        """
        checkout = Checkout.objects.create(student=self.student_user, book=self.book1)
        self.book1.stock = 2
        self.book1.save()

        self.client.force_authenticate(user=self.librarian_user)
        url = reverse('checkout-return-book', kwargs={'pk': checkout.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.stock, 3)
        checkout.refresh_from_db()
        self.assertIsNotNone(checkout.return_date)

    def test_student_cannot_return_book(self):
        """
        Ensure a student receives a 403 Forbidden error when trying to use the return_book action.
        """
        checkout = Checkout.objects.create(student=self.student_user, book=self.book1)
        self.client.force_authenticate(user=self.student_user)
        url = reverse('checkout-return-book', kwargs={'pk': checkout.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)