from apps.core.models import SafeHaven
from django import forms


class SafeHavenForm(forms.ModelForm):

  class Meta:
    model = SafeHaven
    fields = [
        'name',
        'barangay',
        'city',
        'province',
        'safe_phrase',
        'special_instructions',
    ]
    widgets = {
        'name': forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Shell Station - Main St.',
            }
        ),
        'barangay': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g., San Jose'}
        ),
        'city': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g., Cebu City'}
        ),
        'province': forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': 'e.g., Cebu'}
        ),
        'safe_phrase': forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'e.g., I need a lighthouse',
            }
        ),
        'special_instructions': forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': (
                    'Staff instructions, entry details, or emergency protocols'
                ),
            }
        ),
    }


class StatusUpdateForm(forms.ModelForm):

  class Meta:
    model = SafeHaven
    fields = ['is_active']
    widgets = {
        'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }