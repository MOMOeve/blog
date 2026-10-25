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
        # 返回相对路径，避免反向代理或公网部署时把图片地址拼成 localhost。
        return obj.image_url


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
