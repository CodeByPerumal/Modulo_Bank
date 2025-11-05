from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "id", "sender", "receiver", "amount",
        "status", "transaction_type", "timestamp"
    )
    list_filter = ("status", "transaction_type", "timestamp")
    search_fields = ("sender__account_number", "receiver__account_number")
    readonly_fields = ("id", "timestamp")
