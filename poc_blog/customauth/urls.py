
from .views.views import UserViewSet, ActiveAccount
from .views.reset_password_view import PasswordResetRequestApiView, PasswordResetApiView
from rest_framework.routers import DefaultRouter
from django.urls import path, include

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user_viewset')

urlpatterns = [
    path('', include(router.urls)),
    path('activate-account/<int:pk>/', ActiveAccount.as_view()),
    path('password-reset-request/', PasswordResetRequestApiView.as_view()),
    path('password-reset/', PasswordResetApiView.as_view())
]
