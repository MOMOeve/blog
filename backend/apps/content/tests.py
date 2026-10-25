from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.content.models import Category, Post, Tag

User = get_user_model()


class ContentMetaTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='demo', email='demo@test.com', password='demo1234', is_staff=True)
        Profile.objects.filter(user=self.user).update(role=Profile.ROLE_AUTHOR)
        self.category = Category.objects.create(name='技术')
        self.tag = Tag.objects.create(name='Vue')
        Post.objects.create(
            title='测试文章',
            category=self.category,
            excerpt='摘要',
            body='正文',
            published=True,
            author=self.user,
            published_at=timezone.now(),
        ).tags.add(self.tag)

    def test_tag_cloud(self):
        res = self.client.get('/api/v1/posts/tag-cloud/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data[0]['name'], 'Vue')
        self.assertEqual(res.data[0]['count'], 1)

    def test_archive(self):
        res = self.client.get('/api/v1/posts/archive/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(res.data), 1)

    def test_filter_by_tag(self):
        res = self.client.get('/api/v1/posts/', {'tag': 'Vue'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 1)

    def test_post_can_be_retrieved_by_slug(self):
        post = Post.objects.get(title='测试文章')
        res = self.client.get(f'/api/v1/posts/{post.slug}/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['slug'], post.slug)

    def test_search_matches_body_and_tags(self):
        body_match = self.client.get('/api/v1/posts/', {'search': '正文'})
        tag_match = self.client.get('/api/v1/posts/', {'search': 'Vue'})
        self.assertEqual(body_match.data['count'], 1)
        self.assertEqual(tag_match.data['count'], 1)

    def test_sitemap_xml(self):
        res = self.client.get('/api/v1/feed/sitemap.xml')
        self.assertEqual(res.status_code, 200)
        self.assertIn('urlset', res.content.decode())

    def test_rss_feed(self):
        res = self.client.get('/api/v1/feed/rss/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('rss', res.content.decode())
