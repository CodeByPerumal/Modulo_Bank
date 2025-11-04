from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class AuditLog(models.Model):
    """
    Stores system audit events — used by auditors to review key activities.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True) 
    method = models.CharField(max_length=10, blank=True, null=True)
    # endpoint = models.CharField(max_length=255)
    endpoint = models.CharField(max_length=255, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} - {self.action} at {self.created_at}"
