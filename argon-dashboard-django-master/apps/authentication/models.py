# apps/authentication/models.py
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return self.user.username

# models.py
class ApiCredentials(models.Model):
    api_key = models.CharField(max_length=255, unique=True)
    is_active = models.BooleanField(default=False)  # Add this field

    def __str__(self):
        return self.api_key

    @classmethod
    def get_active_key(cls):
        """Retrieve the active API key from the DB"""
        try:
            return cls.objects.get(is_active=True).api_key
        except cls.DoesNotExist:
            return None

class MinId(models.Model):
    channel_name = models.CharField(max_length=255,default="", unique=True)  # Add this field
    destination_channel = models.CharField(max_length=255,default="")  # Add this field

    min_id = models.BigIntegerField()
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Min ID: {self.min_id}"

from django.db import models

class ChannelMinId(models.Model):
    source_channel = models.CharField(max_length=255)
    destination_channel = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)  # Adjust length as needed
    min_id = models.BigIntegerField(default=0)

    class Meta:
        unique_together = (('source_channel', 'destination_channel', 'phone_number'),)

class AdminCredentials(models.Model):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)  # Store hashed passwords in practice

    def __str__(self):
        return self.username

class TelegramBotCredentials(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='bot_credentials')

    token = models.CharField(max_length=255)
    api_id = models.CharField(max_length=255)
    api_hash = models.CharField(max_length=255)
    group_username = models.CharField(max_length=255)
    channel_username = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=13,default="")
    username = models.CharField(max_length=255,default="")
    def __str__(self):
         return f"{self.user} - {self.token}"


class UserLoginData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bot_token = models.CharField(max_length=255)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.login_time}"
    

    