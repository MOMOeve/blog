from django.contrib.auth import get_user_model
from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import PasswordResetToken, Profile

User = get_user_model()


class AuthAPITests(TestCase):
    def setUp(self):
        from django.core.cache import cache
        cache.clear()
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

    def test_password_reset_url_uses_frontend_configuration_not_request_host(self):
        for base in ['https://blog.example.test', 'https://blog.example.test/']:
            with self.subTest(base=base), override_settings(FRONTEND_BASE_URL=base):
                mail.outbox.clear()
                response = self.client.post(reverse('auth-password-reset'), {'email': self.user.email}, format='json', HTTP_HOST='localhost:8000')
                self.assertEqual(response.status_code, 200)
                self.assertEqual(len(mail.outbox), 1)
                token = PasswordResetToken.objects.filter(user=self.user).latest('pk')
                self.assertIn(f'https://blog.example.test/reset-password?token={token.token}', mail.outbox[0].body)
                self.assertNotIn('localhost:8000', mail.outbox[0].body)

    def test_reset_response_does_not_disclose_unknown_email(self):
        mail.outbox.clear()
        unknown = self.client.post(reverse('auth-password-reset'), {'email': 'absent@test.com'}, format='json')
        self.assertEqual(len(mail.outbox), 0)
        known = self.client.post(reverse('auth-password-reset'), {'email': self.user.email}, format='json')
        self.assertEqual(unknown.status_code, known.status_code)
        self.assertEqual(unknown.data, known.data)

    def test_invalid_expired_and_used_reset_tokens_are_rejected(self):
        expired = PasswordResetToken.objects.create(user=self.user, token='expired', expires_at=timezone.now() - timedelta(seconds=1))
        used = PasswordResetToken.objects.create(user=self.user, token='used', expires_at=timezone.now() + timedelta(hours=1), used=True)
        for value in ['nonexistent', expired.token, used.token]:
            response = self.client.post(reverse('auth-password-reset-confirm'), {'token': value, 'newPassword': 'resetpass1'}, format='json')
            self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('readerpass1'))

    def test_reset_token_cannot_be_reused_and_invalidates_other_tokens(self):
        tokens = [PasswordResetToken.objects.create(user=self.user, token=f'valid-{i}', expires_at=timezone.now() + timedelta(hours=1)) for i in range(2)]
        url = reverse('auth-password-reset-confirm')
        payload = {'token': tokens[0].token, 'newPassword': 'resetpass1'}
        self.assertEqual(self.client.post(url, payload, format='json').status_code, 200)
        self.assertEqual(self.client.post(url, payload, format='json').status_code, 400)
        self.assertEqual(self.client.post(url, {'token': tokens[1].token, 'newPassword': 'otherpass1'}, format='json').status_code, 400)


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
