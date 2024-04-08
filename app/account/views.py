import os
from io import BytesIO
from datetime import datetime

from rest_framework import viewsets, mixins, permissions, status, generics, views
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.core.cache import cache
from django.http import HttpResponse

from account import RoleType
from account.models import User
from account.serializers import (
    ListUserSerializer,
    CreateUserSerializer,
    ResetPasswordSerializer,
    UpdateUserSerializer,
    UpdateManagerSerializer,
    CreateManagerSerializer,
    CheckEmailSerializer,
    UserActivateSerializer,
    UserEmailSerializer,
    ObtainTokenSerializer,
    VerifySmsCodeSerializer,
    ForgotPasswordSerializer,
    UserAvatarUploadSerializer,
)
from helpers.logger import log_exception, log_message
from helpers.utils import has_passed_30_minutes, has_passed_2_minutes, generate_activation_code, delete_file
from helpers.serializers import EmailSerializer
from helpers.services import update_instance
from account.tasks import send_email
from account.authentication import JWTAuthentication


class ObtainTokenView(viewsets.GenericViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = ObtainTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')

        user = User.objects.filter(email=email).first()
        if user is None:
            return Response(
                data={'message': 'User not found', 'detail_code': 'user_not_found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if user is None or not user.check_password(password):
            return Response(
                data={'message': 'Invalid credentials', 'detail_code': 'invalid_credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                data={'message': 'User not active', 'detail_code': 'user_not_active'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        jwt_token = JWTAuthentication.create_jwt(user)
        create_refresh_token = JWTAuthentication.create_refresh_token(user)
        user.set_last_login_now()

        return Response({
            'access': jwt_token,
            'refresh': create_refresh_token
        })


class UserViewSet(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    filterset_fields = ['email']
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == 'update':
            serializer = UpdateUserSerializer
        elif self.action == 'partial_update':
            serializer = UpdateUserSerializer
        elif self.action == 'reset_password':
            serializer = ResetPasswordSerializer

        return serializer

    @action(methods=['GET'], detail=False, url_path='me')
    def me(self, requests, *args, **kwargs) -> Response:
        if self.request.user.is_authenticated:
            try:
                user = self.request.user
                serializer = self.get_serializer(user)
                return Response(serializer.data)
            except Exception as e:
                log_exception(e, 'Error user me')

        return Response(status=status.HTTP_404_NOT_FOUND)

    @action(methods=['POST'], detail=False, url_path='reset-password')
    def reset_password(self, request, *args, **kwargs) -> Response:
        try:
            user = request.user
            if user is None or not user.is_active:
                return Response(
                    data={'message': 'User not found or user not active', 'detail_code': 'user_not_fount_or_not_active'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user.set_password(serializer.data.get('password'))
            user.save()

            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            log_exception(e, f'Failed to reset password {str(e)}')
            return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class UserForgotPasswordByEmailView(
    generics.GenericAPIView
):
    queryset = User.objects.all()
    serializer_class = ForgotPasswordSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs) -> Response:
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            email_verified = cache.get(request.data.get('email'))
            if email_verified:
                serializer.save()
                cache.delete(request.data.get('email'))
                return Response(status=200)

            return Response(
                data={'message': 'Email not verified', 'detail_code': 'email_not_verified'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        except Exception as e:
            log_exception(e, f'Failed to reset password {str(e)}')
            return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeByEmailView(
    generics.GenericAPIView
):
    queryset = User.objects.all()
    serializer_class = VerifySmsCodeSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs) -> Response:
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            email = serializer.data.get('email')
            code = serializer.data.get('code')
            user = User.objects.filter(email=email).first()
            log_message(f"verify_email_code email {email}, code {code}")
            if user is not None:
                cache_key = f'confirmation_code:{user.id}'
                confirmation_code = cache.get(cache_key)
                log_message(f"cache_key {cache_key}, code {code}, confirmation_code {confirmation_code}")
                if confirmation_code == code:
                    cache.set(email, True)
                    return Response(status=status.HTTP_200_OK)

            return Response(data={"detail": f"Failed verify sms code {code}"}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            log_exception(e, f'Failed verify sms code {str(e)}')
            return Response(data={'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendVerifyCodeByEmailView(
    generics.GenericAPIView
):
    queryset = User.objects.all()
    serializer_class = ForgotPasswordSerializer
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data.get('email')
        try:
            user = User.objects.filter(email=email).first()
            if user is not None:
                confirmation_key = f'confirmation_resend_{user.id}'
                confirmation_resend_time = cache.get(confirmation_key)

                confirmation_ty_key = f'confirmation_resend_try_{user.id}'
                confirmation_resend_try_count = cache.get(confirmation_ty_key)

                log_message(
                    f"confirmation_key {confirmation_key}, confirmation_resend_time {confirmation_resend_time}, "
                    f"confirmation_ty_key {confirmation_ty_key}, "
                    f"confirmation_resend_try_count {confirmation_resend_try_count}"
                )

                if confirmation_resend_time is None or has_passed_2_minutes(confirmation_resend_time):

                    if confirmation_resend_try_count is not None and confirmation_resend_try_count > 3:
                        return Response(
                            data={"message": "Too many activation code resend requests, wait 1 day."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    confirmation_code = generate_activation_code()

                    cache_key = f'confirmation_code:{user.id}'
                    cache.set(cache_key, confirmation_code)

                    resend_key = f'confirmation_resend_{user.id}'
                    cache.set(resend_key, datetime.now())

                    if confirmation_resend_try_count:
                        resend_ty_key = f'confirmation_resend_try_{user.id}'
                        cache.set(resend_ty_key, confirmation_resend_try_count + 1)
                    else:
                        resend_ty_key = f'confirmation_resend_try_{user.id}'
                        cache.set(resend_ty_key, 1)

                    send_email.delay(
                        "Код подтверждения",
                        [email],
                        'email/confirmation_notification.html',
                        {'text': confirmation_code, 'from_email': 'info@example.com'}
                    )
                    log_message(f"cache_key {cache_key}, confirmation_code {confirmation_code}")
                else:
                    return Response(
                        data={"message": "Please wait 2 minutes to resend the activation code."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            log_exception(e, 'Error in send_confirmation_code')
            return Response(
                data={"message": "Confirmation code error"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data={"message": "Confirmation code sended"},
            status=status.HTTP_200_OK
        )


class UserCreateView(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = CreateUserSerializer
    authentication_classes = []
    permission_classes = []


class UserAvatarViewSet(
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    serializer_class = UserAvatarUploadSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_serializer_class(self):
        serializer = self.serializer_class
        if self.action == 'delete_avatar':
            serializer = None

        return serializer

    @action(detail=True, methods=['post'], url_path='upload')
    def upload_avatar(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'], url_path='delete')
    def delete_avatar(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        avatar_path = user.avatar.name
        try:
            delete_file(avatar_path)
            user.avatar.delete(save=True)
            user.save()
        except Exception as e:
            log_exception(e, f"Error deleting user avatar from MinIO {avatar_path}")
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserCheckEmailView(
    generics.GenericAPIView
):
    serializer_class = CheckEmailSerializer
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs) -> Response:
        email = request.data.get('email')
        if User.objects.filter(email=email).exists():
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserActivateView(
    generics.GenericAPIView
):
    serializer_class = UserActivateSerializer
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs) -> Response:
        email = request.data.get('email')
        code = request.data.get('code')
        user = User.objects.filter(email=email).first()

        log_message(f"email {email} user {user}, code {code}")
        if user is not None:
            try_key = f'activation_try_{user.id}'
            activation_try = cache.get(try_key)

            try_time_key = f'activation_try_time_{user.id}'
            try_time = cache.get(try_time_key)

            if activation_try is None or has_passed_30_minutes(try_time):
                try_time_key = f'activation_try_time_{user.id}'
                activation_try = 1
                cache.set(try_time_key, datetime.now())

            if activation_try and activation_try > 3:
                return Response(
                    data={"message": "Too many failed attempts, please try again after 30min"},
                    status=status.HTTP_200_OK
                )

            cache_key = f'activation_code:{user.id}'
            activation_code = cache.get(cache_key)

            log_message(f"cache_key {cache_key}, activation_code {activation_code}")
            if activation_code and code == activation_code:
                update_instance(user, {'is_active': True})
                return Response(
                    data={"message": "User activated"},
                    status=status.HTTP_200_OK
                )
            activation_try += 1
            cache.set(try_key, activation_try)
        return Response(
            data={"message": "Activation code error"},
            status=status.HTTP_400_BAD_REQUEST
        )


class ResendActivateView(
    generics.GenericAPIView
):
    serializer_class = UserEmailSerializer
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs) -> Response:
        email = request.data.get('email')

        try:
            user = User.objects.filter(email=email).first()
            if user is not None:
                resend_key = f'activation_resend_{user.id}'
                activation_resend_time = cache.get(resend_key)

                resend_ty_key = f'activation_resend_try_{user.id}'
                activation_resend_try_count = cache.get(resend_ty_key)

                if activation_resend_time is None or has_passed_2_minutes(activation_resend_time):

                    if activation_resend_try_count is not None and activation_resend_try_count > 3:
                        return Response(
                            data={"message": "Too many activation code resend requests, wait 1 day."},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    activation_code = generate_activation_code()
                    self.set_activation_code(user.id, activation_code)
                    self.set_resend_time(user.id)
                    self.set_resend_try_count(user.id, activation_resend_try_count)

                    log_message(f"user {user}, activation_code {activation_code}")
                    send_email.delay(
                        "Код активации",
                        [email],
                        'email/resend_notification.html',
                        {'text': activation_code, 'from_email': 'info@example.com'}
                    )
                else:
                    return Response(
                        data={"message": "Please wait 2 minutes to resend the activation code."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        except Exception as e:
            log_exception(e, 'Error in send_activation_code')
            return Response(
                data={"message": "Activation code error"},
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            data={"message": "Activation code sended"},
            status=status.HTTP_200_OK
        )

    def set_activation_code(self, user_id: int, activation_code) -> None:
        cache_key = f'activation_code:{user_id}'
        cache.set(cache_key, activation_code)

    def set_resend_time(self, user_id: int) -> None:
        resend_key = f'activation_resend_{user_id}'
        cache.set(resend_key, datetime.now())

    def set_resend_try_count(self, user_id: int, activation_resend_try_count) -> None:
        if activation_resend_try_count:
            resend_ty_key = f'activation_resend_try_{user_id}'
            cache.set(resend_ty_key, activation_resend_try_count + 1)
        else:
            resend_ty_key = f'activation_resend_try_{user_id}'
            cache.set(resend_ty_key, 1)


class UserPolicyView(
    generics.GenericAPIView
):
    serializer_class = UserActivateSerializer
    authentication_classes = []
    permission_classes = []
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs) -> HttpResponse:
        try:
            pdf_path = '/code/templates/static/политики_конфиденциальности.pdf'
            if os.path.exists(pdf_path):
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_data = pdf_file.read()
                    response = HttpResponse(pdf_data, content_type='application/pdf')
                    response['Content-Disposition'] = 'inline; filename="file.pdf"'

                    return response
            else:
                return Response({'error': 'Policy file not found'}, status=404)
        except Exception as e:
            log_exception(e, 'Error policy file not found')
