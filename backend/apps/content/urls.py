from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .feed import rss_feed, sitemap_feed
from .views import CategoryViewSet, PostViewSet, TagViewSet

router = DefaultRouter()
router.register('posts', PostViewSet, basename='post')
router.register('categories', CategoryViewSet, basename='category')
router.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('feed/rss/', rss_feed, name='rss-feed'),
    path('feed/sitemap.xml', sitemap_feed, name='sitemap-feed'),
    path('', include(router.urls)),
]
