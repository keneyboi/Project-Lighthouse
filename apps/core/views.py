from django.shortcuts import render
from .models import SafeHaven


def show_landing(request):
    """
    Renders the public landing page with all active safe havens
    registered across all accounts pre-loaded for immediate map and card display.
    """
    havens = SafeHaven.objects.filter(is_active=True).select_related('establishment').order_by('id')

    havens_data = [
        {
            'id': h.id,
            'name': h.name,
            'address': h.address,
            'barangay': h.barangay,
            'city': h.city,
            'province': h.province,
            'latitude': float(h.latitude),
            'longitude': float(h.longitude),
            'safe_phrase': h.safe_phrase,
            'special_instructions': h.special_instructions or 'Standard quiet check-in protocol active.',
            'operating_hours': h.operating_hours_display,
            'contact_phone': h.contact_phone,
            'organization_name': h.organization_name,
            'verification_status': h.establishment.verification_status if h.establishment else 'VERIFIED',
            'people_helped': h.people_helped,
            'is_active': h.is_active,
        }
        for h in havens
    ]

    return render(request, 'core/landing.html', {
        'havens': havens,
        'havens_data': havens_data,
    })