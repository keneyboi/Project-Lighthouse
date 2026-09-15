from django.db import models
from django.contrib.auth.models import User

class EstablishmentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_name = models.CharField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} Profile"

class SafeHaven(models.Model):
    establishment = models.ForeignKey(
        EstablishmentProfile, 
        on_delete=models.CASCADE, 
        related_name='safe_havens'
    )
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    safe_phrase = models.CharField(max_length=100, default='I need a lighthouse')
    is_active = models.BooleanField(default=True)
    special_instructions = models.TextField(blank=True, null=True)
    people_helped = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.name} ({self.establishment.user.username})"

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