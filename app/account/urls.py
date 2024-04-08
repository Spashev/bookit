from django.urls import path, include

from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from account.views import (
    UserViewSet,
    UserCheckEmailView,
    UserCreateView,
    UserActivateView,
    ResendActivateView,
    ObtainTokenView,
    UserPolicyView,
    UserForgotPasswordByEmailView,
    SendVerifyCodeByEmailView,
    VerifyCodeByEmailView,
    UserAvatarViewSet,
)

router = DefaultRouter(trailing_slash=True)
router.register('users/create', UserCreateView, basename='users-create')
router.register('users', UserViewSet, basename='users')
router.register('users/avatar', UserAvatarViewSet, basename='user_avatar')

urlpatterns = [
    path('policy/', UserPolicyView.as_view(), name='policy'),

    path('users/token/', ObtainTokenView.as_view(({'post': 'post'})), name='token_obtain_pair'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/check-email/', UserCheckEmailView.as_view(), name='check-email'),

    path('users/activate/', UserActivateView.as_view(), name='user-activate'),
    path('users/resend-activate-code/', ResendActivateView.as_view(), name='resend-activate-code'),
    path('users/forgot-password/', UserForgotPasswordByEmailView.as_view(), name='reset-password'),
    path('users/send-email-verify-code/', SendVerifyCodeByEmailView.as_view(), name='send_verify_email_code'),
    path('users/verify-code/', VerifyCodeByEmailView.as_view(), name='verify_email_code'),

    path('', include(router.urls))
]
