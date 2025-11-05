from django.contrib import admin
from .models import FraudAlert

@admin.register(FraudAlert)
class FraudAlertAdmin(admin.ModelAdmin):
    list_display = ("id", "transaction", "reason", "flagged_at", "reviewed")
    list_filter = ("reviewed", "flagged_at")
    search_fields = ("transaction__id", "reason")
    readonly_fields = ("id", "transaction", "reason", "flagged_at")
