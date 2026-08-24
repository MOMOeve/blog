from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.content.views import IsStaffOrReadOnly

from .models import Photo
from .serializers import PhotoSerializer, PhotoWriteSerializer


class PhotoViewSet(viewsets.ModelViewSet):
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

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return PhotoWriteSerializer
        return PhotoSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        out = PhotoSerializer(serializer.instance, context=self.get_serializer_context())
        return Response(out.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        out = PhotoSerializer(serializer.instance, context=self.get_serializer_context())
        return Response(out.data)

    @action(detail=False, methods=['get'], url_path='categories-list', permission_classes=[permissions.AllowAny])
    def categories_list(self, request):
        names = list(
            Photo.objects.filter(published=True)
            .values_list('category', flat=True)
            .distinct()
            .order_by('category')
        )
        return Response(['全部', *names])
