from django.utils import timezone
from django.utils.feedgenerator import Rss201rev2Feed
from django.utils.html import strip_tags
from django.http import HttpResponse

from .models import Post


def rss_feed(request):
    site = request.build_absolute_uri('/')
    feed = Rss201rev2Feed(
        title='星野文记',
        link=site,
        description='代码与语言，慢慢来',
        language='zh-cn',
    )
    posts = (
        Post.objects.filter(published=True)
        .select_related('category', 'author')
        .order_by('-published_at', '-created_at')[:40]
    )
    for post in posts:
        link = request.build_absolute_uri(f'/articles/{post.id}')
        published = post.published_at or post.created_at or timezone.now()
        feed.add_item(
            title=post.title,
            link=link,
            description=post.excerpt or strip_tags(post.body)[:280],
            pubdate=published,
            unique_id=str(post.id),
            categories=[post.category.name] if post.category_id else None,
        )
    return HttpResponse(feed.writeString('utf-8'), content_type='application/rss+xml; charset=utf-8')


def sitemap_feed(request):
    site = request.build_absolute_uri('/').rstrip('/')
    static_paths = ['/', '/articles', '/photography', '/about', '/contact']
    posts = (
        Post.objects.filter(published=True)
        .only('id', 'updated_at', 'published_at', 'created_at')
        .order_by('-published_at', '-created_at')
    )

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path in static_paths:
        lines.append('  <url>')
        lines.append(f'    <loc>{site}{path if path != "/" else "/"}</loc>')
        lines.append('  </url>')
    for post in posts:
        dt = post.updated_at or post.published_at or post.created_at
        lastmod = dt.strftime('%Y-%m-%d') if dt else ''
        lines.append('  <url>')
        lines.append(f'    <loc>{site}/articles/{post.id}</loc>')
        if lastmod:
            lines.append(f'    <lastmod>{lastmod}</lastmod>')
        lines.append('  </url>')
    lines.append('</urlset>')
    return HttpResponse('\n'.join(lines), content_type='application/xml; charset=utf-8')
