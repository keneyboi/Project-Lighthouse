from apps.core.models import EstablishmentProfile, SafeHaven
from apps.location.forms import SafeHavenForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST


@login_required(login_url='login')
def add_location_view(request):
    profile, _ = EstablishmentProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = SafeHavenForm(request.POST)
        if form.is_valid():
            safe_haven = form.save(commit=False)
            safe_haven.establishment = profile

        if request.POST.get('latitude') and request.POST.get('longitude'):
            safe_haven.latitude = request.POST.get('latitude')
            safe_haven.longitude = request.POST.get('longitude')

        safe_haven.save()
        messages.success(request, 'Safe Haven location successfully created.')
        return redirect('show_home')
    else:
        form = SafeHavenForm()

    return render(request, 'location/add_location.html', {'form': form})


@login_required(login_url='login')
@require_POST
def toggle_status_view(request, haven_id=None):
    haven = get_object_or_404(
        SafeHaven, id=haven_id, establishment_user=request.user
    )

    haven.is_active = not haven.is_active
    haven.save()

    status_label = 'active' if haven.is_active else 'inactive'
    messages.info(request, f'Safe Haven is now {status_label}.')

    return redirect('show_home')