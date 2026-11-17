from django.db import models
from django.contrib.auth.models import User

class VerificationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    VERIFIED = 'VERIFIED', 'Verified'
    REJECTED = 'REJECTED', 'Rejected'
    SUSPENDED = 'SUSPENDED', 'Suspended'


class AlertStatus(models.TextChoices):
    RECEIVED = 'RECEIVED', 'Received'
    STAFF_NOTIFIED = 'STAFF_NOTIFIED', 'Staff Notified'
    RESOLVED = 'RESOLVED', 'Resolved'
    CANCELLED = 'CANCELLED', 'Cancelled'


class EstablishmentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=150, blank=True, null=True)
    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )
    business_permit_number = models.CharField(max_length=300, blank=True, null=True)
    contact_phone = models.CharField(max_length=20, default='', blank=True)
    primary_contact_person = models.CharField(max_length=50, default='', blank=True)
    verified_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"


class SafeHaven(models.Model):
    establishment = models.ForeignKey(
        EstablishmentProfile, 
        on_delete=models.CASCADE, 
        related_name='safe_havens'
    )
    name = models.CharField(max_length=255)
    barangay = models.CharField(max_length=100, default='', blank=True)
    city = models.CharField(max_length=100, default='', blank=True)
    province = models.CharField(max_length=100, default='', blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=8, default=0.0)
    longitude = models.DecimalField(max_digits=11, decimal_places=8, default=0.0)
    operating_hours = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    safe_phrase = models.CharField(max_length=255, default='', blank=True)
    special_instructions = models.TextField(blank=True, null=True)
    people_helped = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.barangay}, {self.city})"

    @property
    def address(self):
        parts = [p for p in [self.barangay, self.city, self.province] if p]
        return ", ".join(parts) if parts else "Location on file"

    @property
    def operating_hours_display(self):
        if isinstance(self.operating_hours, dict) and self.operating_hours:
            if 'summary' in self.operating_hours:
                return str(self.operating_hours['summary'])
            # If standard days exist, build readable string
            return ", ".join(f"{k}: {v}" for k, v in self.operating_hours.items())
        elif isinstance(self.operating_hours, str) and self.operating_hours.strip():
            return self.operating_hours
        return "Open 24/7"

    @property
    def contact_phone(self):
        if self.establishment and self.establishment.contact_phone:
            return self.establishment.contact_phone
        return "0917-000-0000"

    @property
    def organization_name(self):
        if self.establishment and self.establishment.organization_name:
            return self.establishment.organization_name
        elif self.establishment and self.establishment.user:
            user = self.establishment.user
            full = f"{user.first_name} {user.last_name}".strip()
            return f"{full or user.username} Safe Sanctuary"
        return self.name

    def assign_coordinates_if_missing(self):
        """
        Ensures every registered safe haven has valid, plottable coordinates
        for map rendering, inferring from barangay/city or assigning a localized coordinate.
        """
        lat_val = float(self.latitude) if self.latitude is not None else 0.0
        lon_val = float(self.longitude) if self.longitude is not None else 0.0

        if lat_val == 0.0 and lon_val == 0.0:
            from decimal import Decimal
            loc = f"{self.barangay} {self.city} {self.province}".lower()
            if 'guadalupe' in loc:
                self.latitude = Decimal('10.3235')
                self.longitude = Decimal('123.8821')
            elif 'lahug' in loc:
                self.latitude = Decimal('10.3340')
                self.longitude = Decimal('123.8995')
            elif 'mabolo' in loc:
                self.latitude = Decimal('10.3220')
                self.longitude = Decimal('123.9140')
            elif 'banilad' in loc:
                self.latitude = Decimal('10.3450')
                self.longitude = Decimal('123.9110')
            elif 'capitol' in loc:
                self.latitude = Decimal('10.3175')
                self.longitude = Decimal('123.8920')
            elif 'talamban' in loc:
                self.latitude = Decimal('10.3650')
                self.longitude = Decimal('123.9150')
            elif 'mandaue' in loc:
                self.latitude = Decimal('10.3350')
                self.longitude = Decimal('123.9350')
            elif 'lapu' in loc or 'mactan' in loc:
                self.latitude = Decimal('10.3120')
                self.longitude = Decimal('123.9500')
            elif 'manila' in loc:
                self.latitude = Decimal('14.5995')
                self.longitude = Decimal('120.9842')
            else:
                hash_val = sum(ord(c) for c in (self.name or 'Haven'))
                jitter_lat = ((hash_val % 13) - 6) * 0.0025
                jitter_lon = (((hash_val // 13) % 13) - 6) * 0.0025
                self.latitude = Decimal(str(round(10.3280 + jitter_lat, 6)))
                self.longitude = Decimal(str(round(123.8920 + jitter_lon, 6)))

    def save(self, *args, **kwargs):
        self.assign_coordinates_if_missing()
        super().save(*args, **kwargs)


# Protocol Checklist connected to EstablishmentProfile
class ProtocolChecklist(models.Model):
    establishment = models.ForeignKey(
        EstablishmentProfile,
        on_delete=models.CASCADE,
        related_name='protocols'
    )
    title = models.CharField(max_length=150)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.title} - {self.establishment.user.username}"


class EmergencyAlert(models.Model):
    safe_haven = models.ForeignKey(
        SafeHaven, 
        on_delete=models.CASCADE, 
        related_name='emergency_alerts'
    )
    session_token = models.CharField(max_length=255, default='', blank=True)
    status = models.CharField(
        max_length=20,
        choices=AlertStatus.choices,
        default=AlertStatus.RECEIVED,
    )
    time_stamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Alert {self.id} - {self.status} at {self.safe_haven.name}"
    