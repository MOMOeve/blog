from django.db.models import Count, Q

from django.db.models.functions import ExtractMonth, ExtractYear

from rest_framework import permissions, status, viewsets

from rest_framework.decorators import action

from rest_framework.response import Response



from apps.accounts.permissions import user_can_write_content, user_is_author



from .comment_serializers import CommentSerializer, CommentWriteSerializer

from .models import Category, Comment, Post, Tag

from .serializers import (

    CategorySerializer,

    PostDetailSerializer,

    PostListSerializer,

    PostWriteSerializer,

    TagSerializer,

)

from .services import record_view, toggle_like





class IsStaffOrReadOnly(permissions.BasePermission):
    """访客只读；工作人员可写（摄影等后台功能）。"""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IsAuthorStaffOrReadOnly(permissions.BasePermission):

    """访客只读；作者可写自己的内容；工作人员可写全部。"""



    def has_permission(self, request, view):

        if request.method in permissions.SAFE_METHODS:

            return True

        return user_can_write_content(request.user)



    def has_object_permission(self, request, view, obj):

        if request.method in permissions.SAFE_METHODS:

            return True

        if request.user and request.user.is_staff:

            return True

        if user_is_author(request.user) and obj.author_id == request.user.id:

            return True

        return False





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

    permission_classes = [IsAuthorStaffOrReadOnly]



    def get_queryset(self):

        qs = Post.objects.select_related('category', 'author').prefetch_related('tags')

        user = self.request.user

        is_staff = bool(user and user.is_staff)

        is_author = user_is_author(user)



        if is_staff:

            pass

        elif is_author and user.is_authenticated:

            qs = qs.filter(Q(published=True) | Q(author=user))

        else:

            qs = qs.filter(published=True)



        category = self.request.query_params.get('category')

        if category and category != '全部':

            qs = qs.filter(category__name=category)



        tag = self.request.query_params.get('tag')

        if tag:

            qs = qs.filter(tags__name=tag)



        year = self.request.query_params.get('year')

        if year and year.isdigit():

            qs = qs.filter(published_at__year=int(year))



        month = self.request.query_params.get('month')

        if month and month.isdigit():

            qs = qs.filter(published_at__month=int(month))



        search = self.request.query_params.get('search')

        if search:

            qs = qs.filter(Q(title__icontains=search) | Q(excerpt__icontains=search))



        featured = self.request.query_params.get('featured')

        if featured in {'1', 'true', 'True'}:

            qs = qs.filter(featured=True)



        published = self.request.query_params.get('published')

        if published is not None:

            if published.lower() in {'0', 'false'}:

                if is_staff or is_author:

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



    def retrieve(self, request, *args, **kwargs):

        instance = self.get_object()

        if instance.published or (request.user and request.user.is_staff):

            record_view(instance, request)

            instance.refresh_from_db(fields=['view_count', 'like_count'])

        serializer = self.get_serializer(instance)

        return Response(serializer.data)



    def perform_create(self, serializer):

        from django.utils import timezone



        published = serializer.validated_data.get('published', True)

        serializer.save(

            author=self.request.user,

            published_at=timezone.now() if published else None,

        )



    def perform_update(self, serializer):

        from django.utils import timezone



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



    @action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])

    def like(self, request, pk=None):

        post = self.get_object()

        if not post.published and not (request.user and request.user.is_staff):

            return Response({'detail': '文章不存在'}, status=status.HTTP_404_NOT_FOUND)

        count, liked = toggle_like(post, request)

        return Response({'likeCount': count, 'liked': liked})



    @action(detail=True, methods=['get', 'post'], url_path='comments')

    def comments(self, request, pk=None):

        post = self.get_object()

        if request.method == 'GET':

            qs = post.comments.filter(approved=True).select_related('author', 'author__profile')

            if request.user and request.user.is_staff:

                qs = post.comments.select_related('author', 'author__profile').all()

            return Response(CommentSerializer(qs, many=True).data)



        if not request.user or not request.user.is_authenticated:

            return Response({'detail': '请先登录后再评论'}, status=status.HTTP_401_UNAUTHORIZED)



        serializer = CommentWriteSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        comment = Comment.objects.create(

            post=post,

            author=request.user,

            body=serializer.validated_data['body'],

            approved=False,

        )

        return Response(

            {

                **CommentSerializer(comment).data,

                'detail': '评论已提交，审核通过后将显示',

            },

            status=status.HTTP_201_CREATED,

        )



    @action(detail=False, methods=['get'], url_path='categories-list')

    def categories_list(self, request):

        names = ['全部'] + list(Category.objects.values_list('name', flat=True))

        return Response(names)



    @action(detail=False, methods=['get'], url_path='tag-cloud')

    def tag_cloud(self, request):

        rows = (

            Tag.objects.filter(posts__published=True)

            .annotate(count=Count('posts', distinct=True))

            .filter(count__gt=0)

            .order_by('-count', 'name')

            .values('name', 'count')

        )

        return Response(list(rows))



    @action(detail=False, methods=['get'], url_path='archive')

    def archive(self, request):

        rows = (

            Post.objects.filter(published=True, published_at__isnull=False)

            .annotate(year=ExtractYear('published_at'), month=ExtractMonth('published_at'))

            .values('year', 'month')

            .annotate(count=Count('id'))

            .order_by('-year', '-month')

        )

        return Response(list(rows))

