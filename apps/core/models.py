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
    