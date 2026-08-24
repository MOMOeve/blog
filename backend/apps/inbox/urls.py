from django.urls import path

from .views import ContactMessageView, NewsletterSubscribeView

urlpatterns = [
    path('contact/', ContactMessageView.as_view(), name='contact-message'),
    path('subscribe/', NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
]
