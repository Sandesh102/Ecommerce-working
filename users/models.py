from django.db import models
import uuid
import threading
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.forms.models import model_to_dict
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    email = models.EmailField(blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    google_id = models.CharField(max_length=255, blank=True, null=True, unique=True)
    # Admin identification fields (for admin pass / badge)
    admin_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, null=True, blank=True)
    badge_qr_image = models.ImageField(upload_to='admin_badges/', blank=True, null=True)
    badge_issued_at = models.DateTimeField(blank=True, null=True)
    badge_expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.user.username
 