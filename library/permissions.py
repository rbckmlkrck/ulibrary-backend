from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsLibrarian(BasePermission):
    """
    Allows access only to librarian users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "librarian"
        )


class IsStudent(BasePermission):
    """
    Allows access only to student users.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "student"
        )
