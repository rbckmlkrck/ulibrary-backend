import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from library.models import User, Book

class Command(BaseCommand):
    """
    Custom management command to seed the database with sample data.
    """
    help = 'Seeds the database with sample data for books and users.'

    def add_arguments(self, parser):
        """
        Adds command-line arguments for the command.
        """
        parser.add_argument('--books', type=int, help='The number of books to create.', default=200)
        parser.add_argument('--users', type=int, help='The number of users to create.', default=50)
        parser.add_argument('--clear', action='store_true', help='Clear existing book and user data before seeding.')

    @transaction.atomic
    def handle(self, *args, **options):
        """
        The main logic for the command.
        """
        self.stdout.write('Seeding database...')

        num_books = options['books']
        num_users = options['users']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data (books and non-superuser users)...'))
            Book.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        fake = Faker()

        # --- Create Users ---
        self.stdout.write(f'Creating {num_users} users...')
        users = []
        for _ in range(num_users):
            profile = fake.profile()
            user = User(
                username=profile['username'],
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                email=profile['mail'],
                role=random.choice(['student', 'student', 'student', 'librarian']) # 3:1 student to librarian ratio
            )
            user.set_password('password123') # Use a standard password for all seeded users
            users.append(user)
        User.objects.bulk_create(users)

        # --- Create Books ---
        self.stdout.write(f'Creating {num_books} books...')
        genres = ['Fantasy', 'Science Fiction', 'Mystery', 'Thriller', 'Romance', 'History', 'Biography', 'Computer Science']
        books = [
            Book(title=fake.sentence(nb_words=4).replace('.', ''), author=fake.name(), published_year=random.randint(1950, 2024), genre=random.choice(genres), stock=random.randint(1, 10))
            for _ in range(num_books)
        ]
        Book.objects.bulk_create(books)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_users} users and {num_books} books.'))