# Generated by Django 5.0.6 on 2024-09-12 09:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0018_remove_telegrambotcredentials_csv_file_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='telegrambotcredentials',
            old_name='is_active',
            new_name='use_csv',
        ),
        migrations.AddField(
            model_name='telegrambotcredentials',
            name='csv_file',
            field=models.FileField(blank=True, null=True, upload_to='csv_files/'),
        ),
    ]
