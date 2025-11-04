# from django.db import models
# from django.contrib.auth import get_user_model
# import uuid

# User = get_user_model()

# class Notification(models.Model):
#     """
#     Stores system notifications for users.
#     """

#     NOTIFICATION_TYPES = [
#     ("loan", "Loan"),
#     ("transaction", "Transaction"),
#     ("security", "Security"),
#     ("general", "General"),
#     ]
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
#     title = models.CharField(max_length=255)
#     message = models.TextField()
#     notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default="general")
#     is_read = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at']

#     # def __str__(self):
#     #     return f"Notification for {self.user.username}: {self.message[:50]}"

#     def __str__(self):
#         return f"{self.title} for {self.user.username}"


from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class Notification(models.Model):
    """
    Stores system notifications for users.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=100, default="System Notification")  # <-- Added default
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} for {self.user.username}: {self.message[:50]}"

