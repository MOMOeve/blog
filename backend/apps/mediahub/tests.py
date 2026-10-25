from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from apps.accounts.models import Profile

from .models import Photo

User = get_user_model()


class MediaHubAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.staff = User.objects.create_user(
            username='staff', email='staff@example.com', password='staffpass1', is_staff=True
        )
        Profile.objects.filter(user=self.staff).update(role=Profile.ROLE_AUTHOR)

    def test_public_list_hides_unpublished_photos(self):
        Photo.objects.create(title='公开', category='自然', image_url='/media/public.jpg', published=True)
        Photo.objects.create(title='草稿', category='自然', image_url='/media/draft.jpg', published=False)
        response = self.client.get('/api/v1/photos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], '公开')

    def test_only_staff_can_create_photo(self):
        payload = {'title': '新照片', 'category': '自然', 'img': '/media/new.jpg'}
        anonymous = self.client.post('/api/v1/photos/', payload, format='json')
        self.assertEqual(anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
        self.client.force_authenticate(self.staff)
        staff_response = self.client.post('/api/v1/photos/', payload, format='json')
        self.assertEqual(staff_response.status_code, status.HTTP_201_CREATED)

    def test_upload_rejects_non_image_content(self):
        self.client.force_authenticate(self.staff)
        upload = SimpleUploadedFile('bad.png', b'not an image', content_type='image/png')
        response = self.client.post('/api/v1/uploads/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_accepts_valid_png(self):
        self.client.force_authenticate(self.staff)
        stream = BytesIO()
        Image.new('RGB', (2, 2), 'white').save(stream, format='PNG')
        upload = SimpleUploadedFile('ok.png', stream.getvalue(), content_type='image/png')
        response = self.client.post('/api/v1/uploads/', {'file': upload}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
