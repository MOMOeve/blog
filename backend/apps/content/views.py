from django.db.models import Q
from django.utils import timezone
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Post, Tag
from .serializers import (
    CategorySerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostWriteSerializer,
    TagSerializer,
)


class IsStaffOrReadOnly(permissions.BasePermission):
    """访客只读；工作人员可写。"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class PostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsStaffOrReadOnly]

    def get_queryset(self):
        qs = Post.objects.select_related('category', 'author').prefetch_related('tags')
        if not (self.request.user and self.request.user.is_staff):
            qs = qs.filter(published=True)

        category = self.request.query_params.get('category')
        if category and category != '全部':
            qs = qs.filter(category__name=category)

        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(excerpt__icontains=search))

        featured = self.request.query_params.get('featured')
        if featured in {'1', 'true', 'True'}:
            qs = qs.filter(featured=True)

        published = self.request.query_params.get('published')
        if published is not None:
            is_staff = bool(self.request.user and self.request.user.is_staff)
            if published.lower() in {'0', 'false'}:
                if is_staff:
                    qs = qs.filter(published=False)
                else:
                    qs = qs.filter(published=True)
            elif published.lower() in {'1', 'true'}:
                qs = qs.filter(published=True)

        ordering = self.request.query_params.get('ordering', '-published_at')
        if ordering in {
            'published_at',
            '-published_at',
            'created_at',
            '-created_at',
            'updated_at',
            '-updated_at',
        }:
            qs = qs.order_by(ordering)
        return qs.distinct()

    def get_serializer_class(self):
        if self.action in {'create', 'update', 'partial_update'}:
            return PostWriteSerializer
        if self.action == 'retrieve':
            return PostDetailSerializer
        return PostListSerializer

    def perform_create(self, serializer):
        published = serializer.validated_data.get('published', True)
        serializer.save(
            author=self.request.user,
            published_at=timezone.now() if published else None,
        )

    def perform_update(self, serializer):
        published = serializer.validated_data.get('published', serializer.instance.published)
        extra = {}
        if published and not serializer.instance.published_at:
            extra['published_at'] = timezone.now()
        serializer.save(**extra)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        out = PostDetailSerializer(serializer.instance, context=self.get_serializer_context())
        headers = self.get_success_headers(out.data)
        return Response(out.data, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        out = PostDetailSerializer(serializer.instance, context=self.get_serializer_context())
        return Response(out.data)

    @action(detail=False, methods=['get'], url_path='categories-list')
    def categories_list(self, request):
        names = ['全部'] + list(Category.objects.values_list('name', flat=True))
        return Response(names)
