from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.settings import api_settings

User = get_user_model()


def serialize_user(user) -> dict:
    profile = getattr(user, 'profile', None)
    display_name = ''
    role = 'reader'
    bio = ''
    avatar = ''
    if profile:
        display_name = profile.display_name or user.get_full_name() or user.username
        role = profile.role
        bio = profile.bio or ''
        avatar = profile.avatar or ''
    else:
        display_name = user.get_full_name() or user.username
    is_staff = bool(user.is_staff)
    is_author = is_staff or role == 'author'
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'displayName': display_name,
        'role': 'staff' if is_staff else role,
        'isStaff': is_staff,
        'isAuthor': is_author,
        'bio': bio,
        'avatar': avatar,
    }


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.EmailField()
    displayName = serializers.CharField()
    role = serializers.CharField()
    isStaff = serializers.BooleanField()
    isAuthor = serializers.BooleanField()
    bio = serializers.CharField()
    avatar = serializers.CharField()


class ProfileUpdateSerializer(serializers.Serializer):
    displayName = serializers.CharField(required=False, allow_blank=True, max_length=64)
    bio = serializers.CharField(required=False, allow_blank=True, max_length=500)
    avatar = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def update(self, instance, validated_data):
        profile = getattr(instance, 'profile', None)
        if not profile:
            from .models import Profile

            profile, _ = Profile.objects.get_or_create(user=instance)
        if 'displayName' in validated_data:
            profile.display_name = validated_data['displayName'].strip()
        if 'bio' in validated_data:
            profile.bio = validated_data['bio'].strip()
        if 'avatar' in validated_data:
            profile.avatar = validated_data['avatar'].strip()
        profile.save()
        return instance


class ChangePasswordSerializer(serializers.Serializer):
    currentPassword = serializers.CharField(write_only=True)
    newPassword = serializers.CharField(min_length=8, max_length=128, write_only=True)

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.check_password(attrs['currentPassword']):
            raise serializers.ValidationError({'currentPassword': '当前密码不正确'})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['newPassword'])
        user.save(update_fields=['password'])
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value: str) -> str:
        return value.strip().lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    token = serializers.CharField()
    newPassword = serializers.CharField(min_length=8, max_length=128, write_only=True)


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, max_length=128, write_only=True)
    displayName = serializers.CharField(required=False, allow_blank=True, max_length=64)

    def validate_email(self, value: str) -> str:
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError('该邮箱已注册')
        return email

    def create(self, validated_data):
        email = validated_data['email']
        password = validated_data['password']
        display_name = validated_data.get('displayName', '').strip()

        username = email.split('@')[0] or 'user'
        base = username
        suffix = 1
        while User.objects.filter(username=username).exists():
            username = f'{base}{suffix}'
            suffix += 1

        user = User.objects.create_user(username=username, email=email, password=password)
        if display_name:
            profile = getattr(user, 'profile', None)
            if profile:
                profile.display_name = display_name
                profile.save(update_fields=['display_name'])
        return user


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
