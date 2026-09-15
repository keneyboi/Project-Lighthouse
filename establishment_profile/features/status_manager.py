from django import forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from ..models import SafeHaven

class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = SafeHaven
        fields = ['is_active']

@login_required(login_url='login')
def toggle_status_view(request, haven_id=None):
    haven = get_object_or_404(SafeHaven, id=haven_id, establishment__user=request.user)
    
    if request.method == 'POST':
        haven.is_active = not haven.is_active
        haven.save()
        return redirect('show_home')
        
    return redirect('show_home')