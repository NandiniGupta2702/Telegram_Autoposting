# Generated by Django 4.2.16 on 2024-09-23 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0025_minid'),
    ]

    operations = [
        migrations.AddField(
            model_name='minid',
            name='channel_name',
            field=models.CharField(default='', max_length=255, unique=True),
        ),
    ]