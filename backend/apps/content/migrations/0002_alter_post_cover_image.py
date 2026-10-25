# Generated manually for local media paths

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('content', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='cover_image',
            field=models.CharField(blank=True, max_length=500, verbose_name='封面图'),
        ),
    ]
