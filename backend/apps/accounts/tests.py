from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import PasswordResetToken, Profile

User = get_user_model()


class AuthAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='reader', email='reader@test.com', password='readerpass1')
        Profile.objects.filter(user=self.user).update(display_name='读者', role=Profile.ROLE_READER)

    def test_register_creates_reader(self):
        res = self.client.post(
            reverse('auth-register'),
            {'email': 'new@test.com', 'password': 'newpass123', 'displayName': '新用户'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['user']['role'], 'reader')
        self.assertFalse(res.data['user']['isAuthor'])

    def test_profile_patch(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.patch(
            reverse('auth-me'),
            {'displayName': '更新昵称', 'bio': '简介测试'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['displayName'], '更新昵称')
        self.assertEqual(res.data['bio'], '简介测试')

    def test_change_password(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(
            reverse('auth-password-change'),
            {'currentPassword': 'readerpass1', 'newPassword': 'newpass1234'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass1234'))

    def test_password_reset_flow(self):
        mail.outbox.clear()
        res = self.client.post(
            reverse('auth-password-reset'),
            {'email': 'reader@test.com'},
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(mail.outbox), 1)
        token = PasswordResetToken.objects.get(user=self.user)
        confirm = self.client.post(
            reverse('auth-password-reset-confirm'),
            {'token': token.token, 'newPassword': 'resetpass1'},
            format='json',
        )
        self.assertEqual(confirm.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('resetpass1'))


class AuthorRoleTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.author = User.objects.create_user(username='author', email='author@test.com', password='authorpass1')
        Profile.objects.filter(user=self.author).update(role=Profile.ROLE_AUTHOR)
        refresh = RefreshToken.for_user(self.author)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

    def test_author_can_create_post(self):
        res = self.client.post(
            '/api/v1/posts/',
            {
                'title': '作者文章',
                'category': '随笔',
                'excerpt': '摘要',
                'body': '正文',
                'published': False,
            },
            format='json',
        )
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['title'], '作者文章')
