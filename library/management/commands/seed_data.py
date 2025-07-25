"""
library/management/commands/seed_data.py

This file is part of the University Library project.
It contains a Django management command to populate the database with
sample data for testing and development purposes.

Author: Raul Berrios
"""
import os
import random
from django.core.management.base import BaseCommand
from django.db import transaction
from faker import Faker
from library.models import User, Book

class Command(BaseCommand):
    """
    A custom Django management command to seed the database with sample data.

    This command creates a specified number of books and users (students and
    librarians) using the Faker library. It supports clearing existing data
    before seeding and avoids creating duplicate users.

    Usage:
        python manage.py seed_data
        python manage.py seed_data --books 500 --users 100
        python manage.py seed_data --clear
    """
    help = 'Seeds the database with sample data for books and users.'

    def add_arguments(self, parser):
        """
        Adds command-line arguments to the command.

        Arguments:
            --books: The number of book records to create.
            --users: The number of user records to create.
            --clear: A flag to clear existing book and user data before seeding.
        """
        parser.add_argument('--books', type=int, help='The number of books to create.', default=200)
        parser.add_argument('--users', type=int, help='The number of users to create.', default=50)
        parser.add_argument('--clear', action='store_true', help='Clear existing book and user data before seeding.')

    @transaction.atomic
    def handle(self, *args, **options):
        """
        The main logic for the command.

        Executes the database seeding process within a single atomic transaction
        to ensure data integrity. It handles data clearing, user creation,
        and book creation.
        """
        self.stdout.write('Seeding database...')

        num_books = options['books']
        num_users = options['users']
        clear_data = options['clear']

        if clear_data:
            self.stdout.write(self.style.WARNING('Clearing existing data (books and non-superuser users)...'))
            Book.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
        elif Book.objects.exists() or User.objects.filter(is_superuser=False).exists():
            self.stdout.write(self.style.SUCCESS('Database already seeded. Skipping.'))
            return

        fake = Faker()
        # Use an environment variable for the seed password, with a default fallback.
        seed_password = os.environ.get('SEED_USER_PASSWORD', 'password123')

        # --- Create Users ---
        self.stdout.write(f'Creating {num_users} users...')
        created_users_count = 0
        for _ in range(num_users):
            try:
                profile = fake.profile()
                username = profile['username']

                # Check if user already exists to avoid IntegrityError.
                # This can happen if the Faker library generates a duplicate username,
                # especially when running in environments with a fixed random seed.
                if User.objects.filter(username=username).exists():
                    self.stdout.write(self.style.WARNING(f"User '{username}' already exists. Skipping."))
                    continue

                user = User(
                    username=username,
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=profile['mail'],
                    role=random.choice(['student', 'student', 'student', 'librarian']) # 3:1 student to librarian ratio
                )
                user.set_password(seed_password)
                user.save()
                created_users_count += 1
            except Exception as e:
                # Handle other potential errors gracefully without stopping the script
                self.stdout.write(self.style.ERROR(f"An error occurred while creating a user: {e}. Skipping."))
                continue

        # --- Create Books ---
        self.stdout.write(f'Creating {num_books} books...')
        genres = ['Fantasy', 'Science Fiction', 'Mystery', 'Thriller', 'Romance', 'History', 'Biography', 'Computer Science']
        books = [
            Book(title=fake.sentence(nb_words=4).replace('.', ''), author=fake.name(), published_year=random.randint(1950, 2024), genre=random.choice(genres), stock=random.randint(1, 10))
            for _ in range(num_books)
        ]
        Book.objects.bulk_create(books)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {created_users_count} new users and {num_books} books.'))