from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.utils import timezone
from django.core.files import File
from io import BytesIO
import qrcode
from django.conf import settings
from django.urls import reverse

class User(AbstractUser):
    phone_number = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.phone_number}"


class Vehicle(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    plate_number = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    make_model = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    qr_token = models.ImageField(upload_to='qr_codes/', blank=True, null=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Use the correct view name
        qr_url = reverse('scan_qr', args=[str(self.pk)])  # or 'contact_owner' with mode if needed
        full_url = f"{settings.SITE_DOMAIN}{qr_url}"

        # Generate QR code
        qr_img = qrcode.make(full_url)
        buffer = BytesIO()
        qr_img.save(buffer, format='PNG')
        filename = f"vehicle_qr_{self.pk}.png"

        self.qr_token.save(filename, File(buffer), save=False)
        super().save(update_fields=['qr_token'])

class Guardian(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='guardians')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50)
    is_primary = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.relationship})"


class ContactLog(models.Model):
    CONTACT_TYPE_CHOICES = [
        ('call', 'Call'),
        ('message', 'Message'),
        ('emergency', 'Emergency'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('delivered', 'Delivered'),
        ('failed', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='contact_logs')
    contact_type = models.CharField(max_length=20, choices=CONTACT_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    initiator_ip = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.contact_type} → {self.vehicle.plate_number} ({self.status})"
