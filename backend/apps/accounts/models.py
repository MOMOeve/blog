from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone


class Profile(models.Model):
    ROLE_READER = 'reader'
    ROLE_AUTHOR = 'author'
    ROLE_CHOICES = [
        (ROLE_READER, '读者'),
        (ROLE_AUTHOR, '作者'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    display_name = models.CharField('显示名', max_length=64, blank=True)
    role = models.CharField('角色', max_length=16, choices=ROLE_CHOICES, default=ROLE_READER)
    bio = models.TextField('简介', blank=True)
    avatar = models.CharField('头像', max_length=500, blank=True)

    class Meta:
        verbose_name = '用户资料'
        verbose_name_plural = '用户资料'

    def __str__(self) -> str:
        return self.display_name or self.user.get_username()


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='password_reset_tokens',
    )
    token = models.CharField('令牌', max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)

    class Meta:
        verbose_name = '密码重置令牌'
        verbose_name_plural = '密码重置令牌'
        ordering = ['-created_at']

    def is_valid(self) -> bool:
        return not self.used and self.expires_at > timezone.now()


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            display_name=instance.get_full_name() or instance.username,
        )
    else:
        Profile.objects.get_or_create(
            user=instance,
            defaults={'display_name': instance.username},
        )
