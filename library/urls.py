from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, BookViewSet, CheckoutViewSet, current_user_api

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'books', BookViewSet)
router.register(r'checkouts', CheckoutViewSet, basename='checkout')


urlpatterns = [
    path('', include(router.urls)),
    path('me/', current_user_api, name='current-user'),
]

# The `basename` is provided for the CheckoutViewSet because the queryset is dynamic
# and DRF cannot automatically determine it.

