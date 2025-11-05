from django.contrib import admin
from .models import Account

@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ("user", "account_number", "account_type", "balance", "created_at")
    search_fields = ("account_number", "user__username")
    list_filter = ("account_type", "created_at")
    readonly_fields = ("account_number", "created_at")
