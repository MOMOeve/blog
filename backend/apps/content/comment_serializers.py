from rest_framework import serializers

from .models import Comment


class CommentSerializer(serializers.ModelSerializer):
    authorName = serializers.SerializerMethodField()
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'body', 'authorName', 'createdAt', 'approved']
        read_only_fields = ['id', 'authorName', 'createdAt', 'approved']

    def get_authorName(self, obj: Comment) -> str:
        profile = getattr(obj.author, 'profile', None)
        if profile and profile.display_name:
            return profile.display_name
        return obj.author.get_full_name() or obj.author.username


class CommentWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['body']

    def validate_body(self, value: str) -> str:
        text = (value or '').strip()
        if len(text) < 2:
            raise serializers.ValidationError('评论至少 2 个字')
        if len(text) > 2000:
            raise serializers.ValidationError('评论不能超过 2000 字')
        return text


class CommentModerationSerializer(serializers.Serializer):
    approved = serializers.BooleanField(required=True)

    def to_internal_value(self, data):
        if not isinstance(data, dict) or set(data) != {'approved'} or type(data.get('approved')) is not bool:
            raise serializers.ValidationError({'approved': '仅允许提交 approved 布尔字段'})
        return super().to_internal_value(data)
