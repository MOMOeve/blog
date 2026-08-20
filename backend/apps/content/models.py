from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField('名称', max_length=32, unique=True)
    slug = models.SlugField('标识', max_length=64, unique=True, blank=True)

    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True) or self.name
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.name


class Tag(models.Model):
    name = models.CharField('名称', max_length=32, unique=True)

    class Meta:
        verbose_name = '标签'
        verbose_name_plural = '标签'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name


class Post(models.Model):
    title = models.CharField('标题', max_length=200)
    title_en = models.CharField('英文标题', max_length=200, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='posts',
        verbose_name='分类',
    )
    tags = models.ManyToManyField(Tag, blank=True, related_name='posts', verbose_name='标签')
    excerpt = models.TextField('摘要')
    body = models.TextField('正文', blank=True)
    cover_image = models.CharField('封面图', max_length=500, blank=True)
    read_time = models.CharField('阅读时长', max_length=32, default='5 分钟')
    featured = models.BooleanField('精选', default=False)
    published = models.BooleanField('已发布', default=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='作者',
    )
    published_at = models.DateTimeField('发布时间', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '文章'
        verbose_name_plural = '文章'
        ordering = ['-published_at', '-created_at']

    def __str__(self) -> str:
        return self.title
