from django.conf import settings
from django import forms
from captcha.fields import CaptchaField

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    if settings.IN_PRODUCTION:
        captcha = CaptchaField()