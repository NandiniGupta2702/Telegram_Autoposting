# Generated by Django 4.2.16 on 2024-09-23 11:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0024_delete_telegrambotstate'),
    ]

    operations = [
        migrations.CreateModel(
            name='MinId',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('min_id', models.BigIntegerField()),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]