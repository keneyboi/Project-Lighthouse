from django import forms
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from ..models import EstablishmentProfile, SafeHaven

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

@login_required(login_url='login')
def add_location_view(request):
    profile, _ = EstablishmentProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = SafeHavenForm(request.POST)
        if form.is_valid():
            safe_haven = form.save(commit=False)
            safe_haven.establishment = profile
            safe_haven.save()
            return redirect('show_home')
    else:
        form = SafeHavenForm()

    return render(request, 'establishment_profile/add_location.html', {'form': form})