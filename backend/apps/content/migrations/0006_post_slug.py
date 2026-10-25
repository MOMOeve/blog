from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    Post = apps.get_model('content', 'Post')
    used = set()
    for post in Post.objects.order_by('id'):
        base = slugify(post.title, allow_unicode=True) or f'post-{post.pk}'
        candidate = base
        suffix = 2
        while candidate in used:
            candidate = f'{base}-{suffix}'
            suffix += 1
        post.slug = candidate[:220]
        post.save(update_fields=['slug'])
        used.add(post.slug)


class Migration(migrations.Migration):
    dependencies = [('content', '0005_postlike_identity_key')]

    operations = [
        migrations.AddField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, null=True, verbose_name='链接标识'),
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='post',
            name='slug',
            field=models.SlugField(blank=True, max_length=220, unique=True, verbose_name='链接标识'),
        ),
    ]
