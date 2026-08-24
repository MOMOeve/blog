"""文章互动与导航辅助逻辑。"""

from __future__ import annotations

from django.db.models import Count, Q

from .models import Post, PostLike, PostViewRecord


def get_visitor_id(request) -> str:
    return (request.headers.get('X-Visitor-Id') or request.META.get('REMOTE_ADDR') or 'anonymous')[:64]


def user_has_liked(post: Post, request) -> bool:
    if request.user and request.user.is_authenticated:
        return PostLike.objects.filter(post=post, user=request.user).exists()
    visitor_id = get_visitor_id(request)
    return PostLike.objects.filter(post=post, visitor_id=visitor_id, user__isnull=True).exists()


def record_view(post: Post, request) -> int:
    visitor_id = get_visitor_id(request)
    _, created = PostViewRecord.objects.get_or_create(post=post, visitor_id=visitor_id)
    if created:
        Post.objects.filter(pk=post.pk).update(view_count=post.view_count + 1)
        post.view_count += 1
    return post.view_count


def toggle_like(post: Post, request) -> tuple[int, bool]:
    if request.user and request.user.is_authenticated:
        like = PostLike.objects.filter(post=post, user=request.user).first()
        if like:
            like.delete()
            Post.objects.filter(pk=post.pk, like_count__gt=0).update(like_count=post.like_count - 1)
            post.like_count = max(0, post.like_count - 1)
            return post.like_count, False
        PostLike.objects.create(post=post, user=request.user)
        Post.objects.filter(pk=post.pk).update(like_count=post.like_count + 1)
        post.like_count += 1
        return post.like_count, True

    visitor_id = get_visitor_id(request)
    like = PostLike.objects.filter(post=post, visitor_id=visitor_id, user__isnull=True).first()
    if like:
        like.delete()
        Post.objects.filter(pk=post.pk, like_count__gt=0).update(like_count=post.like_count - 1)
        post.like_count = max(0, post.like_count - 1)
        return post.like_count, False
    PostLike.objects.create(post=post, visitor_id=visitor_id)
    Post.objects.filter(pk=post.pk).update(like_count=post.like_count + 1)
    post.like_count += 1
    return post.like_count, True


def get_related_posts(post: Post, limit: int = 3):
    tag_ids = list(post.tags.values_list('id', flat=True))
    qs = Post.objects.filter(published=True).exclude(pk=post.pk).select_related('category').prefetch_related('tags')
    if tag_ids:
        qs = (
            qs.filter(tags__in=tag_ids)
            .annotate(tag_match=Count('tags', filter=Q(tags__in=tag_ids)))
            .order_by('-tag_match', '-published_at', '-pk')
        )
    else:
        qs = qs.filter(category=post.category).order_by('-published_at', '-pk')
    return qs.distinct()[:limit]


def get_prev_next(post: Post):
    if not post.published:
        return None, None
    dt = post.published_at or post.created_at
    prev_post = (
        Post.objects.filter(published=True)
        .filter(Q(published_at__lt=dt) | Q(published_at=dt, pk__lt=post.pk))
        .order_by('-published_at', '-pk')
        .first()
    )
    next_post = (
        Post.objects.filter(published=True)
        .filter(Q(published_at__gt=dt) | Q(published_at=dt, pk__gt=post.pk))
        .order_by('published_at', 'pk')
        .first()
    )
    return prev_post, next_post


def serialize_nav_post(post: Post | None) -> dict | None:
    if not post:
        return None
    return {'id': post.id, 'title': post.title}
