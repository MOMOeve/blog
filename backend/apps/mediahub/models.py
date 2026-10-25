from django.db import models


class Photo(models.Model):
    ASPECT_CHOICES = [
        ('landscape', '横图'),
        ('portrait', '竖图'),
    ]

    title = models.CharField('标题', max_length=120)
    location = models.CharField('地点', max_length=120, blank=True)
    taken_on = models.CharField('拍摄时间文案', max_length=64, blank=True)
    image_url = models.CharField('图片地址', max_length=500)
    aspect = models.CharField('比例', max_length=16, choices=ASPECT_CHOICES, default='landscape')
    category = models.CharField('分类', max_length=32, db_index=True)
    description = models.TextField('描述', blank=True)
    published = models.BooleanField('已发布', default=True)
    sort_order = models.PositiveIntegerField('排序', default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '照片'
        verbose_name_plural = '照片'
        ordering = ['sort_order', '-created_at']

    def __str__(self) -> str:
        return self.title
