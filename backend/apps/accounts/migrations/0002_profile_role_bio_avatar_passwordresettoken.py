# Generated manually

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='avatar',
            field=models.CharField(blank=True, max_length=500, verbose_name='头像'),
        ),
        migrations.AddField(
            model_name='profile',
            name='bio',
            field=models.TextField(blank=True, verbose_name='简介'),
        ),
        migrations.AddField(
            model_name='profile',
            name='role',
            field=models.CharField(
                choices=[('reader', '读者'), ('author', '作者')],
                default='reader',
                max_length=16,
                verbose_name='角色',
            ),
        ),
        migrations.CreateModel(
            name='PasswordResetToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(db_index=True, max_length=64, unique=True, verbose_name='令牌')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('used', models.BooleanField(default=False)),
                (
                    'user',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='password_reset_tokens',
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                'verbose_name': '密码重置令牌',
                'verbose_name_plural': '密码重置令牌',
                'ordering': ['-created_at'],
            },
        ),
    ]
