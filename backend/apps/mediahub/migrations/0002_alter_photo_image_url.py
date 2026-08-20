# Generated manually for local media paths

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mediahub', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='image_url',
            field=models.CharField(max_length=500, verbose_name='图片地址'),
        ),
    ]
