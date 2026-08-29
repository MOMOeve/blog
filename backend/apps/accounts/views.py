import secrets
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .models import PasswordResetToken
from .serializers import (
    ChangePasswordSerializer,
    EmailTokenObtainPairSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ProfileUpdateSerializer,
    RegisterSerializer,
    SiteAboutUpdateSerializer,
    UserSerializer,
    serialize_site_about,
    serialize_user,
)

User = get_user_model()


class RegisterView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serialize_user(user),
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = serialize_user(request.user)
        return Response(UserSerializer(data).data)

    def patch(self, request):
        serializer = ProfileUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(request.user, serializer.validated_data)
        data = serialize_user(request.user)
        return Response(UserSerializer(data).data)


class SiteAuthorView(APIView):
    """公开站点作者资料（取首个 staff），供侧栏等展示。"""

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        data = serialize_site_about()
        return Response(
            {
                'displayName': data['displayName'],
                'bio': data['body'],
                'avatar': data['avatar'],
            }
        )


class SiteAboutView(APIView):
    """公开关于页完整配置；staff 可 PATCH 更新。"""

    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [permissions.AllowAny()]
        return [permissions.IsAdminUser()]

    def get(self, request):
        return Response(serialize_site_about())

    def patch(self, request):
        from .models import SiteAbout

        about = SiteAbout.get_solo()
        serializer = SiteAboutUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.update(about, serializer.validated_data)
        return Response(serialize_site_about())


class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': '密码已更新'})


class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            pass
        else:
            token = secrets.token_urlsafe(32)
            expires_at = timezone.now() + timedelta(hours=1)
            PasswordResetToken.objects.create(user=user, token=token, expires_at=expires_at)

            reset_path = f'/reset-password?token={token}'
            reset_url = request.build_absolute_uri(reset_path)
            send_mail(
                subject='星野文记 · 重置密码',
                message=f'请在 1 小时内打开以下链接重置密码：\n\n{reset_url}\n',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=[user.email],
                fail_silently=True,
            )

        return Response({'detail': '若该邮箱已注册，将收到重置链接'})


class PasswordResetConfirmView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token_value = serializer.validated_data['token']
        new_password = serializer.validated_data['newPassword']

        try:
            token = PasswordResetToken.objects.select_related('user').get(token=token_value)
        except PasswordResetToken.DoesNotExist:
            return Response({'detail': '链接无效或已过期'}, status=status.HTTP_400_BAD_REQUEST)

        if not token.is_valid():
            return Response({'detail': '链接无效或已过期'}, status=status.HTTP_400_BAD_REQUEST)

        user = token.user
        user.set_password(new_password)
        user.save(update_fields=['password'])
        token.used = True
        token.save(update_fields=['used'])
        PasswordResetToken.objects.filter(user=user, used=False).update(used=True)

        return Response({'detail': '密码已重置，请使用新密码登录'})


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh = request.data.get('refresh')
        if not refresh:
            return Response({'detail': '缺少 refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh)
            token.blacklist()
        except Exception:
            return Response({'detail': '无效的 refresh token'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]
