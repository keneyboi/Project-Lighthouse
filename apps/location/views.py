from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.core.models import EstablishmentProfile, SafeHaven
from apps.location.forms import SafeHavenForm




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

    return render(request, 'location/add_location.html', {'form': form})

@login_required(login_url='login')
def toggle_status_view(request, haven_id=None):
    haven = get_object_or_404(SafeHaven, id=haven_id, establishment__user=request.user)
    
    if request.method == 'POST':
        haven.is_active = not haven.is_active
        haven.save()
        return redirect('show_home')
        
    return redirect('show_home')