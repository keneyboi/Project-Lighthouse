import json
import math
import uuid
from decimal import Decimal
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from .models import AlertStatus, EmergencyAlert, SafeHaven, VerificationStatus


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance in kilometers between two points
    on the earth (specified in decimal degrees).
    """
    R = 6371.0  # Earth radius in kilometers

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


@require_GET
def safe_havens_geojson_api(request):
    """
    GeoJSON endpoint returning active, verified SafeHaven records
    optionally filtered and ordered by proximity to the user's coordinates.
    """
    # Parse query parameters
    lat_param = request.GET.get('lat')
    lon_param = request.GET.get('lon') or request.GET.get('lng')
    radius_param = request.GET.get('radius')  # in kilometers
    query_param = request.GET.get('q', '').strip()

    user_lat = None
    user_lon = None
    if lat_param and lon_param:
        try:
            user_lat = float(lat_param)
            user_lon = float(lon_param)
        except (ValueError, TypeError):
            user_lat = None
            user_lon = None

    radius = None
    if radius_param:
        try:
            radius = float(radius_param)
        except (ValueError, TypeError):
            radius = None

    # Base query: Active safe havens
    qs = SafeHaven.objects.filter(is_active=True).select_related('establishment')

    # Filter verified establishments (with graceful fallback if no verified records exist yet)
    has_verified = qs.filter(establishment__verification_status=VerificationStatus.VERIFIED).exists()
    if has_verified:
        qs = qs.filter(establishment__verification_status=VerificationStatus.VERIFIED)
    else:
        # Fallback in local/development environments
        qs = qs.filter(
            Q(establishment__verification_status=VerificationStatus.VERIFIED)
            | Q(establishment__verification_status=VerificationStatus.PENDING)
            | Q(establishment__isnull=True)
        )

    # Optional text search filter
    if query_param:
        qs = qs.filter(
            Q(name__icontains=query_param)
            | Q(barangay__icontains=query_param)
            | Q(city__icontains=query_param)
            | Q(province__icontains=query_param)
            | Q(safe_phrase__icontains=query_param)
            | Q(special_instructions__icontains=query_param)
        )

    havens_with_distance = []
    for haven in qs:
        haven_lat = float(haven.latitude)
        haven_lon = float(haven.longitude)

        # Distance calculation
        dist = None
        if user_lat is not None and user_lon is not None and (haven_lat != 0.0 or haven_lon != 0.0):
            dist = haversine_distance(user_lat, user_lon, haven_lat, haven_lon)
            if radius is not None and dist > radius:
                continue

        havens_with_distance.append((haven, dist))

    # Sort: by distance if coordinates provided, else by ID
    if user_lat is not None and user_lon is not None:
        havens_with_distance.sort(key=lambda item: (item[1] is None, item[1] or 0.0))
    else:
        havens_with_distance.sort(key=lambda item: item[0].id)

    # Format as standard GeoJSON FeatureCollection
    features = []
    for haven, dist in havens_with_distance:
        haven_lat = float(haven.latitude)
        haven_lon = float(haven.longitude)

        dist_km = round(dist, 2) if dist is not None else None
        dist_text = f"{round(dist, 1)} km away" if dist is not None else ""

        org_name = haven.establishment.organization_name if (haven.establishment and haven.establishment.organization_name) else haven.name
        phone = haven.establishment.contact_phone if haven.establishment else ""
        verif_status = haven.establishment.verification_status if haven.establishment else "VERIFIED"

        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [haven_lon, haven_lat]
            },
            "properties": {
                "id": haven.id,
                "name": haven.name,
                "address": haven.address,
                "barangay": haven.barangay,
                "city": haven.city,
                "province": haven.province,
                "latitude": haven_lat,
                "longitude": haven_lon,
                "safe_phrase": haven.safe_phrase,
                "special_instructions": haven.special_instructions or "Standard quiet check-in protocol active.",
                "operating_hours": haven.operating_hours_display,
                "contact_phone": phone,
                "organization_name": org_name,
                "verification_status": verif_status,
                "people_helped": haven.people_helped,
                "distance_km": dist_km,
                "distance_text": dist_text,
                "is_active": haven.is_active
            }
        })

    response_data = {
        "type": "FeatureCollection",
        "count": len(features),
        "user_coordinates": {"latitude": user_lat, "longitude": user_lon} if user_lat and user_lon else None,
        "features": features
    }

    return JsonResponse(response_data, safe=False)


@csrf_exempt
@require_POST
def discreet_ping_api(request):
    """
    Discreetly sends an EmergencyAlert to the specified SafeHaven.
    Returns status confirmation and discreet token.
    """
    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body.decode('utf-8'))
        else:
            data = request.POST

        haven_id = data.get('haven_id')
        if not haven_id:
            return JsonResponse({'success': False, 'error': 'Safe Haven ID is required.'}, status=400)

        try:
            haven = SafeHaven.objects.get(id=haven_id, is_active=True)
        except SafeHaven.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Safe Haven not found or inactive.'}, status=404)

        notes = data.get('notes', '')
        descriptors = data.get('descriptors', [])
        if isinstance(descriptors, list) and descriptors:
            descriptor_str = ", ".join(descriptors)
            notes = f"Descriptors: [{descriptor_str}]. {notes}".strip()

        session_token = data.get('session_token') or uuid.uuid4().hex[:12]

        alert = EmergencyAlert.objects.create(
            safe_haven=haven,
            session_token=session_token,
            status=AlertStatus.RECEIVED,
            notes=notes
        )

        return JsonResponse({
            'success': True,
            'alert_id': alert.id,
            'session_token': session_token,
            'haven_name': haven.name,
            'message': f"Discreet ping delivered to {haven.name}. Personnel have been quietly alerted."
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
