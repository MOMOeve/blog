from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Profile
from apps.content.models import Category, Comment, Post, Tag

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


class CommentPermissionTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user(username='owner')
        cls.other_author = User.objects.create_user(username='other-author')
        cls.reader = User.objects.create_user(username='comment-reader')
        cls.staff = User.objects.create_user(username='moderator', is_staff=True)
        Profile.objects.filter(user__in=[cls.owner, cls.other_author]).update(role=Profile.ROLE_AUTHOR)
        cls.owner.refresh_from_db()
        cls.other_author.refresh_from_db()
        category = Category.objects.create(name='权限测试')
        cls.post = Post.objects.create(title='公开文章', category=category, author=cls.owner, published=True)
        cls.other_post = Post.objects.create(title='其他文章', category=category, author=cls.other_author, published=True)
        cls.draft = Post.objects.create(title='未发布文章', category=category, author=cls.owner, published=False)
        cls.pending = Comment.objects.create(post=cls.post, author=cls.reader, body='待审评论')
        cls.approved = Comment.objects.create(post=cls.post, author=cls.reader, body='公开评论', approved=True)
        cls.foreign = Comment.objects.create(post=cls.other_post, author=cls.reader, body='别处评论')

    def setUp(self):
        from django.core.cache import cache
        cache.clear()
        self.client = APIClient()
        self.comments_url = f'/api/v1/posts/{self.post.pk}/comments/'
        self.moderate_url = f'{self.comments_url}{self.pending.pk}/'

    def test_reader_submits_pending_comment_and_cannot_self_approve(self):
        self.client.force_authenticate(self.reader)
        response = self.client.post(self.comments_url, {'body': '读者评论', 'approved': True}, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertFalse(response.data['approved'])
        self.assertFalse(Comment.objects.get(pk=response.data['id']).approved)

    def test_anonymous_can_read_only_approved_and_cannot_submit(self):
        response = self.client.get(self.comments_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([item['id'] for item in response.data], [self.approved.pk])
        self.assertEqual(self.client.post(self.comments_url, {'body': '匿名评论'}).status_code, 401)

    def test_readers_and_other_authors_cannot_see_pending_or_moderate(self):
        for user in [self.reader, self.other_author]:
            with self.subTest(user=user.username):
                self.client.force_authenticate(user)
                response = self.client.get(self.comments_url)
                self.assertEqual([item['id'] for item in response.data], [self.approved.pk])
                response = self.client.patch(self.moderate_url, {'approved': True}, format='json')
                self.assertEqual(response.status_code, 403)
                detail = self.client.get(f'/api/v1/posts/{self.post.pk}/')
                self.assertFalse(detail.data['canModerateComments'])
        self.pending.refresh_from_db()
        self.assertFalse(self.pending.approved)

    def test_owner_and_staff_can_see_pending_and_approve_then_withdraw(self):
        for user in [self.owner, self.staff]:
            with self.subTest(user=user.username):
                self.client.force_authenticate(user)
                detail = self.client.get(f'/api/v1/posts/{self.post.slug}/')
                self.assertTrue(detail.data['canModerateComments'])
                response = self.client.get(self.comments_url)
                self.assertIn(self.pending.pk, [item['id'] for item in response.data])
                slug_url = f'/api/v1/posts/{self.post.slug}/comments/{self.pending.pk}/'
                self.assertEqual(self.client.patch(slug_url, {'approved': True}, format='json').status_code, 200)
                self.client.force_authenticate(None)
                self.assertIn(self.pending.pk, [item['id'] for item in self.client.get(self.comments_url).data])
                self.client.force_authenticate(user)
                self.assertEqual(self.client.patch(slug_url, {'approved': False}, format='json').status_code, 200)
                self.client.force_authenticate(None)
                self.assertNotIn(self.pending.pk, [item['id'] for item in self.client.get(self.comments_url).data])

    def test_cross_post_comment_id_is_not_found(self):
        self.client.force_authenticate(self.owner)
        response = self.client.patch(f'{self.comments_url}{self.foreign.pk}/', {'approved': True}, format='json')
        self.assertEqual(response.status_code, 404)
        self.foreign.refresh_from_db()
        self.assertFalse(self.foreign.approved)

    def test_moderation_accepts_only_boolean_approved(self):
        self.client.force_authenticate(self.owner)
        for payload in [[], ['approved'], {}, {'approved': 'true'}, {'approved': 1}, {'approved': None},
                        {'approved': True, 'body': '篡改'}, {'approved': True, 'author': self.owner.pk},
                        {'approved': True, 'post': self.other_post.pk}]:
            with self.subTest(payload=payload):
                self.assertEqual(self.client.patch(self.moderate_url, payload, format='json').status_code, 400)
        self.pending.refresh_from_db()
        self.assertEqual(self.pending.body, '待审评论')
        self.assertEqual(self.pending.author_id, self.reader.pk)
        self.assertFalse(self.pending.approved)

    def test_draft_is_hidden_and_not_open_for_commenting(self):
        url = f'/api/v1/posts/{self.draft.pk}/comments/'
        for user in [None, self.reader, self.other_author]:
            self.client.force_authenticate(user)
            self.assertEqual(self.client.get(url).status_code, 404)
        self.client.force_authenticate(self.owner)
        self.assertEqual(self.client.post(url, {'body': '草稿评论'}, format='json').status_code, 403)

    def test_article_edit_permissions_remain_restricted(self):
        for user in [self.reader, self.other_author]:
            self.client.force_authenticate(user)
            response = self.client.patch(f'/api/v1/posts/{self.post.pk}/', {'title': '越权修改'}, format='json')
            self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_moderate_or_claim_capability(self):
        self.assertEqual(self.client.patch(self.moderate_url, {'approved': True}, format='json').status_code, 401)
        self.assertFalse(self.client.get(f'/api/v1/posts/{self.post.pk}/').data['canModerateComments'])

    def test_blank_or_oversized_comments_are_rejected(self):
        self.client.force_authenticate(self.reader)
        for body in [' ', 'a', '字' * 2001]:
            self.assertEqual(self.client.post(self.comments_url, {'body': body}, format='json').status_code, 400)
