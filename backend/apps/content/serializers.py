from rest_framework import serializers

from .models import Category, Post, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']


class PostListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name')
    tags = serializers.SlugRelatedField(many=True, read_only=True, slug_field='name')
    date = serializers.SerializerMethodField()
    readTime = serializers.CharField(source='read_time')
    titleEn = serializers.CharField(source='title_en')
    img = serializers.SerializerMethodField()
    viewCount = serializers.IntegerField(source='view_count', read_only=True)
    likeCount = serializers.IntegerField(source='like_count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id',
            'title',
            'titleEn',
            'category',
            'date',
            'readTime',
            'excerpt',
            'img',
            'featured',
            'tags',
            'published',
            'viewCount',
            'likeCount',
        ]

    def get_date(self, obj: Post) -> str:
        dt = obj.published_at or obj.created_at
        if not dt:
            return ''
        return f'{dt.year}年{dt.month}月{dt.day}日'

    def get_img(self, obj: Post) -> str:
        """返回相对路径，避免反向代理下绝对 URL 端口/域名错误导致封面裂图。"""
        url = (obj.cover_image or '').strip()
        if not url:
            return ''
        if url.startswith(('http://', 'https://')):
            from urllib.parse import urlparse

            path = urlparse(url).path or ''
            if path.startswith('/media/'):
                return path
            return url
        return url if url.startswith('/') else f'/{url}'


class PostDetailSerializer(PostListSerializer):
    body = serializers.CharField()
    liked = serializers.SerializerMethodField()
    related = serializers.SerializerMethodField()
    prev = serializers.SerializerMethodField()
    next = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ['body', 'liked', 'related', 'prev', 'next']

    def get_liked(self, obj: Post) -> bool:
        request = self.context.get('request')
        if not request:
            return False
        from .services import user_has_liked

        return user_has_liked(obj, request)

    def get_related(self, obj: Post):
        from .services import get_related_posts

        qs = get_related_posts(obj)
        return PostListSerializer(qs, many=True, context=self.context).data

    def get_prev(self, obj: Post):
        from .services import get_prev_next, serialize_nav_post

        prev_post, _ = get_prev_next(obj)
        return serialize_nav_post(prev_post)

    def get_next(self, obj: Post):
        from .services import get_prev_next, serialize_nav_post

        _, next_post = get_prev_next(obj)
        return serialize_nav_post(next_post)


class PostWriteSerializer(serializers.ModelSerializer):
    """前台写文章：Markdown 正文存在 body；分类/标签按名称自动创建。"""

    category = serializers.CharField()
    tags = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)
    titleEn = serializers.CharField(source='title_en', required=False, allow_blank=True)
    readTime = serializers.CharField(source='read_time', required=False, allow_blank=True)
    img = serializers.CharField(source='cover_image', required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)
    featured = serializers.BooleanField(required=False)
    published = serializers.BooleanField(required=False)

    class Meta:
        model = Post
        fields = [
            'title',
            'titleEn',
            'category',
            'tags',
            'excerpt',
            'body',
            'img',
            'readTime',
            'featured',
            'published',
        ]

    def _resolve_category(self, name: str) -> Category:
        name = name.strip()
        if not name:
            raise serializers.ValidationError({'category': '分类不能为空'})
        category, _ = Category.objects.get_or_create(name=name)
        return category

    def _resolve_tags(self, names: list[str]) -> list[Tag]:
        tags = []
        for raw in names:
            name = raw.strip()
            if not name:
                continue
            tag, _ = Tag.objects.get_or_create(name=name)
            tags.append(tag)
        return tags

    def create(self, validated_data):
        category_name = validated_data.pop('category')
        tag_names = validated_data.pop('tags', [])
        post = Post.objects.create(
            category=self._resolve_category(category_name),
            **validated_data,
        )
        if tag_names:
            post.tags.set(self._resolve_tags(tag_names))
        return post

    def update(self, instance, validated_data):
        category_name = validated_data.pop('category', None)
        tag_names = validated_data.pop('tags', None)
        if category_name is not None:
            instance.category = self._resolve_category(category_name)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if tag_names is not None:
            instance.tags.set(self._resolve_tags(tag_names))
        return instance
