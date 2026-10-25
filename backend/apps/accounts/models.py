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


class SiteAbout(models.Model):
    """站点「关于」页配置（单例，pk=1）。"""

    tagline = models.CharField('头衔/副标题', max_length=128, blank=True)
    quote = models.TextField('引言', blank=True)
    body = models.TextField('正文', blank=True, help_text='多段用空行分隔')
    focus_tags = models.JSONField('关注标签', default=list, blank=True)
    stats = models.JSONField('数据卡片', default=list, blank=True)
    timeline = models.JSONField('时间线', default=list, blank=True)
    timeline_subtitle = models.CharField('时间线副标题', max_length=128, blank=True)
    influences = models.JSONField('影响与资源', default=list, blank=True)
    tech_stack = models.JSONField('技术栈', default=list, blank=True)
    stack_note = models.TextField('技术栈备注', blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '关于页配置'
        verbose_name_plural = '关于页配置'

    def __str__(self) -> str:
        return '关于页配置'

    @classmethod
    def get_solo(cls) -> 'SiteAbout':
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


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
