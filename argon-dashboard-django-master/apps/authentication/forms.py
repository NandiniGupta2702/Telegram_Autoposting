# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TelegramBotCredentials
from .models import ApiCredentials

USER_TYPE_CHOICES = [
    ('user', 'User'),
    ('admin', 'Admin'),
]

class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        widget=forms.RadioSelect,
        label="Login as"
    )


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={
                "placeholder": "Username",
                "class": "form-control"
            }
        ))
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Email",
                "class": "form-control"
            }
        ))
    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "class": "form-control"
            }
        ))
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password check",
                "class": "form-control"
            }
        ))

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')



class TelegramBotForm(forms.ModelForm):
    
    class Meta:
        model = TelegramBotCredentials
        fields = ['token', 'api_id', 'api_hash', 'group_username', 'channel_username','phone_number']
        widgets = {
            'token': forms.TextInput(attrs={'class': 'form-control'}),
            'api_id': forms.TextInput(attrs={'class': 'form-control'}),
            'api_hash': forms.TextInput(attrs={'class': 'form-control'}),
            'group_username': forms.TextInput(attrs={'class': 'form-control'}),
            'channel_username': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),

        }

    def save(self, commit=True,user=None):
        bot = super().save(commit=False)
        if user:
            bot.user = user
        if commit:
            bot.save()
        return bot



class ApiInputForm(forms.ModelForm):
    previous_apis = forms.ModelChoiceField(
        queryset=ApiCredentials.objects.all(), required=False, label="Select Previous API"
    )

    class Meta:
        model = ApiCredentials
        fields = ['api_key']  # Only need to input API key

    def save(self, commit=True):
        # Ensure that duplicate API keys are not saved
        api_key = self.cleaned_data.get('api_key')
        instance, created = ApiCredentials.objects.get_or_create(api_key=api_key)
        if commit:
            instance.save()
        return instance

