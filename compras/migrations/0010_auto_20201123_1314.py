# Generated by Django 3.1.3 on 2020-11-23 16:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0009_auto_20201123_1311'),
    ]

    operations = [
        migrations.AlterField(
            model_name='endereco',
            name='cep',
            field=models.CharField(max_length=8),
        ),
    ]
