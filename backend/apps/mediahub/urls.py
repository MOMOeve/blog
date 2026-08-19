from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .upload import MediaUploadView
from .views import PhotoViewSet

router = DefaultRouter()
router.register('photos', PhotoViewSet, basename='photo')

urlpatterns = [
    path('uploads/', MediaUploadView.as_view(), name='media-upload'),
    path('', include(router.urls)),
]
