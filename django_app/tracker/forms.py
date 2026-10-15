from django import forms
from .models import DailyLog

class DailyLogForm(forms.ModelForm):
    class Meta:
        model = DailyLog
        fields = ['date', 'mood', 'sleep_hours', 'journal']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'mood': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Vui vẻ, Căng thẳng...'}),
            'sleep_hours': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.5'}),
            'journal': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Hôm nay của bạn thế nào?'}),
        }