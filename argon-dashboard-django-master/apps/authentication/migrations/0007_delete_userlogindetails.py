# Generated by Django 5.0.6 on 2024-09-06 05:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0006_telegrambotcredentials_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserLoginDetails',
        ),
    ]