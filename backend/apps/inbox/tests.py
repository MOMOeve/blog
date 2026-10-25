from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import ContactMessage, NewsletterSubscription


class InboxAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_contact_message_is_saved(self):
        response = self.client.post(
            '/api/v1/contact/',
            {'name': '访客', 'email': 'visitor@example.com', 'subject': '你好', 'message': '这是一条留言'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_contact_message_validates_email(self):
        response = self.client.post(
            '/api/v1/contact/',
            {'name': '访客', 'email': 'invalid', 'message': '内容'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_subscription_is_idempotent(self):
        payload = {'email': 'reader@example.com'}
        first = self.client.post('/api/v1/subscribe/', payload, format='json')
        second = self.client.post('/api/v1/subscribe/', payload, format='json')
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(NewsletterSubscription.objects.count(), 1)
