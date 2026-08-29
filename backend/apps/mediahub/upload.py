from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from rest_framework import parsers, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

ALLOWED_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'image/gif',
    'image/svg+xml',
}
MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5MB


from apps.accounts.permissions import user_can_write_content


class IsAuthorOrStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return user_can_write_content(request.user)


class IsAuthenticatedUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class AvatarUploadView(APIView):
    """登录用户上传头像。"""

    permission_classes = [IsAuthenticatedUser]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    MAX_AVATAR_BYTES = 2 * 1024 * 1024

    def post(self, request):
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': '请选择图片文件（字段名 file）'}, status=status.HTTP_400_BAD_REQUEST)

        content_type = (upload.content_type or '').lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            return Response({'detail': '仅支持 jpg / png / webp / gif / svg'}, status=status.HTTP_400_BAD_REQUEST)

        if upload.size and upload.size > self.MAX_AVATAR_BYTES:
            return Response({'detail': '头像不能超过 2MB'}, status=status.HTTP_400_BAD_REQUEST)

        ext = Path(upload.name).suffix.lower()
        if ext not in {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}:
            ext = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/webp': '.webp',
                'image/gif': '.gif',
                'image/svg+xml': '.svg',
            }.get(content_type, '.bin')

        folder = timezone.now().strftime('uploads/avatars/%Y/%m')
        filename = f'{uuid4().hex}{ext}'
        saved_path = default_storage.save(f'{folder}/{filename}', upload)
        relative_url = f'/{settings.MEDIA_URL.strip("/")}/{saved_path.lstrip("/")}'
        absolute_url = request.build_absolute_uri(relative_url)

        return Response(
            {
                'url': absolute_url,
                'path': relative_url,
            },
            status=status.HTTP_201_CREATED,
        )


class MediaUploadView(APIView):
    """作者/Staff 上传图片到 MEDIA，返回可访问 URL。"""

    permission_classes = [IsAuthorOrStaff]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        upload = request.FILES.get('file')
        if not upload:
            return Response({'detail': '请选择图片文件（字段名 file）'}, status=status.HTTP_400_BAD_REQUEST)

        content_type = (upload.content_type or '').lower()
        if content_type not in ALLOWED_CONTENT_TYPES:
            return Response({'detail': '仅支持 jpg / png / webp / gif / svg'}, status=status.HTTP_400_BAD_REQUEST)

        if upload.size and upload.size > MAX_UPLOAD_BYTES:
            return Response({'detail': '图片不能超过 5MB'}, status=status.HTTP_400_BAD_REQUEST)

        ext = Path(upload.name).suffix.lower()
        if ext not in {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.svg'}:
            # 按 content-type 补后缀
            ext = {
                'image/jpeg': '.jpg',
                'image/png': '.png',
                'image/webp': '.webp',
                'image/gif': '.gif',
                'image/svg+xml': '.svg',
            }.get(content_type, '.bin')

        folder = timezone.now().strftime('uploads/%Y/%m')
        filename = f'{uuid4().hex}{ext}'
        saved_path = default_storage.save(f'{folder}/{filename}', upload)
        relative_url = f'/{settings.MEDIA_URL.strip("/")}/{saved_path.lstrip("/")}'
        absolute_url = request.build_absolute_uri(relative_url)

        return Response(
            {
                'url': absolute_url,
                'path': relative_url,
                'name': upload.name,
                'size': upload.size,
            },
            status=status.HTTP_201_CREATED,
        )
