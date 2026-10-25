from django.db import migrations, models


def backfill_identity_keys(apps, schema_editor):
    PostLike = apps.get_model('content', 'PostLike')
    for like in PostLike.objects.all().iterator():
        identity = f'user:{like.user_id}' if like.user_id else f'visitor:{like.visitor_id}'
        like.identity_key = identity[:96]
        like.save(update_fields=['identity_key'])


class Migration(migrations.Migration):
    dependencies = [
        ('content', '0004_postlike_unique_constraints'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveConstraint(
                    model_name='postlike',
                    name='unique_user_post_like',
                ),
                migrations.RemoveConstraint(
                    model_name='postlike',
                    name='unique_visitor_post_like',
                ),
            ],
        ),
        migrations.AddField(
            model_name='postlike',
            name='identity_key',
            field=models.CharField(db_index=True, default='', max_length=96, verbose_name='点赞身份键'),
        ),
        migrations.RunPython(backfill_identity_keys, migrations.RunPython.noop),
        migrations.AddConstraint(
            model_name='postlike',
            constraint=models.UniqueConstraint(
                fields=('post', 'identity_key'),
                name='unique_post_like_identity',
            ),
        ),
    ]
