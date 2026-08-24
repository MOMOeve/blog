from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ContactMessage, NewsletterSubscription
from .serializers import ContactMessageSerializer, NewsletterSubscriptionSerializer


class ContactMessageView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = ContactMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class NewsletterSubscribeView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = (request.data.get('email') or '').strip().lower()
        if not email:
            return Response({'detail': '请输入邮箱地址'}, status=status.HTTP_400_BAD_REQUEST)

        subscription, created = NewsletterSubscription.objects.get_or_create(email=email)
        data = NewsletterSubscriptionSerializer(subscription).data
        if created:
            return Response(data, status=status.HTTP_201_CREATED)
        return Response({**data, 'detail': '该邮箱已订阅'}, status=status.HTTP_200_OK)
