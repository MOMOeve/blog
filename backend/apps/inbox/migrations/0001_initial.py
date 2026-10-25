# Generated manually for inbox app

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64, verbose_name='姓名')),
                ('email', models.EmailField(max_length=254, verbose_name='邮箱')),
                ('subject', models.CharField(blank=True, max_length=200, verbose_name='主题')),
                ('message', models.TextField(verbose_name='留言')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='提交时间')),
            ],
            options={
                'verbose_name': '联系留言',
                'verbose_name_plural': '联系留言',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='NewsletterSubscription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='邮箱')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='订阅时间')),
            ],
            options={
                'verbose_name': '邮件订阅',
                'verbose_name_plural': '邮件订阅',
                'ordering': ['-created_at'],
            },
        ),
    ]
