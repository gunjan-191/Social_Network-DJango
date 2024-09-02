from django import forms
from .models import NotificationSetting

class NotificationSettingForm(forms.ModelForm):
    class Meta:
        model = NotificationSetting
        fields = ['condition', 'is_active']
