from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import EstablishmentProfile, SafeHaven, ProtocolChecklist

@login_required
def settings_view(request):
    # Retrieve or create the profile linked to the logged-in user
    profile, _ = EstablishmentProfile.objects.get_or_create(user=request.user)
    
    locations = profile.safe_havens.all()
    protocols = profile.protocols.all()

    if request.method == 'POST':
        action_type = request.POST.get('action_type')

        # Delete SafeHaven Location
        if action_type == 'delete_location':
            location_id = request.POST.get('location_id')
            location = get_object_or_404(SafeHaven, id=location_id, establishment=profile)
            location_name = location.name
            location.delete()
            messages.success(request, f'Location "{location_name}" deleted successfully.')
            return redirect('settings')

        # Add Protocol Step
        elif action_type == 'add_protocol':
            title = request.POST.get('title')
            description = request.POST.get('description')
            if title and description:
                ProtocolChecklist.objects.create(
                    establishment=profile,
                    title=title,
                    description=description
                )
                messages.success(request, 'Emergency protocol step added.')
            return redirect('settings')

        # Delete Protocol Step
        elif action_type == 'delete_protocol':
            protocol_id = request.POST.get('protocol_id')
            protocol = get_object_or_404(ProtocolChecklist, id=protocol_id, establishment=profile)
            protocol.delete()
            messages.success(request, 'Protocol step removed.')
            return redirect('settings')

    return render(request, 'establishment_profile/settings.html', {
        'locations': locations,
        'protocols': protocols,
    })