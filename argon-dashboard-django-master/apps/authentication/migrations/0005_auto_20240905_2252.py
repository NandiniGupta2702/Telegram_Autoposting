# in your_app/migrations/000X_auto_set_default_user.py
from django.db import migrations, models
from django.contrib.auth.models import User

def set_default_user(apps, schema_editor):
    TelegramBotCredentials = apps.get_model('authentication', 'TelegramBotCredentials')
    User = apps.get_model('auth', 'User')
    default_user = User.objects.first()  # Or specify a user
    for credentials in TelegramBotCredentials.objects.all():
        credentials.user = default_user
        credentials.save()

class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_rename_bot_token_telegrambotcredentials_token'),
    ]

    operations = [
        migrations.RunPython(set_default_user),
    ]
