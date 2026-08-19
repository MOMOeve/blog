from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()


def serialize_user(user) -> dict:
    profile = getattr(user, 'profile', None)
    display_name = ''
    if profile and profile.display_name:
        display_name = profile.display_name
    else:
        display_name = user.get_full_name() or user.username
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'displayName': display_name,
        'isStaff': bool(user.is_staff),
    }


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    displayName = serializers.CharField()
    isStaff = serializers.BooleanField()


class EmailTokenObtainPairSerializer(TokenObtainPairSerializer):
    """用邮箱 + 密码换取 JWT，并附带 user 信息。"""

    username_field = User.EMAIL_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(User.USERNAME_FIELD, None)
        self.fields['email'] = serializers.EmailField(write_only=True)
        self.fields['password'] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email', '').strip().lower()
        password = attrs.get('password', '')
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist as exc:
            raise serializers.ValidationError({'detail': '邮箱或密码错误'}) from exc

        if not user.check_password(password):
            raise serializers.ValidationError({'detail': '邮箱或密码错误'})
        if not user.is_active:
            raise serializers.ValidationError({'detail': '账号已禁用'})

        refresh = self.get_token(user)
        data = {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': serialize_user(user),
        }
        if api_settings.UPDATE_LAST_LOGIN:
            update_last_login(None, user)
        return data
