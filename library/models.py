from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


# Resolve Bug: When I'm creating a superuser, the default role assigned was 'student' instead of 'librarian'
class CustomUserManager(UserManager):
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
    ROLE_CHOICES = (
        ("student", "Student"),
        ("librarian", "Librarian"),
    )
    # Add role field with default 'student'
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="student")

    objects = CustomUserManager()

    groups = models.ManyToManyField(
        "auth.Group",
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="library_user_groups",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="library_user_permissions",
        related_query_name="user",
    )


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    published_year = models.IntegerField()
    genre = models.CharField(max_length=100)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class Checkout(models.Model):
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
