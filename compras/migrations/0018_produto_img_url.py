# Generated by Django 3.1.3 on 2020-12-12 20:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0017_auto_20201209_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='img_url',
            field=models.URLField(default='', max_length=1000),
            preserve_default=False,
        ),
    ]
