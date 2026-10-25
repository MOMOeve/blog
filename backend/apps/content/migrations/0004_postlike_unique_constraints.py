from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0003_post_stats_comments'),
    ]

    operations = [
        migrations.RunPython(
            code=lambda apps, schema_editor: _deduplicate_likes(apps),
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AddConstraint(
            model_name='postlike',
            constraint=models.UniqueConstraint(
                fields=('post', 'user'),
                condition=Q(user__isnull=False),
                name='unique_user_post_like',
            ),
        ),
        migrations.AddConstraint(
            model_name='postlike',
            constraint=models.UniqueConstraint(
                fields=('post', 'visitor_id'),
                condition=Q(user__isnull=True),
                name='unique_visitor_post_like',
            ),
        ),
    ]


def _deduplicate_likes(apps):
    PostLike = apps.get_model('content', 'PostLike')
    seen_users = set()
    seen_visitors = set()
    for like in PostLike.objects.order_by('id').iterator():
        if like.user_id is not None:
            key = (like.post_id, like.user_id)
            if key in seen_users:
                like.delete()
            else:
                seen_users.add(key)
        else:
            key = (like.post_id, like.visitor_id)
            if key in seen_visitors:
                like.delete()
            else:
                seen_visitors.add(key)
