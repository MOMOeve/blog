from django.db import models


class ContactMessage(models.Model):
    name = models.CharField('姓名', max_length=64)
    email = models.EmailField('邮箱')
    subject = models.CharField('主题', max_length=200, blank=True)
    message = models.TextField('留言')
    created_at = models.DateTimeField('提交时间', auto_now_add=True)

    class Meta:
        verbose_name = '联系留言'
        verbose_name_plural = '联系留言'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f'{self.name} · {self.subject or self.email}'


class NewsletterSubscription(models.Model):
    email = models.EmailField('邮箱', unique=True)
    created_at = models.DateTimeField('订阅时间', auto_now_add=True)

    class Meta:
        verbose_name = '邮件订阅'
        verbose_name_plural = '邮件订阅'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.email
