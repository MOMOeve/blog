from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.content.views import IsStaffOrReadOnly

from .models import Photo
from .serializers import PhotoSerializer


class PhotoViewSet(viewsets.ModelViewSet):
    serializer_class = PhotoSerializer
    permission_classes = [IsStaffOrReadOnly]
    pagination_class = None

    def get_queryset(self):
        qs = Photo.objects.all()
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(published=True)

        category = self.request.query_params.get('category')
        if category and category != '全部':
            qs = qs.filter(category=category)
        return qs

    @action(detail=False, methods=['get'], url_path='categories-list', permission_classes=[permissions.AllowAny])
    def categories_list(self, request):
        names = list(
            Photo.objects.filter(published=True)
            .values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )
        return Response(['全部', *names])
