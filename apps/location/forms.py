from django import forms
from apps.core.models import SafeHaven

class SafeHavenForm(forms.ModelForm):
    class Meta:
        model = SafeHaven
        fields = ['name', 'address', 'safe_phrase', 'special_instructions']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'e.g., Shell Station - Main St.'}),
            'address': forms.TextInput(attrs={'placeholder': '123 Rescue Ave, City'}),
            'safe_phrase': forms.TextInput(attrs={'placeholder': 'e.g., I need a lighthouse'}),
            'special_instructions': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Staff instructions or entry details'}),
        }

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = SafeHaven
        fields = ['is_active']