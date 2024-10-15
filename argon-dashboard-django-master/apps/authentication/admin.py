# apps/authentication/admin.py

from django.contrib import admin
from .models import ChannelMinId, TelegramBotCredentials,ApiCredentials

@admin.register(TelegramBotCredentials)
class TelegramBotConfigurationAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'api_id', 'api_hash', 'group_username', 'channel_username','phone_number']


@admin.register(ChannelMinId)
class MinIdAdmin(admin.ModelAdmin):
    list_display = ['min_id','source_channel','destination_channel', 'phone_number']


@admin.register(ApiCredentials)
class ApiCredentialsAdmin(admin.ModelAdmin):
    list_display = ['api_key', 'is_active']
    list_editable = ['is_active']  # Allows editing 'is_active' from the list view

