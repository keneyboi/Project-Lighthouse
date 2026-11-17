import json
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST
from apps.core.models import EstablishmentProfile, SafeHaven
from apps.location.forms import SafeHavenForm


def _haven_to_dict(haven):
    return {
        'id': haven.id,
        'name': haven.name,
        'address': haven.address,
        'barangay': haven.barangay,
        'city': haven.city,
        'province': haven.province,
        'latitude': float(haven.latitude),
        'longitude': float(haven.longitude),
        'safe_phrase': haven.safe_phrase,
        'special_instructions': haven.special_instructions or '',
        'operating_hours': haven.operating_hours_display,
        'is_active': haven.is_active,
        'people_helped': haven.people_helped,
    }


@login_required(login_url='login')
def manage_locations_view(request):
    """
    Primary Safe Havens management dashboard view:
    - Interactive account-level sanctuary map
    - Search & filter toolbar
    - Scrollable safe havens list with live status toggling, edit, and delete
    """
    profile, _ = EstablishmentProfile.objects.get_or_create(user=request.user)
    user_havens = profile.safe_havens.all().order_by('-id')

    havens_data = [_haven_to_dict(h) for h in user_havens]

    form = SafeHavenForm()

    return render(request, 'location/manage_locations.html', {
        'profile': profile,
        'havens': user_havens,
        'havens_data': havens_data,
        'form': form,
        'total_havens': user_havens.count(),
        'active_havens_count': user_havens.filter(is_active=True).count(),
    })


@login_required(login_url='login')
@require_POST
def create_location_view(request):
    """
    Creates a new SafeHaven tied to the user's establishment profile.
    Supports both AJAX JSON requests and standard form submissions.
    """
    profile, _ = EstablishmentProfile.objects.get_or_create(user=request.user)
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or request.content_type == 'application/json'
    )

    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)
    else:
        data = request.POST

    name = data.get('name', '').strip()
    if not name:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Safe Haven name is required.'}, status=400)
        messages.error(request, 'Safe Haven name is required.')
        return redirect('manage_locations')

    safe_haven = SafeHaven(
        establishment=profile,
        name=name,
        barangay=data.get('barangay', '').strip(),
        city=data.get('city', '').strip(),
        province=data.get('province', '').strip(),
        safe_phrase=data.get('safe_phrase', '').strip(),
        special_instructions=data.get('special_instructions', '').strip(),
        is_active=data.get('is_active', True) in (True, 'True', 'true', 'on', '1', 1),
    )

    lat = data.get('latitude')
    lon = data.get('longitude')
    if lat and lon:
        try:
            safe_haven.latitude = Decimal(str(lat))
            safe_haven.longitude = Decimal(str(lon))
        except (ValueError, InvalidOperation):
            safe_haven.latitude = Decimal('0.0')
            safe_haven.longitude = Decimal('0.0')

    safe_haven.save()

    if is_ajax:
        return JsonResponse({
            'success': True,
            'haven': _haven_to_dict(safe_haven),
            'message': f'Safe Haven "{safe_haven.name}" successfully created.'
        })

    messages.success(request, f'Safe Haven "{safe_haven.name}" successfully registered.')
    return redirect('manage_locations')


@login_required(login_url='login')
@require_http_methods(['GET', 'POST'])
def edit_location_view(request, haven_id):
    """
    GET: Returns SafeHaven JSON details for pre-filling edit forms.
    POST: Updates the SafeHaven instance.
    """
    haven = get_object_or_404(SafeHaven, id=haven_id, establishment__user=request.user)
    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or request.content_type == 'application/json'
    )

    if request.method == 'GET':
        return JsonResponse({'success': True, 'haven': _haven_to_dict(haven)})

    # Handle POST
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8'))
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data.'}, status=400)
    else:
        data = request.POST

    name = data.get('name', '').strip()
    if not name:
        if is_ajax:
            return JsonResponse({'success': False, 'error': 'Safe Haven name is required.'}, status=400)
        messages.error(request, 'Safe Haven name is required.')
        return redirect('manage_locations')

    haven.name = name
    if 'barangay' in data:
        haven.barangay = (data.get('barangay') or '').strip()
    if 'city' in data:
        haven.city = (data.get('city') or '').strip()
    if 'province' in data:
        haven.province = (data.get('province') or '').strip()
    if 'safe_phrase' in data:
        haven.safe_phrase = (data.get('safe_phrase') or '').strip()
    if 'special_instructions' in data:
        haven.special_instructions = (data.get('special_instructions') or '').strip()

    if 'is_active' in data:
        haven.is_active = data.get('is_active') in (True, 'True', 'true', 'on', '1', 1)

    lat = data.get('latitude')
    lon = data.get('longitude')
    if lat is not None and lon is not None:
        try:
            haven.latitude = Decimal(str(lat))
            haven.longitude = Decimal(str(lon))
        except (ValueError, InvalidOperation):
            pass

    haven.save()

    if is_ajax:
        return JsonResponse({
            'success': True,
            'haven': _haven_to_dict(haven),
            'message': f'Safe Haven "{haven.name}" successfully updated.'
        })

    messages.success(request, f'Safe Haven "{haven.name}" updated.')
    return redirect('manage_locations')


@login_required(login_url='login')
@require_POST
def toggle_status_view(request, haven_id=None):
    """
    Toggles the is_active status of a SafeHaven.
    """
    haven = get_object_or_404(SafeHaven, id=haven_id, establishment__user=request.user)

    haven.is_active = not haven.is_active
    haven.save()

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or request.content_type == 'application/json'
    )

    status_label = 'Active' if haven.is_active else 'Inactive'

    if is_ajax:
        return JsonResponse({
            'success': True,
            'id': haven.id,
            'is_active': haven.is_active,
            'status_label': status_label,
            'message': f'Safe Haven "{haven.name}" is now {status_label}.'
        })

    messages.info(request, f'Safe Haven is now {status_label.lower()}.')
    return redirect('manage_locations')


@login_required(login_url='login')
@require_POST
def delete_location_view(request, haven_id=None):
    """
    Removes a SafeHaven record after confirmation.
    """
    haven = get_object_or_404(SafeHaven, id=haven_id, establishment__user=request.user)
    haven_name = haven.name
    haven.delete()

    is_ajax = (
        request.headers.get('x-requested-with') == 'XMLHttpRequest'
        or request.content_type == 'application/json'
    )

    if is_ajax:
        return JsonResponse({
            'success': True,
            'id': haven_id,
            'message': f'Safe Haven "{haven_name}" was permanently removed.'
        })

    messages.success(request, f'Safe Haven "{haven_name}" deleted.')
    return redirect('manage_locations')


@login_required(login_url='login')
def add_location_view(request):
    """
    Legacy standalone creation page redirecting to the management dashboard.
    """
    if request.method == 'POST':
        return create_location_view(request)
    form = SafeHavenForm()
    return render(request, 'location/add_location.html', {'form': form})
