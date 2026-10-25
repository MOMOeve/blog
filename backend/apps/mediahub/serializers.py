from rest_framework import serializers

from .models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    date = serializers.CharField(source='taken_on')
    img = serializers.SerializerMethodField()

    class Meta:
        model = Photo
        fields = [
            'id',
            'title',
            'location',
            'date',
            'img',
            'aspect',
            'category',
            'description',
            'sort_order',
            'published',
        ]

    def get_img(self, obj: Photo) -> str:
        url = obj.image_url
        request = self.context.get('request')
        if request and url.startswith('/'):
            return request.build_absolute_uri(url)
        return url


class PhotoWriteSerializer(serializers.ModelSerializer):
    date = serializers.CharField(source='taken_on', required=False, allow_blank=True)
    img = serializers.CharField(source='image_url')

    class Meta:
        model = Photo
        fields = [
            'title',
            'location',
            'date',
            'img',
            'aspect',
            'category',
            'description',
            'sort_order',
            'published',
        ]
